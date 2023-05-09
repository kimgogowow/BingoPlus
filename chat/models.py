from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatHistory(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    roomid = models.IntegerField()
    crtime = models.DateTimeField(auto_now_add=True)

    @classmethod
    def make_chat_history_list(cls, roomid=None):
        item_dict_list = []
        for item in cls.objects.filter(roomid=roomid) if roomid else cls.objects.all():
            item_dict = {
                'id': item.id,
                'text': item.text,
                'user': item.user.username,
                # 'crtime': item.crtime,
            }
            item_dict_list.append(item_dict)
        return item_dict_list