from flask import g
from flask import session, render_template, current_app, jsonify, request
# 2-----导入蓝图对象，使用蓝图对象
from info.utils.response_code import RET
from . import news_blue
# 导入模型类
from info.models import User, News, Category, Comment, CommentLike
# 导入常量文件
from info import constants, db
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

    # 定义标记，用来标识用户是否收藏
    is_collected = False
    # 判断用户是否登录，以及用户是否收藏该新闻
    if g.user and news in user.collection_news:
        is_collected = True

    # 新闻的评论信息
    try:
        comment_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询评论信息失败")
    # 定义容器
    comments = []
    # 如果该评论有内容
    if comment_list:
        for comment in comment_list:
            comments.append(comment.to_dict())
    # 定义容器, 返回数据
    data = {
        'news_detail': news.to_dict(),
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list,
        'is_collected': is_collected,
        'comments': comments

    }
    return render_template('news/detail.html', data=data)


@news_blue.route('/news_collect', methods=["POST"])
@login_required
def user_collect():
    """
    用户收藏取消收藏
    1. 判断用户是否登录
    2. 如果没有登录，返回错误信息
    3. 获取参数，news_id, action[collect, cancel_collect]
    4. 检查参数的完整性
    5. 转换参数类型news_id
    6. 检查action是否是[collect, cancel_collect]
    7. 判断如果用户选择的是收藏，添加该新闻
    8. 否则，移除用户收藏的新闻
    9. 返回结果

    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 检查参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 转换参数类型
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")
    # 检查action参数
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式错误")
    # 根据news_id查询数据，确认新闻的存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻数据失败")
    # 判断查询结果
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="无新闻数据")
    # 如果用户是收藏
    if action == 'collect':
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)
    # 提交数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="新闻收藏失败")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK")


@news_blue.route('/news_comment', methods=["post"])
@login_required
def news_comments():
    """
    新闻评论
    获取参数－－检查参数－－业务处理－－返回结果
    用户必须登录
    1. 获取参数，news_id/comment/parent_id（可选）
    2. 检查参数
    3. 转换参数的数据类型，判断parent_id是否存在
    4. 根据新闻，确认新闻的存在
    5. 保存评论信息，判断parent_id是否存在
    6. 提交数据
    7. 返回结果

    :return:
    """
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取参数
    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')
    # 检查参数
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 转换数据类型
    try:
        news_id = int(news_id)
        # 如果有父评论, 保存父评论信息
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")
    # 查询数据库，确认新闻的存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    # 判断查询结果
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="没有新闻数据")
    # 构造评论的模型类对象
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id
    # 提交数据
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="评论失败")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@news_blue.route('/comment_like', methods=["POST"])
@login_required
def comment_like():
    """
    评论点赞
    获取参数－－检查参数－－业务处理－－返回结果
    用户必须登录
    1. 获取参数，comment_id, news_id, action
    2. 检查参数
    3. 判断参数
    4. 查询评论数据
    5. 保存点赞信息
    6. 提交数据
    7. 返回结果

    :return:
    """
    # 确认用户登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户为登录")
    # 获取参数
    comment_id = request.json.get("comment_id")
    # news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 判断参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    if action not in ("add", "remove"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 查询评论数据
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if action == "add":
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            # 增加点赞条数
            comment.like_count += 1
    else:
        # 删除点赞数据
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
        if comment_like:
            db.session.delete(comment_like)
            # 减小点赞条数
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")
    return jsonify(errno=RET.OK, errmsg="操作成功", )


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
