import bisect

from django.db import models
from django.contrib.auth.models import User
import random
from django.db import transaction
import numpy as np
from django.db.models import F

# Create your models here.

pic_dic = {0: '/static/image/profile0.png', 1: '/static/image/profile1.png', 2: '/static/image/profile2.png',
           3: '/static/image/profile3.png', 4: '/static/image/profile5.png', 5: '/static/image/profile5.png'}

ERR_INCARD = 9999
ERR_NOTINCOL = 1
ERR_EXCHANGE = 2
ERR_MARKED = 4
ERR_BOUNDARY = 8
# the model definiation for Profile model
# yirun

class GameEntry(models.Model):
    player = models.ManyToManyField(User)
    # gameCard = models.CharField(default="",max_length=10000)
    # THE GAME ITSELF SHOULD ONLY CONTAIN THE SEQUENCE
    gameSequence = models.CharField(default="", max_length=5000)
    dimension = models.IntegerField(default=5)
    mode = models.CharField(default="Dumb", max_length=500)
    player_cap = models.IntegerField(default=4)
    random_token = models.IntegerField(default=0)
    gameStatus = models.BooleanField(default=False)
    winner = models.ForeignKey(User, null=True, on_delete=models.PROTECT,related_name="winner")
    closest_num_to_bingo = models.IntegerField(default = -1)
    flipped_most_user  =  models.ForeignKey(User,null = True, on_delete= models.PROTECT,related_name="flipped_most_user")
    flipped_most_num = models.IntegerField(default = 0)


    @classmethod
    def get_game_current_num(cls, game_id, iterPassed) -> int:
        return int(cls.objects.get(id=game_id).gameSequence.split(" ")[iterPassed])

    @classmethod
    def get_game_dim(cls, game_id) -> int:
        return cls.objects.get(id=game_id).dimension

    @classmethod
    def get_status(cls, game_id) -> bool:
        return cls.objects.get(id=game_id).gameStatus

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    allow_to_create_new_game = models.BooleanField(default = True)
    most_up_to_date_game = models.ForeignKey(GameEntry, null = True, on_delete = models.PROTECT)

    picture = models.FileField(blank=True,
                               default=pic_dic.get(random.randint(0, 5)))   
    account_balance = models.IntegerField(default=200)
    won_times = models.IntegerField(default=0)
    lost_times = models.IntegerField(default=0)
    item_1_count = models.IntegerField(default = 0)
    item_2_count  = models.IntegerField(default = 0)
    pic_by_default = models.IntegerField(default=1)

    def __str__(self):
        return 'id=' + str(self.id) + ',user="' + self.user.username + ""

    @classmethod
    def get_user_game_id(cls, user) -> int:
        return cls.objects.get(user=user).most_up_to_date_game.id

    @classmethod
    def get_user_balance(cls, user) -> int:
        return cls.objects.get(user=user).account_balance

    @classmethod
    def update_user_balance(cls, user, delta) -> None:
        p = cls.objects.get(user=user)
        p.account_balance = F('account_balance') + delta
        p.save()
        
def reshape_matrix(flat_matrix):
    n = int(len(flat_matrix) ** 0.5)  # get the size of the square matrix
    return [flat_matrix[i * n: (i + 1) * n] for i in range(n)]


def transpose_matrix(matrix):
    return list(map(list, zip(*matrix)))


def flatten_matrix(matrix):
    return [element for row in matrix for element in row]


class playerGameInstance(models.Model):

    player = models.ForeignKey(User, default = None, on_delete=models.PROTECT)
    game_belonging_to = models.ForeignKey(GameEntry, default = None, on_delete= models.PROTECT)
    #keep track of the user's game card PUT IT HERE INSTEAD OF GAME ENTRY CONTAINING THE CARDS
    gameCard = models.CharField(default="",max_length=5000)
    #keeps track the state of the game
    gameState = models.CharField(default="", max_length=5000)
    iterPassed = models.IntegerField(default = -1)
    filled_in_num = models.IntegerField(default = 0)

    def __str__(self):
        return 'id=' + str(self.id) + ',gameCard="' + self.gameCard + ""

    @classmethod
    def get_game_user_iter(cls, game_id, user_id) -> int:
        return cls.objects.get(game_belonging_to=game_id, player=user_id).iterPassed

    @classmethod
    def in_game_user(cls, game_id, user_id, curr_num: int) -> bool:
        #card = list(map(int, cls.objects.get(game_belonging_to=game_id, player=user_id).gameCard.split(" ")))
        #if curr_num not in card:
        #    return False
        #state = cls.objects.get(game_belonging_to=game_id, player=user_id).gameState.split(" ")
        #return state[card.index[curr_num]] == 'T'
        return curr_num in set(map(int, cls.objects.get(game_belonging_to=game_id, player=user_id).gameCard.split(" ")))

    @classmethod
    def swap(cls, game, usera, itema, userb, itemb, colora=False) -> bool:
        try:
            with transaction.atomic():
                usera_card = cls.objects.get(game_belonging_to=game, player=usera).gameCard
                usera_state = cls.objects.get(game_belonging_to=game, player=usera).gameState
                userb_card = cls.objects.get(game_belonging_to=game, player=userb).gameCard
                userb_state = cls.objects.get(game_belonging_to=game, player=userb).gameState
                usera_card = \
                flatten_matrix(
                    transpose_matrix(
                        reshape_matrix(list(map(int, usera_card.split(" "))))))
                usera_state = \
                    flatten_matrix(
                        transpose_matrix(
                            reshape_matrix(
                                usera_state.split(" "))))
                userb_card = \
                flatten_matrix(
                    transpose_matrix(
                        reshape_matrix(list(map(int, userb_card.split(" "))))))
                userb_state = \
                    flatten_matrix(
                        transpose_matrix(
                            reshape_matrix(
                                userb_state.split(" "))))
                if itema not in usera_card or itemb not in userb_card:
                    return False
                idxa = usera_card.index(itema)
                idxb = userb_card.index(itemb)
                userb_card[idxb] = itema
                usera_card[idxa] = itemb
                userb_state[idxb], usera_state[idxa] = usera_state[idxa], userb_state[idxb]
                if colora:
                    usera_state[idxa] = 'T'
                ranka = np.argsort(usera_card)
                rankb = np.argsort(userb_card)
                usera_card = [usera_card[i] for i in ranka]
                userb_card = [userb_card[i] for i in rankb]
                usera_state = [usera_state[i] for i in ranka]
                userb_state = [userb_state[i] for i in rankb]
                usera_card = " ".join(flatten_matrix(transpose_matrix(reshape_matrix(list(map(str, usera_card))))))
                userb_card = " ".join(flatten_matrix(transpose_matrix(reshape_matrix(list(map(str, userb_card))))))
                carda = cls.objects.select_for_update().get(game_belonging_to=game, player=usera)
                carda.gameCard = usera_card
                carda.gameState = " ".join(flatten_matrix(transpose_matrix(reshape_matrix(usera_state))))
                cardb = cls.objects.select_for_update().get(game_belonging_to=game, player=userb)
                cardb.gameCard = userb_card
                cardb.gameState = " ".join(flatten_matrix(transpose_matrix(reshape_matrix(userb_state))))
                carda.save()
                cardb.save()
            return True
        except Exception as e:
            print("[fatal] swap", e)
            return False

    @classmethod
    def get_exchange_candidate_all(cls, game_id, user_id):
        user_card = cls.objects.get(game_belonging_to=game_id, player=user_id).gameCard
        return set(map(int, user_card.split(" ")))
    @classmethod
    def get_exchange_candidate(cls, game_id, user_id, auction_item, targets=()) -> int:
        user_card = cls.objects.get(game_belonging_to=game_id, player=user_id).gameCard
        game_state = cls.objects.get(game_belonging_to=game_id, player=user_id).gameState
        game_state = \
            flatten_matrix(
                transpose_matrix(
                    reshape_matrix(game_state.split(" "))))
        user_card = \
            flatten_matrix(
                transpose_matrix(
                    reshape_matrix(
                        list(map(int, user_card.split(" "))))))
        idx = bisect.bisect_left(user_card, auction_item)
        if auction_item in user_card:
            return -ERR_INCARD
        if idx == len(user_card):
            if game_state[-1] == 'T':
                return -(ERR_BOUNDARY | ERR_MARKED)
            if user_card[-1] in targets:
                return -(ERR_BOUNDARY | ERR_EXCHANGE)
            return user_card[-1]
        if idx - 1 < 0:
            if game_state[0] == 'T':
                return -(ERR_BOUNDARY | ERR_MARKED)
            if user_card[0] in targets:
                return -(ERR_BOUNDARY | ERR_EXCHANGE)
            return user_card[0]
        auction_col = auction_item // (3 * GameEntry.get_game_dim(game_id))
        samller_col = user_card[idx - 1] // (3 * GameEntry.get_game_dim(game_id))
        larger_col = user_card[idx] // (3 * GameEntry.get_game_dim(game_id))
        errrocode = 0
        if game_state[idx - 1] == 'F':
            if samller_col == auction_col:
                if user_card[idx - 1] not in targets:
                    return user_card[idx - 1]
                else:
                    errrocode |= ERR_EXCHANGE
            else:
                errrocode |= ERR_NOTINCOL
        else:
            errrocode |= ERR_MARKED
        errrocode = errrocode << 4
        if game_state[idx] == 'F':
            if larger_col == auction_col:
                if user_card[idx] not in targets:
                    return user_card[idx]
                else:
                    errrocode |= ERR_EXCHANGE
            else:
                errrocode |= ERR_NOTINCOL
        else:
            errrocode |= ERR_MARKED
        return -errrocode


# used for building scoreboard, among many people/ one person.

class ScoreEntry(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    date_happened = models.DateTimeField()
    score = models.FloatField()

    def __str__(self):
        return 'id=' + str(self.id) + ',user="' + self.user + ""


# used for user to check the money spent
class BettingEntry(models.Model):
    user_sending = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    user_receiving = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name="user_receiving")
    date = models.DateTimeField()
    money_spent = models.FloatField()
