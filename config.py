# 导入redis模块
from redis import StrictRedis


class Config:

    DEBUG = True
    # 配置秘钥
    SECRET_KEY = 'nBZKnG1Uh9oaV/5pz0In0Nc5b9RQc/4PUDQedSZwFwq4IOUB2WymC+x9gKsMhm3S45u5oGFpm6ispAgnAk5UREDm'


    # mysql 配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/my_info'
    # 动态追踪修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置session信息存储在redis中
    SESSION_TYPE = 'redis'
    # 定义redis 的主机和端口号
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    # session 有效期的设置，Flask内置的
    PERMANET_SESSION_LIFETIME = 86400

# 封装不同环境的配置类，生产模式
class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

# 定义字典，实现不同环境下的不同映射
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}