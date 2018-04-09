# coding=utf-8
from django.shortcuts import render
from models import *
# 分页的模块
from django.core.paginator import Paginator
from haystack.generic_views import SearchView

# 首页
def index(request):
    # 创建一个列表
    goods_list = []# 列表要包含多个结构 [{},{},{}] =====>{'typeinfo':'new_list','click_list':}
    # 查询分类对象
    # 查询每个分类中最新的4个商品
    # 查询每个分类中最火的4个商品
    # 查询数据模型中的所有商品
    type_list = TypeInfo.objects.all()
    for t1 in type_list:
        # 分类商品中降序排列，取前四个
        nlist = t1.goodsinfo_set.order_by('-id')[0:4]
        # 查询商品点击量最高的四个
        clist = t1.goodsinfo_set.order_by('-gclick')[0:4]
        goods_list.append({'t1': t1, 'nlist': nlist, 'clist': clist})

    context = {'title': '首页', 'glist': goods_list, 'cart_show': '1'}
    return render(request,'ttsx_goods/index.html', context)


# 商品列表
def goods_list(request, tid, pindex, orderby):
    # get方法当查询不到的时候会报异常，所以这里try一下
    try:
        t1 = TypeInfo.objects.get(pk=int(tid))
        new_list = t1.goodsinfo_set.order_by('-id')[0:2]
        # 指定排序规则
        orderby_str = '-id' # 默认排序：是id降序排列
        desc = '1'
        if orderby == '2': # 跟据价格排序
            # 指定排序规则，升还是降
            desc = request.GET.get('desc', '1')
            if desc == '1':
                orderby_str = '-gprice'
                # desc = '0'
            else:
                orderby_str = 'gprice'
                # desc = '1'
        elif orderby == '3': # 跟据人气排序
            orderby_str = '-gclick'

        # 查询：当前分类的所有商品，按每页15个来显示
        glist = t1.goodsinfo_set.order_by(orderby_str)
        # 一页显示商品的条数
        paginator = Paginator(glist, 10)
        # 对页码进行验证，防止用户非法输入
        pindex1 = int(pindex)
        if pindex1 < 1:
            pindex1 = 1
        elif pindex1 > paginator.num_pages:
            pindex1 = paginator.num_pages
        page = paginator.page(pindex1)
        context = {'title': '商品列表页', 'cart_show':'1', 't1': t1, 'new_list':new_list, 'page':page,'orderby':orderby, 'desc':desc}
        return render(request, 'ttsx_goods/list.html', context)

    except:
        return render(request,'404.html')


def detail(request, id):
    try:
        # objects是django提供给我们的模型类管理器，模型类来调用，是类成员，不是对象成员，
        # 用TypeInfo，和GoodsInfo,都可以调用
        goods = GoodsInfo.objects.get(pk=int(id))
        # 商品浏览量 只要看了就加1
        goods.gclick += 1
        # 对浏览量进行保存
        goods.save()
        # 查询商品当前分类中最新的两个商品
        new_list = goods.gtype.goodsinfo_set.order_by('-id')[0:2]
        # GoodInfo.objects
        # 通过书（一）中找英雄，就得通过英雄的
        # book-->book.heroinfo_set.***
        # 英雄（多）找书，直接找hero中的模型属性就可以了
        # hero-->hero.hbook
        context = {'title': '商品详细页', 'cart_show':'1','goods': goods, 'new_list': new_list}
        response = render(request, 'ttsx_goods/detail.html', context)
        # 将浏览的商品存储到浏览器中的cookie中 (存储的名字，存储的东西，过期时间)
        # 保存最近浏览[1,2,3,4,5]<==>'1,2,3,4,5'   ','.join()   .split()
        # 步骤：先读取已存的》进行拼接》输出

        gids = request.COOKIES.get('goods_ids', '').split(',')
        # 判断这个编号是否存在，如果存在，删除，然后再加到最前边
        if id in gids:
            gids.remove(id)
        # 最新浏览的商品拼接到最前边
        gids.insert(0, id)
        # 如果超过5个，则删除最后一个
        if len(gids)> 6:
            gids.pop()
        response.set_cookie('goods_ids', ','.join(gids), max_age=60*60*24*7)
        return response

    except:
        return render(request, '404.html')


# 官方提供的方法，获取到全文检索的视图
class MySearchView(SearchView):
    def get_context_data(self, *args, **kwargs):
        context = super(MySearchView, self).get_context_data(*args, **kwargs)
        # do something
        context['cart_show']='1'
        page_range = []
        page = context.get('page_obj')
        if page.paginator.num_pages<5:# 当页码小于5页的时候
            page_range = page.paginator.page_range
        elif page.number <= 2: # 当为第一第二页
            page_range = range(1, 6)
        elif page.number >= page.paginator.num_pages-1:
            page_range = range(page.paginator.num_pages-4, page.paginator.num_pages+1)
        else:
            page_range = range(page.number-2, page.number+3)
        context['page_range'] = page_range
        context['title'] = '搜索'
        return context




'''
计算数量使用js来计算，这样直接就可以显示在页面上
商品还需要做的功能
列表页：排序，页码控制
最近浏览
全文检索



购物车：模型类，视图，模板，列表页购买，详细页购买（登录的用户才能购买，没等路的要跳转到登录页）
要显示添加的所有商品，计算数量，计算总价钱，点击结算，跳转到订单页
订单页：1.模型类2.购买3.事务处理
1.显示收获地址，显示选中的商品，点击提交订单要做几个处理：1.判断库存够不够，够的话，减掉买入的商品数量，
2.创建订单，在订单详表中去添加每一个购物车中的商品，再将购物车中的商品删除3.要使用事务，操作一步错误，就放弃
4.回滚
'''


























