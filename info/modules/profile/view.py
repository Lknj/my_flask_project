from flask import render_template

from . import profile_blue

from flask import redirect
from info.utils.commons import login_required
from flask import g

@profile_blue.route('/info')
@login_required
def user_info():
    """
    用户登录信息展示
    1. 尝试获取用户信息
    2. 如果用户未登录,重定向到项目首页
    3. 如果用户已登录,使用模板渲染数据

    :return:
    """
    user = g.user
    if not user:
        return redirect('/')
    data = {
        'user': user.to_dict()
    }
    return render_template('news/user.html', data=data)


@profile_blue.route('/base_info')
def base_info():
    """
    用户基本信息

    :return:
    """
    user = g.user
    data = {
        'user': user.to_dict()
    }
    return render_template('news/user_base_info.html', data=data)