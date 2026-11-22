"""
登录认证中间件
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class AuthMiddleware(MiddlewareMixin):
    """统一登录校验，未登录访问受保护页面自动跳转登录页"""

    # 不需要登录就能访问的路径
    WHITE_LIST = ["/login/", "/image/code/"]

    def process_request(self, request):
        # 白名单路径直接放行
        if request.path_info in self.WHITE_LIST:
            return None

        # 从session读取用户信息，能读到说明已登录
        user_id = request.session.get("user_id")
        if user_id:
            return None

        # 未登录，跳转登录页
        return redirect("/login/")
