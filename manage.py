from flask import Flask, session
# 集成管理器脚本
from flask_script import Manager
# 集成SQLalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 数据库迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 集成状态保持的扩展
from flask_session import Session
# 导入redis模块
from redis import StrictRedis


app = Flask(__name__)
# 配置秘钥
app.config['SECRET_KEY'] = 'nBZKnG1Uh9oaV/5pz0In0Nc5b9RQc/4PUDQedSZwFwq4IOUB2WymC+x9gKsMhm3S45u5oGFpm6ispAgnAk5UREDm'


# mysql 配置信息
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/my_info'
# 动态追踪修改
app.config['SESSION_TRACK_MODIFICATIONS'] = False

# 配置session信息存储在redis中
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = StrictRedis(host='127.0.0.1', port=6379)
app.config['SESSION_USE_SIGNER'] = True
# session 有效期的设置，Flask内置的
app.config["PERMANET_SESSION_LIFETIME"] = 86400

# 创建sqlalchemy对象
db = SQLAlchemy(app)

# 使用管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app, db)
# 添加迁移命令
manage.add_command('db', MigrateCommand)


# 实例化Session
Session(app)


@app.route('/')
def index():
    session["itcast"] = 'python18'
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
