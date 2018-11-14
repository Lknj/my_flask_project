from flask import session
# 2-----导入蓝图对象，使用蓝图对象
from . import  news_blue


@news_blue.route('/')
def index():
    session["itcast"] = 'python18'
    return 'Hello World!'
