# 导入蓝图模块
from flask import Blueprint

# 创建蓝图对象
passport_blue = Blueprint('passport_blue', __name__)
# 把导入蓝图对象的文件views 导入到创建蓝图对象的下面

from . import views
