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
# 导入正则
import re
# 随机数
import random
# 导入云通讯
from info.libs.yuntongxun.sms import CCP


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


@passport_blue.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    发送短信
    接收参数-----检查参数------业务逻辑处理------返回结果
    1. 获取参数，mobile, image, code, image_code_id
    2. 检查参数，参数必须存在
    3. 检查手机号的格式，使用正则
    4. 检查图片验证码是否正确
    5. 从redis中获取真实的图片验证码
    6. 判断获取结果是否存在
    7. 如果存在，先删除redis数据库中的图片验证码，
    因为图片验证码只能比较一次，本质是只能读取一次redis数据库一次
    8. 比较图片验证码是否正确
    9. 生成短信验证码, 六位数
    10. 存储在redis 数据库中
    11. 调用云通讯发送短信
    12. 保存发送结果，用来判断发送是否成功
    13. 返回结果

    :return:
    """
    # 获取post请求的三个参数
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    # 检查参数的完整性
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 检查参数，手机号格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")
    # 根据uuid从redis中获取图片验证码
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
    # 判断获取错误
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证过期')
    # 如果获取到了图片验证码，需要把redis中的图片验证码删除，因为只能get一次
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 比较图片验证是否正确, 忽略大小写
    if real_image_code.lower() != image_code:
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    # 生成短信随机数
    sms_code = '%06d' % random.randint(0, 999999)
    # 存入redis中
    try:
        redis_store.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES,
                          sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 调用云通讯发送短信
    try:
        #　构造发送短信对象
        ccp = CCP()
        # 第一个参数手机号，第二个参数短信内容，　第三个参数模板id
        result = ccp.send_template_sms(mobile,
                              [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信异常")
    # 判断发送结果
    if result == 0:
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")




