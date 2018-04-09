# coding=utf-8
class UrlMiddleWare:
    def process_view(self, request,view_name,view_args,view_kwargs):
        # print '-----------------------%s' %request.path
        if request.path not in ['/user/register/',
                                '/user/register_handle/',
                                '/user/register_valid/',
                                '/user/login/',
                                '/user/login_handle/',
                                '/user/logout/',
                                '/user/islogin/',]:

            request.session['url_path'] = request.get_full_path()

'''
process_request
process_view
'''


'''
每次请求响应的时候，都执行中间件，但是我们在这里边排除了，所以没记录路径，但是是执行的
http://www.itcast.cn/python/?a=100
get_full_path()-->/python/?a=100    get_full_path 还带了参数
path-->/python/                     path只要路径
'''