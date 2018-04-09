# coding=utf-8
from django.db import models
from ttsx_goods.models import GoodsInfo


class CartInfo(models.Model):
    # c谁买了个多少个什么
    user = models.ForeignKey('ttsx_user.UserInfo')
    goods = models.ForeignKey(GoodsInfo)
    count = models.IntegerField()