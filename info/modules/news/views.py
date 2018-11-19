from flask import g
from flask import session, render_template, current_app, jsonify, request
# 2-----导入蓝图对象，使用蓝图对象
from info.utils.response_code import RET
from . import news_blue
# 导入模型类
from info.models import User, News, Category
# 导入常量文件
from info import constants
# 导入自定义的装饰器
from info.utils.commons import login_required


@news_blue.route('/')
@login_required
def index():
    """
    首页：
    一. 实现页面右上角的内容，检查用户登录状态，
    如果用户登录，显示用户登录信息
    如果未登录，提供注册登录入口
    1. 从redis中获取用户id
    2. 根据user_id查询mysql, 获取用户信息
    3. 把用户信息传给模板
    二. 新闻点击排行展示：
    根据新闻的点击次数查询数据库，使用模板渲染
    三. 新闻分类展示
    查询所有新闻分类，使用模板渲染数据
    :return:
    """
    # user_id = session.get('user_id')
    # user = None
    #
    # # 根据user_id读取mysql, 获取用户信息
    # try:
    #     user = User.query.get(user_id)  # 返回是个对象
    # except Exception as e:
    #     current_app.logger.error(e)
    user = g.user

    # 新闻点击排行查询
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻排行失败")
    # 判断查询结果
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg="无新闻排行数据")
    # 定义一个容器，存储新闻数据
    news_click_list = []
    for news in news_list:
        news_click_list.append(news.to_dict())

    # 新闻分类展示
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻分类数据失败")
    # 判断查询结果
    if not categories:
        return jsonify(errno=RET.NODATA, errmsg="无新闻分类数据")
    # 定义容器，存储新闻分类数据
    category_list = []
    # 遍历插叙结果
    for category in categories:
        category_list.append(category.to_dict())

    # 定义字典，用来返回数据
    data = {
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list,
        'category_list': category_list
    }

    return render_template('news/index.html', data=data)


@news_blue.route('/news_list')
def news_list():
    """
    首页新闻列表
    获取参数－－检查参数－－业务处理－－返回结果
    1. 获取参数　get请求获取  cid   page   per_page
    2.                  cid 分类id　　
    2. 检查参数，转化参数的数据类型
    cid, page, per_page = int(cid), int(page), int(per_page)
    3. 根据分类id查询新闻列表，新闻列表默认按照新闻发布时间倒序排序
    4. 判断用户选择的新闻分类
    实现形式一
    if cid> 1:
        News.query.fliter(news, category_id==cid).order_by(News.create_time.desc()).pageinait(page, perpage, False)
    else:
        News.query.filter().order_by(News.create_time.desc()).pageinait(page, perpage, False)

    实现形式二
    fliers = []
    if cid > 1:
        filters.append(News.category_id==cid)
    # 拆包
        News.query.filter(*filters).order_by(News.create_time.desc()).pageinait(page, perpage, False)
    5. 获取分页后的数据
    paginate.items 分页总数据
    paginate.pages 分页总页数
    pageinate.page 分页当前页数
    6. 遍历分页后的总数据，调用模型类中的方法，转成字典
    7. 返回结果

    :return:
    """
    # 获取参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    # 检查参数
    try:
        cid, page, per_page = int(cid), int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")
    # 根据分类id查询数据库
    filters = []
    # 如果分类id不是最新, 添加分类id给filter过滤条件
    if cid > 1:
        filters.append(News.category_id == cid)
    # 查询数据库
    try:
        # 拆包
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻列表失败")
    # 使用分页对象，　获取分页后的数据，总数据，总页数，当前页数
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    # 遍历分页数据，转成字典
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 定义容器　返回数据
    data = {
        'total_page': total_page,
        'current_page': current_page,
        'news_dict_list': news_dict_list
    }
    # 返回数据
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@news_blue.route('/<int:news_id>')
@login_required
def news_detail(news_id):
    """
    新闻详情：
    1. 根据news_id查询mysql数据库
    2. 使用模板渲染数据

    """
    # user_id = session.get('user_id')
    # user = None
    #
    # # 根据user_id读取mysql, 获取用户信息
    # try:
    #     user = User.query.get(user_id)  # 返回是个对象
    # except Exception as e:
    #     current_app.logger.error(e)
    user = g.user
    # 新闻点击排行查询
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻排行失败")
    # 判断查询结果
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg="无新闻排行数据")
    # 定义一个容器，存储新闻数据
    news_click_list = []
    for news in news_list:
        news_click_list.append(news.to_dict())

    # 查询数据库
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻详情数据失败")
    # 判断查询结果
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="无新闻数据")
    # 定义容器
    data = {
        'news_detail': news.to_dict(),
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list

    }
    return render_template('news/detail.html', data=data)


# 加载logo图标，浏览器会默认请求,url地址：http://127.0.0.1:5000/favicon.ico
# flask 默认创建一个静态路由
# favicon.ico 文件按路径：　http://127.0.0.1:5000/static/news/favicon.ico
# 原因：
# １. 浏览器不是每次都请求，会使用缓存
# 2. 清空浏览器缓存
# 3. 浏览器需要彻底重启
@news_blue.route('/favicon.ico')
def favicon():
    # favicon图标传给浏览器, 发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')
