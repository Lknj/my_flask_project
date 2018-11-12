from flask import Flask

# 导入数据库扩展，并在配置中填写相关配置
from flask_sqlalchemy import SQLAlchemy

# 导入redis扩展包
import redis

# 包含请求体的请求都需要开启CSRF
from flask_wtf.csrf import CSRFProtect

# 利用flask_session扩展，将session数据保存到Redis中
from flask_session import Session

from flask_script import Manager
# 数据库迁移扩展
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)


# 先在当前类中定义配置的类，并从中加载配置
class Config:
    """工程配置信息"""
    DEBUG = True
    # os,base64  os.urandom  base64.b64encode
    SESSION_KEY = "NPSlFEu3wMk6ofiJaLuTl3TBKEGSbuZT1eJBF+MVSpqrdQbd2ir+Itm3lZfNQB+MjruExZheHrU37W5UeeqPCQ=="
    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/my_info"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # flask_session配置信息
    SESSION_TYPE = "redis" # 指定session 保存到redis　中
    SESSION_USE_SIGNER = True # 让 cookie 中的　session_id 被加密签名处理
    # 使用　redis 实例
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400 # session 的有效期，　单位是秒

app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要自己实现
CSRFProtect(app)

Session(app)

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    manager.run()
