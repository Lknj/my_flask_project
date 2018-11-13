from flask import Flask
from config import config_dict
# 集成SQLalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 集成状态保持的扩展
from flask_session import Session

# 创建sqlalchemy对象
db = SQLAlchemy()

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

    return app