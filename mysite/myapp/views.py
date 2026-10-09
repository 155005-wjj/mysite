"""
函数：写"页面逻辑"的地方
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse



# Create your views here.
def index(request):
    return HttpResponse('欢迎使用')

def user_list(request):
    return render(request,'user_list.html')

def user_add(request):
    return render(request,'user_add.html')

def tpl(request):

    name="韩超发方法"
    roles=["管理员","CEO","保安"]
    user_info = {"name":"郭智","salary":100000, "role":"CTO"}
    data_list = [
        {"name":"郭智", "salary": 1000000, 'role': "CTO"},
        {"name":"卢慧","salary":1000000,"role":"CTO"},
        {"name":"赵建先","salary":1000000, 'role':"CTO"},
    ]
    return render(request, 'tpl.html',{"n1": name, "n2": roles, 'n3': user_info, "n4":data_list})

def weather(req):
    # 第三方模块：requests  (pip install requests)
    import requests

    res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=30.67&longitude=104.07&current=temperature_2m")
    data_list = res.json()
    print(data_list)

    return render(req, template_name='weather.html', context={"weather_list": data_list})

def something(request):

    print(request.method)

    print(request.GET)

    print(request.POST)

    return redirect('https://www.baidu.com')

def login(request):
    if request.method == "GET":
        return render(request, "login.html")

    # 如果是POST请求，获取用户提交的数据
    # print(request.POST)
    username = request.POST.get("user")
    password = request.POST.get("pwd")
    if username == 'root' and password == "123":
        # return HttpResponse("登录成功")
        return redirect("http://www.chinaunicom.com.cn/")

    # return HttpResponse("登录失败")
    return render(request, 'login.html', {"error_msg": "用户名或密码错误"})



from myapp.models import Department, UserInfo

def orm(request):
    #### 1.新建 ####
    # Department.objects.create(title="销售部")
    # Department.objects.create(title="IT部")
    # Department.objects.create(title="运营部")
    # UserInfo.objects.create(name="武沛齐", password="123", age=19)
    # UserInfo.objects.create(name="朱虎飞", password="666", age=29)
    # UserInfo.objects.create(name="吴阳军", password="666", age=22)
    # return HttpResponse("成功")

    # UserInfo.objects.filter(id=3).delete()
    # Department.objects.all().delete()
    # return HttpResponse('成功')

    # data_list = UserInfo.objects.all()
    # print(data_list)
    # for obj in data_list:
    #     print(obj.id, obj.name, obj.password, obj.age)
    # return HttpResponse('成功')

    # data_list1 = UserInfo.objects.filter(id = 1)
    # print(data_list1)
    # return HttpResponse('成功')

    # row_list = UserInfo.objects.filter(id=1).first()
    # print(row_list.id, row_list.name, row_list.password, row_list.age)
    # return HttpResponse("成功")

    UserInfo.objects.all().update(password=999)
    UserInfo.objects.filter(id=2).update(age=999)
    UserInfo.objects.filter(name='朱虎飞').update(age=999)
    return HttpResponse('成功')

def info_list(request):
    data_list = UserInfo.objects.all()

    return render(request,'info_list.html',
                  {'data_list': data_list})

def info_add(request):
    if request.method == "GET":
        return render(request,'info_add.html')

    #获取用户提交数据
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    age = request.POST.get("age")

    #添加到数据库
    UserInfo.objects.create(name=user, password=pwd, age=age)

    #自动跳转
    # return redirect('http://127.0.0.1:8000/info/list/')
    return redirect('/info/list/')

def info_delete(request):
    nid = request.GET.get('nid')
    UserInfo.objects.filter(id=nid).delete()
    return redirect('/info/list/')