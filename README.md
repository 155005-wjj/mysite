# mysite

一个随手搭的 Django 小项目，纯粹是学框架的时候自己折腾用的。没指望它多正经——就是拿路由、模板、表单、ORM，还有随手调了个天气接口练手。想克隆就克隆，跑一跑、拆一拆，随你。

> 学习用途，里面留了不少乱七八糟的实验痕迹，别嫌弃。

## 里面都有啥

- `/index/` — 打个招呼，就这
- `/login/` — 超简单的校验（`root` / `123`），对了就跳转
- `/info/list/` · `/info/add/` · `/info/delete/` — 一个用户表的增删查改闭环
- `/weather` — 从 Open-Meteo 拉成都的实时温度
- `/orm/` — 我的 ORM 笔记，大部分是注释掉的增删改查片段
- `/user/*`、`/tpl`、`/something` — 模板和跳转的小实验

## 跑起来

需要 Python 3.10+，还要一个 MySQL（或者干脆换 SQLite 也行）。

```bash
pip install django requests
```

数据库配置在 `mysite/settings.py` 里，改成你自己的：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "test1",
        "USER": "root",
        "PASSWORD": "123456",   # ← 记得改
        "HOST": "127.0.0.1",
        "PORT": 3306,
    }
}
```

然后：

```bash
python manage.py makemigrations myapp
python manage.py migrate
python manage.py runserver
```

浏览器打开 http://127.0.0.1:8000/index/ ，自己玩吧。

## 结构瞅一眼

```
mysite/
├── manage.py
├── mysite/          # settings、urls、wsgi/asgi
└── myapp/           # 真正干活的应用
    ├── views.py     # 页面逻辑都在这
    ├── models.py    # UserInfo + Department
    ├── templates/   # html 页面
    └── static/      # css / js / img
```

## 备注

- 就两个模型：`UserInfo`（name / password / age）和 `Department`（title）。
- 上面那串数据库账号密码是本地开发占位，别把真的推到 GitHub 上。
- `test`、`test1`、`db.sqlite3`、`__pycache__/` 这些是垃圾文件，忽略掉（或者丢进 gitignore）。
