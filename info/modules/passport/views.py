# 导入蓝图对象
from . import passport_blue
# 导入captcha工具，生成图片验证码
from info.utils.captcha.captcha import captcha
# 导入flask 内置的请求上下文对象,...   应用上下文对象(针对当前请求的一个请求对象)
from flask import request, jsonify, current_app, make_response
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入redis实例，               常量文件
from info import redis_store, constants


@passport_blue.route('/image_code')
def generate_image_code():
    """
    生成图片验证码
    接收参数-----检查参数------业务逻辑处理------返回结果
    参数：前段需要传入uuid
    1. 获取前段传入的uuid，查询字符串args
    2. 如果没有uuid 　返回信息
    3. 调用captcha工具，生成验证码
    name, text, image文件
    4. 把照片验证码的内容text, 根据uuid 存入redis数据库中
    5. 返回图片
    :return:
    """
    image_code_id = request.args.get('image_code_id')
    # 检查参数是否存在,导入response_code.py文件
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 调用工具captcha生成图片验证码
    name, text, image = captcha.generate_captcha()
    # 把text存入redis数据库中, 在info/__init__文件中实例化redis对象
    try:
        redis_store.setex('ImageCode_' + image_code_id,
                          constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 把错误信息记录到项目日志中
        current_app.logger.error(e)
        # 直接终止程序运行
        return jsonify(errno=RET.DBERR, errmsg='存储数据失败')
    else:
        # 使用响应对象返回图片
        respone = make_response(image)

        # 返回响应
        return respone
