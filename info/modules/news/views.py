from flask import session, render_template, current_app
# 2-----导入蓝图对象，使用蓝图对象
from . import news_blue
# 导入模型类
from info.models import User


@news_blue.route('/')
def index():
    """
    首页：
    实现页面右上角的内容，检查用户登录状态，
    如果用户登录，显示用户登录信息
    如果未登录，提供注册登录入口
    1. 从redis中获取用户id
    2. 根据user_id查询mysql, 获取用户信息
    3. 把用户信息传给模板

    :return:
    """
    user_id = session.get('user_id')
    user = None

    # 根据user_id读取mysql, 获取用户信息
    try:
        user = User.query.get(user_id)  # 返回是个对象
    except Exception as e:
        current_app.logger.error(e)

    # 定义字典，用来返回数据
    data = {
        'user_info': user.to_dict() if user else None
    }

    return render_template('news/index.html', data=data)


# 加载logo图标，浏览器会默认请求,url地址：http://127.0.0.1:5000/favicon.ico
# flask 默认创建一个静态路由
# favicon.ico 文件按路径：　http://127.0.0.1:5000/static/news/favicon.ico
# 原因：
# １. 浏览器不是每次都请求，会使用缓存
# 2. 清空浏览器缓存
# 3. 浏览器需要彻底重启
@news_blue.route('/favicon.ico')
def favicon():
    # favicon图标传给浏览器, 发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')
