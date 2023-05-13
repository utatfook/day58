from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class M1(MiddlewareMixin):
    def process_request(self, request):
        # 获取当前用户请求的地址,如果是login就返回空
        if request.path_info in ['/login/','/code/img/']:
            return
        info = request.session.get('info')
        if info:
            return  # 有session就向后走，返回空就是向后走
        return redirect('/login/')
