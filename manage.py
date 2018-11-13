from flask import session
# 集成管理器脚本
from flask_script import Manager
# 数据库迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 导入info目录下的app和db
from info import create_app, db

app = create_app('development')

# 使用管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app, db)
# 添加迁移命令
manage.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session["itcast"] = 'python18'
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
