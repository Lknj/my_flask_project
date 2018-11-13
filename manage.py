from flask import Flask, session
# 集成管理器脚本
from flask_script import Manager
# 集成SQLalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 数据库迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 集成状态保持的扩展
from flask_session import Session
from config import config_dict


app = Flask(__name__)

# 使用配置信息
app.config.from_object(config_dict['development'])

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
