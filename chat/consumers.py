from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from chat.models import ChatHistory
import json
from threading import Lock

lock = Lock()
active_connections = 0


class MyConsumer(WebsocketConsumer):
    group_name = 'chat_group'
    channel_name = 'chat_channel'
    user = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        # @fixme: uncomment this
        # if not self.scope["user"].is_authenticated:
        #     self.send_error(f'You must be logged in')
        #     self.close()
        #     return

        self.user = self.scope["user"]
        with lock:
            global active_connections
            active_connections += 1
            message = '{} active connections'.format(active_connections)
        self.broadcast_message(message)
        self.broadcast_list()

    def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except:
            self.send_error('invalid JSON sent to server')
            return
        if not 'action' in data:
            self.send_error('action property not sent in JSON')
            return
        action = data['action']

        if action == 'add':
            self.handle_new(data)
            return

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

        with lock:
            global active_connections
            active_connections -= 1
            message = '{} active connections'.format(active_connections)
        self.broadcast_message(message)

    def handle_new(self, data):
        if not 'text' in data:
            self.send_error('text property not sent in JSON')
            return
        # if not 'roomid' in data:
        #     self.send_error('roomid property not sent in JSON')
        #     return
        text = data['text']
        # roomid = data['roomid']
        ChatHistory.objects.create(text=text, user=self.user, roomid=0).save()
        self.broadcast_list()

    def broadcast_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps({'message': message})
            }
        )

    def broadcast_list(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(ChatHistory.make_chat_history_list())
            }
        )

    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])