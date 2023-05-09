from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.db.models.signals import pre_save

# Create your models here.
class Auction(models.Model):
    active = models.BooleanField(default=True)
    bid_price = models.IntegerField(default=0)
    open_price = models.IntegerField(default=0)
    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name='seller2user')
    buyer = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name='buyer2user', null=True)
    item = models.IntegerField(default=-1)
    exchange_out = models.IntegerField(default=-1)
    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             check=Q(bid_price__gt=F('old_bid_price')) & Q(active=True),
    #             name='check_field_bid_price'
    #         )
    #     ]

    # def save(self, *args, **kwargs):
    #     self.old_bid_price = getattr(self, 'bid_price', None)
    #     super(Auction, self).save(*args, **kwargs)

    @classmethod
    def make_auction_record(cls, auction_id):
        item = cls.objects.get(id=auction_id)
        fields = item._meta.get_fields()
        item_dict = {
            field.name: str(getattr(item, field.name))
            for field in fields
            if hasattr(item, field.name)
        }
        item_dict['seller'] = item.seller.username
        item_dict['buyer'] = item.buyer.username if item.buyer else None
        return item_dict

# def set_old_bid_price(sender, instance, **kwargs):
#     if instance.pk:
#         old_bid_price = Auction.objects.get(pk=instance.pk).bid_price
#         instance.old_bid_price = old_bid_price
#
# pre_save.connect(set_old_bid_price, sender=Auction)