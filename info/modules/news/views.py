from flask import session, render_template, current_app
# 2-----导入蓝图对象，使用蓝图对象
from . import news_blue


@news_blue.route('/')
def index():
    # session["itcast"] = 'python18'
    # return 'Hello World!'
    return render_template('news/index.html')


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
