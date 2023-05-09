from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from auction.models import Auction
from bingo_plus.models import playerGameInstance, GameEntry, Profile
from django.contrib.auth.models import User
from threading import Lock, Thread
import json
from django.db import transaction
import time
from typing import *
from urllib.parse import parse_qsl

lock = Lock()
open_lock = Lock()
active_connections = 0
COUNTDOWN = 20
uid2channel = dict()
state_tracker = dict()  # global variable, k:game_id, v:aid


class AuctionConsumer(WebsocketConsumer):
    group_name = 'auction_group'

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.game_id = None
        self.user = None
        self.group_name = None
        self.query_string = None

    def connect(self):
        self.user = self.scope["user"]
        self.game_id = Profile.get_user_game_id(self.user)

        self.group_name = 'auction_group_{}'.format(self.game_id)
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        # @fixme: bypass user at testing, uncomment this

        with lock:
            global active_connections
            active_connections += 1
            message = '{} active connections'.format(active_connections)
        self.__broadcast_message(message)
        global state_tracker
        state_tracker[self.game_id] = None
        print('connected', self.channel_name, self.group_name, self.game_id, self.user)
        self.__send_balance()

    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            # @fixme: remove test only
        except:
            self.__send_error('invalid JSON sent to server')
            return
        if not 'action' in data:
            self.__send_error('action property not sent in JSON')
            return

        self.__handle_new(data)
    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

        with lock:
            global active_connections
            active_connections -= 1
            message = '{} active connections'.format(active_connections)
        self.__broadcast_message(message)

    def __send_balance(self):
        self.send(text_data=json.dumps({
            'type': 'display_balance',
            'body': Profile.get_user_balance(self.user)
        }))

    def __broadcast_balance(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {'type': 'display_balance'}
        )

    def display_balance(self, event):
        self.send(text_data=json.dumps({
            'type': 'display_balance',
            'body': Profile.get_user_balance(self.user)
        }))
    def __broadcast_record(self, auction_id: int):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'auction_record',
                'body': Auction.make_auction_record(auction_id),
            }
        )

    def auction_record(self, event):
        self.send(text_data=json.dumps(event))

    def __broadcast_message(self, message: str):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'display_message',
                'body': message,
            }
        )

    def display_message(self, event):
        self.send(text_data=json.dumps(event))

    def __broadcast_timer(self, timer: int):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_timer',
                'body': timer,
            }
        )

    def broadcast_timer(self, event):
        self.send(text_data=json.dumps(event))

    def __broadcast_control(self, params: Dict[str, Any], myself=True):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'control' if myself else 'control_others',
                'body': params,
                'sender': self.channel_name,
            }
        )

    def control(self, event):
        self.send(text_data=json.dumps(event))

    def control_others(self, event):
        sender = event["sender"]
        if self.channel_name != sender:
            self.send(text_data=json.dumps(event))

    def __send_error(self, error_message):
        self.send(text_data=json.dumps({'type': 'error', 'body': error_message}))

    def __handle_new(self, data):
        try:
            global state_tracker
            if data['action'] == 'bid':
                if 'bid_price' not in data or not data['bid_price']:
                    self.__send_error('bid_price not sent in JSON')
                    return
                auction_record = Auction.objects.get(id=state_tracker[self.game_id])
                auction_item = auction_record.item
                targets = playerGameInstance.get_exchange_candidate_all(self.game_id, auction_record.seller.id)
                exchagne_out = playerGameInstance.get_exchange_candidate(self.game_id, self.user.id, auction_item,
                                                                         targets)
                if exchagne_out < 0:
                    if exchagne_out == -9999:
                        self.__send_error(f'no available item to exchange {auction_item} at game {self.game_id} '
                                          f'auction {state_tracker[self.game_id]}: you already have this item')
                    else:
                        self.__send_error(f'no available item to exchange {auction_item} at game {self.game_id} '
                                          f'auction {state_tracker[self.game_id]}: '
                                          f'seller have colored the number you want to exchange')
                    return
                user_balance = Profile.get_user_balance(self.user)
                if user_balance < int(data['bid_price']):
                    self.__send_error(f'not enough balance {user_balance} to bid {data["bid_price"]} at game {self.game_id} '
                                      f'auction {state_tracker[self.game_id]}')
                    return
                with transaction.atomic():
                    # @fixme: add mutex?
                    bid_price = int(data['bid_price'])
                    auction = Auction.objects.select_for_update().get(id=state_tracker[self.game_id])
                    if auction.active and auction.bid_price < bid_price:
                        auction.bid_price = bid_price
                        auction.buyer = self.user
                        auction.exchange_out = exchagne_out
                        auction.save()
                    else:
                        self.__send_error(f'auction {state_tracker[self.game_id]} for game {self.game_id} '
                                          f'not active or bid price too low')
                        return
                self.__broadcast_record(state_tracker[self.game_id])
                self.__send_balance()

            if data['action'] == 'new':
                if 'bid_price' not in data or not data['bid_price']:
                    self.__send_error('bid_price not set')
                    return
                if not data['bid_price'].isdigit():
                    self.__send_error('bid_price must be integer')
                    return
                if int(data['bid_price']) <= 0:
                    self.__send_error('bid_price must be positive')
                    return
                if GameEntry.get_status(self.game_id):
                    self.__send_error(f'game {self.game_id} already ended')
                    return
                with open_lock:
                    if self.game_id in state_tracker and \
                            state_tracker[self.game_id] and \
                            Auction.objects.get(id=state_tracker[self.game_id]).active:
                        self.__send_error(f'auction {state_tracker[self.game_id]} '
                                          f'for game {self.game_id} active, cannot start new auction')
                        return
                    iter = playerGameInstance.get_game_user_iter(self.game_id, self.user.id)
                    curr_num = GameEntry.get_game_current_num(self.game_id, iter)
                    print('new auction: iter={}, num={}, userid={}'.format(iter, curr_num, self.user.id))
                    if not playerGameInstance.in_game_user(self.game_id, self.user.id, curr_num):
                        self.__send_error(f'Auction must be held on current number, '
                                          f'expected iter={iter}, num={curr_num}, userid={self.user.id}')
                        return
                # with open_lock:  # synchronized method
                    # call by main game page, seller
                    auction = Auction.objects.create(
                        seller=self.user,
                        bid_price=data['bid_price'],
                        open_price=data['bid_price'],
                        active=True,
                        item=curr_num,
                    )
                    auction.save()
                    self.__broadcast_control(
                        {'action': 'start', 'aid': auction.id})  # , 'search_params': data['search_params']})
                    self.send(
                        text_data=json.dumps({'type': 'control', 'body': {'action': 'accept', 'aid': auction.id}}))
                    state_tracker[self.game_id] = auction.id
                    self.__broadcast_record(auction.id)
                    print('starting new auction thread: iter={}, num={}, userid={}...'.format(iter, curr_num, self.user.id))
                    Thread(target=self.run_timer, args=(auction.id,)).start()
        except Exception as e:
            print('error', e)
            self.__send_error(str(e))
            return

        if data['action'] == 'close':
            auction = Auction.objects.get(id=state_tracker[self.game_id])
            auction.active = False
            auction.save()
            self.__broadcast_record(auction.id)

    def finalize_auction(self, aid) -> str:
        record = Auction.objects.get(id=aid)
        if not record.buyer or record.exchange_out < 0:
            return 'no buyer'
        buyer = record.buyer
        seller = record.seller
        if playerGameInstance.swap(self.game_id, usera=buyer, userb=seller, itema=record.exchange_out,
                                   itemb=record.item, colora=True):
            Profile.update_user_balance(buyer, -record.bid_price)
            Profile.update_user_balance(seller, record.bid_price)
            return 'success, buyer: {}, seller: {}'.format(buyer.first_name + ' ' + buyer.last_name,
                                                           seller.first_name + ' ' + seller.last_name)
        else:
            return 'fail, buyer: {}, seller: {}'.format(buyer.first_name + ' ' + buyer.last_name,
                                                        seller.first_name + ' ' + seller.last_name)

    def run_timer(self, aid: int):
        timer = COUNTDOWN
        while True:
            time.sleep(1)
            timer -= 1
            self.__broadcast_timer(timer)
            if timer == 0:
                break
        auction = Auction.objects.get(id=aid)
        auction.active = False
        auction.save()
        message = self.finalize_auction(aid)
        self.__broadcast_control({'action': 'end', 'message': message})
        self.__broadcast_record(aid)  # @fixme replace with correct result sending
        self.__broadcast_balance()
        return aid
