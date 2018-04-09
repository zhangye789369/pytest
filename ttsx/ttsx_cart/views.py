#coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse
from models import *
from django.db.models import Sum
from ttsx_user.user_decorators import user_login
from ttsx_user.models import UserInfo


# 添加商品
def add(request):
    # 获取数据
    try:
        uid = request.session.get('uid')
        gid = int(request.GET.get('gid'))
        count = int(request.GET.get('count', '1'))
        # 如果用filter来查询，就算没查到，返回一个空列表，get没查到就会抛异常
        carts = CartInfo.objects.filter(user_id=uid, goods_id=gid)
        if len(carts) == 1:
            cart = carts[0]
            cart.count+=count
            cart.save()
        else:
            cart = CartInfo()
            cart.user_id = uid
            cart.goods_id = gid
            cart.count = count
            cart.save()
        return JsonResponse({'isadd': 1})
    except:
        return JsonResponse({'isadd': 0})


# 修改数值
def count(request):
    # 先查询到用户id
    uid = request.session.get('uid')
    # 跟据用户id，拿到数量这个值,这个是商品的个数
    # cart_count = CartInfo.objects.filter(user_id = uid).count()
    # 下边的是求和的
    cart_count = CartInfo.objects.aggregate(Sum('count')).get('count__sum')
    return JsonResponse({'cart_count': cart_count})


# 点击加入购物车，进行验证登录，先判断是否登录
@user_login
def index(request):
    uid = request.session.get('uid')
    cart_list = CartInfo.objects.filter(user_id = uid)

    context={'title':'购物车','cart_list': cart_list}
    return render(request, 'ttsx_cart/cart.html', context)


# 保存数量
def edit(request):
    # 获取用户当前点击的id，数量count
    id = int(request.GET.get('id'))
    count = int(request.GET.get('count'))
    # 获取当前购物车对象，对应id来查找
    cart = CartInfo.objects.get(pk=id)
    # 将修改的购物车的数量保存到数据库中
    cart.count = count
    cart.save()
    # 保存成功，返回js数据
    return JsonResponse({'ok':1})


# 删除商品
def delete(request):
    # 得到点击删除位置的id
    id = int(request.GET.get('id'))
    cart = CartInfo.objects.get(pk=id)
    # 执行删除
    cart.delete()
    return JsonResponse({'ok': 1})


# 订单处理
def order(request):
    user = UserInfo.objects.get(pk=request.session.get('uid'))
    cart_ids = request.POST.getlist('cart_id')
    cart_list = CartInfo.objects.filter(id__in=cart_ids)
    c_ids = ','.join(cart_ids)#4,5,6
    context = {'title': '提交订单','user': user, 'cart_list': cart_list,'c_ids':c_ids}
    return render(request, 'ttsx_cart/order.html', context)