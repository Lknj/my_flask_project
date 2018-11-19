# 自定义过滤器
from flask import current_app
from flask import g
from flask import session

from info.models import User


def index_filter(index):
    if index == 0:
        return 'first'
    elif index == 1:
        return 'second'
    elif index == 2:
        return 'third'
    else:
        return ''

# 装饰器: 函数嵌套，本质是闭包，作用：不修改代码的前提下，添加新的功能
# 登录验证装饰器
# 标准模块让被装饰的函数属性不发生变化
import functools


def login_required(f):
    @functools.wraps(f)
    def warpper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            # 根据user_id读取mysql, 获取用户信息
            try:
                user = User.query.get(user_id)  # 返回是个对象
            except Exception as e:
                current_app.logger.error(e)
            # flask　内置的函数，和request  session 一样，在请求的过程中存在，
            # 请求结束后，被销毁
            # 用来临时存储数据
        user = g.user
        return f(*args, **kwargs)
    # 在返回warpper之前，把被装饰的函数名，赋值给warpper
    # warpper.__name__ = f.__name__
    return warpper()