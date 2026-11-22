"""
认证相关视图：登录、注销、验证码
"""
from django.shortcuts import render, redirect
from django.http import HttpResponse
from app01.models import User
from app01.utils.captcha import captcha_image_stream

# 同一 session 连续登录失败上限，超过后需等待（防暴力破解）
MAX_FAIL_COUNT = 5
# 失败锁定时长（秒）
LOCK_SECONDS = 30


def image_code(request):
    """生成验证码图片"""
    image_bytes, code_str = captcha_image_stream()
    # 验证码存入session
    request.session["image_code"] = code_str
    return HttpResponse(image_bytes, content_type="image/png")


def login(request):
    """用户登录（含验证码校验与失败次数限制）"""
    if request.method == "GET":
        # 已登录直接进入首页
        if request.session.get("user_id"):
            return redirect("/depart/list/")
        return render(request, "app01/login.html")

    # POST：读取失败计数与锁定时间
    fail_count = request.session.get("login_fail_count", 0)
    locked_until = request.session.get("login_locked_until", 0)
    import time
    now = int(time.time())
    if locked_until and now < locked_until:
        remain = locked_until - now
        return render(request, "app01/login.html", {
            "error": f"失败次数过多，请 {remain} 秒后再试"
        })

    # 获取表单数据
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    input_code = request.POST.get("img_code", "")
    session_code = request.session.get("image_code", "")

    # 校验验证码（不区分大小写）
    if input_code.upper() != session_code.upper():
        return render(request, "app01/login.html", {"error": "验证码错误"})

    # 查询用户
    user = User.objects.filter(username=username).first()
    if not user:
        fail_count = _increase_fail(request, fail_count)
        return render(request, "app01/login.html", {"error": "用户名不存在"})

    # 校验密码（Django安全哈希）
    if not user.check_password(password):
        fail_count = _increase_fail(request, fail_count)
        return render(request, "app01/login.html", {"error": "密码错误"})

    # 登录成功，清空失败计数并写入 session
    request.session.pop("login_fail_count", None)
    request.session.pop("login_locked_until", None)
    request.session["user_id"] = user.id
    request.session["user_name"] = user.username
    return redirect("/depart/list/")


def _increase_fail(request, fail_count):
    """累加失败次数，达到上限时写入锁定时间"""
    import time
    fail_count += 1
    request.session["login_fail_count"] = fail_count
    if fail_count >= MAX_FAIL_COUNT:
        request.session["login_locked_until"] = int(time.time()) + LOCK_SECONDS
    return fail_count


def logout(request):
    """注销"""
    request.session.flush()
    return redirect("/login/")
