# coding=utf-8
from django.shortcuts import render, redirect
from hashlib import sha1
from models import *
from django.http import JsonResponse
import datetime
from user_decorators import *
from ttsx_goods.models import GoodsInfo
from ttsx_order.models import OrderMain,OrderDetail
from django.core.paginator import Paginator
# 注册
def register(request):
    context={'title': '注册','top':'0'}
    return render(request, 'ttsx_user/register.html', context)


# 注册 数据处理
def register_handle(request):
    # 接收数据
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('user_pwd')
    umail = post.get('user_email')
    # 加密
    s1 = sha1()
    s1.update(upwd)
    upwd_sha1 = s1.hexdigest()

    # 创建对象 来接收用户输入的数据
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd_sha1
    user.umail = umail
    user.save()
    # 完成转向
    return redirect('user/login/')


# 注册 验证用户名是否存在
def register_valid(request):
    uname = request.GET.get('uname')
    # 查询
    result = UserInfo.objects.filter(uname=uname).count()
    context = {'valid': result}
    return JsonResponse(context)


# 登录
def login(request):
    # 给一个空字符串，这样当不记住用户名的时候才不会显示None
    uname = request.COOKIES.get('uname', '')
    context={'title': '登录', 'uname':uname, 'top':'0'}
    return render(request, 'ttsx_user/login.html', context)


# 登录 数据处理
def login_handle(request):
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('user_pwd')
    uname_jz = post.get('name_jz','0')
    # 加密
    s1 = sha1()
    s1.update(upwd)
    upwd_sha1 = s1.hexdigest()
    context = {'title': '登录', 'uname': uname, 'upwd': upwd, 'top':'0'}

    # 跟据用户名查询数据，如果未查到返回[]，如果查到了则返回[UserInfo]
    # 使用get方法抛异常，还不如用filter
    users = UserInfo.objects.filter(uname=uname)
    if len(users) == 0:
        # 用户名错误
        context['name_error'] = '1'
        return render(request, 'ttsx_user/login.html', context)
    else:
        if users[0].upwd == upwd_sha1:
            # 记录当前登录的用户
            request.session['uid'] = users[0].id
            request.session['uname'] = uname
            # 登录成功
            # 记住用户名
            # 在页面登录完成后，转回登录之前的页面,如果记录了，就赚回去，没记录就转到首页
            path = request.session.get('url_path', '/')
            # httpresponseredirect继承于httpresponse这个类
            response = redirect(path)
            # 记住用户名不是特别重要的隐私，所以直接保存到cookie中就可以了，当前登录的日期保存七天
            if uname_jz == '1':
                response.set_cookie('uname', uname, expires=datetime.datetime.now()+datetime.timedelta(days =7))
            else:
                # 设置-1立即删除
                response.set_cookie('uname', '', max_age=-1)
            return response
        else:
            # 密码错误
            context['pwd_error'] = '1'
            return render(request, 'ttsx_user/login.html', context)


def logout(request):
    request.session.flush()
    return redirect('/user/login/')


def islogin(request):
    result = 0
    if request.session.has_key('uid'):
        result = 1
    return JsonResponse({'islogin': result})


# 用户中心
# 用装饰器器来进行登录验证
@user_login
def center(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    # 查询最近浏览['23','53','123','']  ''空字符串转不成int
    gids = request.COOKIES.get('goods_ids', '').split(',')
    # 删除最后又一个空字符串
    gids.pop()
    # print gids
    # 跟据id去查询
    glist=[]
    for gid in gids:
        glist.append(GoodsInfo.objects.get(id=gid))
    context= {'title': '用户中心','user':user, 'glist':glist}
    return render(request,'ttsx_user/center.html', context)


# 全部订单
@user_login
def order(request):
    pindex = int(request.GET.get('pindex','1'))
    # 查询当前用户的所有订单,并进行分页
    uid = request.session.get('uid')
    order_list = OrderMain.objects.filter(user_id=uid)
    # 分页,一页放几个数据
    paginator = Paginator(order_list, 2)
    # 当前页码
    order_page = paginator.page(pindex)

    # 页码
    page_list = []
    if paginator.num_pages < 5:
        page_list = paginator.page_range
    elif order_page.number <= 2:
        page_list = (1, 6)
    elif order_page.number >= paginator.num_pages-1:
        page_list=range(paginator.num_pages-4, paginator.num_pages+1)
    else:
        page_list=range(pindex-2,pindex+3)
    context = {'title': '用户订单', 'order_page': order_page, 'page_list': page_list}
    return render(request, 'ttsx_user/order.html', context)


# 收获地址
@user_login
def site(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.ucode = post.get('ucode')
        user.uphone = post.get('uphone')
        user.save()
    context = {'title': '收货地址','user':user}
    return render(request, 'ttsx_user/site.html', context)


"""
在一个页面A中转到登录页，登录完成后转回A页
**** = request.path
1.如果这段代码写在视图中，维护的视图非常多
2.对于必须登录的页面，由于装饰器的影响，在未登录的时候，并不会执行
问题一的解决：让代码可以在每个视图中执行
问题二：在视图之前执行

中间件  每次请求响应之前都会被执行


"""




























