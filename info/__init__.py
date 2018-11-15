from flask import Flask
from config import config_dict
# 集成SQLalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 集成状态保持的扩展
from flask_session import Session
# 集成python的标准日志模块
import logging
from logging.handlers import RotatingFileHandler
# 创建sqlalchemy对象
db = SQLAlchemy()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 定义函数，封装程序初始化操作，　--->工厂函数
# 工厂函数: 生产实例app
# 让启动文件manage来调用函数实现动态的传入不同的配置信息，获取不同配置信息下的app
def create_app(config_name):

    app = Flask(__name__)

    # 使用配置信息
    app.config.from_object(config_dict[config_name])

    # 通过db对象，让程序实例和db进行关联
    db.init_app(app)

    # 实例化Session
    Session(app)

    # 3----导入蓝图，注册蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)

    return app