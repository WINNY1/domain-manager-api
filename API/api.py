import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from API.get_md5 import get_md5
from API.qq_checker import QQChecker
from API.we_chat_checker import WeChatChecker
from API.db import UserDB, DomainDB

app = Flask(__name__)
CORS(app, resources=r'/*')  # 所有接口允许跨域资源共享

"""
接口返回数据约定:
type: json,
code: {
    0: 处理成功,
    1: 用户检查失败,
    2: 二维码过期，需要刷新,
    3: token不匹配, 需要重新登陆
    4: 需要先登陆微信
}
msg: {
    处理成功时: 空,
    处理失败时: 错误信息
}
data: {
    前端请求的数据
}
"""


@app.route('/api/take_token')
def take_token():
    """
    提供id2的test用户的token
    :return:
    """
    db = UserDB()
    data = db.take_token()
    if data:
        return jsonify({
            'code': 0,
            'msg': '',
            'data': data
        })


@app.route('/api/auto_login', methods=['GET', 'POST'])
def auto_login():
    """
    自动登陆接口, 通过用户id和token同步登陆状态
    :return:
    """
    if request.method == 'POST':
        user_id = request.form['user_id']
        token = request.form['token']
    else:
        user_id = request.args.get('user_id', type=int, default=None)
        token = request.args.get('token', type=str, default=None)
    db = UserDB()  # 连接数据库
    user_data = db.check_token(user_id, token)  # 验证用户
    if user_data:
        return jsonify({
            'code': 0,
            'msg': '',
            'data': {
                'id': user_data['id'],  # 用户id
                'status': user_data['status'],  # 用户状态码
                'token': user_data['token'],  # 用户token
                'endtime': user_data['endtime'],  # 接口有效期
                'username': user_data['username'],  # 用户名
                'userrank': user_data['userrank'],  # 用户等级
            }
        })
    else:
        return jsonify({
            'code': 3,
            'msg': 'token不匹配, 需要重新登陆'
        })


@app.route('/api/login', methods=['GET', 'POST'])
def login():
    """
    使用用户名和密码进行用户登陆操作
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    else:
        username = request.args.get('username', type=str, default=None)
        password = request.args.get('password', type=str, default=None)
    db = UserDB()  # 连接数据库
    user_data = db.check_user(username, password)  # 尝试获取用户信息
    if user_data:
        # 如果成功取得用户信息:
        data = {
            'id': user_data['id'],
            'token': get_md5(text=str(datetime.datetime.now().timestamp()))
        }
        db.update_information(data)  # 每次使用口令登陆时更新token
        return jsonify({
            'code': 0,
            'msg': '',
            'data': data,
        })
    else:
        return jsonify({
            'code': 1,
            'msg': '用户名或密码错误'
        })


@app.route('/api/qq_check')
def qq_check():
    """
    QQ网址检测
    :return:
    """
    user_id = request.args.get('user_id', type=str, default=None)
    token = request.args.get('token', type=str, default=None)
    url = request.args.get('url', type=str, default=None)
    db = UserDB()
    user_data = db.check_token(user_id, token)
    if user_data:
        if user_data['endtime'] >= datetime.datetime.now():  # 验证用户有效期
            c = QQChecker()  # 创建检测对象
            data = c.check(url)
            data.update({
                'username': user_data['username'],
                'endtime': user_data['endtime'].strftime('%Y-%m-%d')
            })  # 加入会员信息和有效期
            return jsonify({
                'code': 0,
                'msg': '',
                'data': data
            })
        else:
            return jsonify({
                'code': 1,
                'msg': '会员服务到期, 请及时续费'
            })
    else:
        return jsonify({
            'code': 1,
            'msg': '用户名或密码错误'
        })


@app.route('/api/we_chat_check', methods=['GET', 'POST'])
def we_chat_check():
    """
    检测微信域名
    :return:
    """
    if request.method == 'GET':
        # 获取用户名 密码 待检测域名信息
        user_id = request.args.get('user_id', type=str, default=None)
        token = request.args.get('token', type=str, default=None)
        domain = request.args.get('domain', type=str, default=None)
    else:
        # 获取用户名 密码 待检测域名信息
        user_id = request.form['user_id']
        token = request.form['token']
        domain = request.form['domain']
    return do_we_chat_check(user_id, token, domain)


def do_we_chat_check(user_id, token, domain):
    """
    验证用户并进行域名检测
    :param user_id:
    :param token:
    :param domain:
    :return:
    """
    db = UserDB()
    user_data = db.check_token(user_id, token)  # 验证用户
    if user_data:
        if user_data['endtime'] >= datetime.datetime.now():  # 验证用户有效期
            if user_data['cookies'] is None or user_data['baseurl'] is None:
                return jsonify({
                    'code': 4,
                    'msg': '需要先登陆微信',
                })  # 如果没有足够的信息进行检测, 则返回查询失败
            c = WeChatChecker(data={
                'uuid': None,
                'cookies': eval(user_data['cookies']),
                'baseurl': user_data['baseurl']
            })  # 创建检测对象
            data = c.check(domain)
            if data['status'] == 3:
                db.update_information(user_data={
                    'id': user_data['id'],
                    'status': 0
                })
                return jsonify({
                    'code': 4,
                    'msg': '需要先登陆微信'
                })
            data.update({
                'username': user_data['username'],
                'endtime': user_data['endtime'].strftime('%Y-%m-%d')
            })  # 加入用户名和有效期
            return jsonify({
                'code': 0,
                'msg': '',
                'data': data
            })
        else:
            db.update_information(user_data={
                'id': user_data['id'],
                'status': 0
            })
            return jsonify({
                'code': 1,
                'msg': '会员服务到期, 请及时续费'
            })
    else:
        return jsonify({
            'code': 1,
            'msg': '用户名或密码错误'
        })


@app.route('/api/login/we_chat/get_qr', methods=['GET', 'POST'])
def get_qr():
    """
    获取微信登陆的二维码
    :return:
    """
    try:
        c = WeChatChecker()  # 建立微信域名检测对象
        data = c.get_qr()  # 获取二维码
        return jsonify({
            'code': 0,
            'msg': '',
            'data': data
        })
    except Exception as e:
        print('微信登陆失败: ', e.args)


@app.route('/api/login/we_chat/get_status', methods=['GET', 'POST'])
def get_status():
    if request.method == 'GET':
        # 获取用户名 密码
        user_id = request.args.get('user_id', type=str, default=None)
        uuid = request.args.get('uuid', type=str, default=None)
    else:
        # 获取用户名 密码
        user_id = request.form['user_id']
        uuid = request.form['uuid']
    return do_the_get_status(user_id, uuid)


def do_the_get_status(user_id, uuid):
    db = UserDB()  # 连接数据库
    try:
        c = WeChatChecker(data={
            'cookies': None,
            'baseurl': None,
            'uuid': uuid
        })
        data = c.loading()
        if data:
            # 更新数据
            db.update_information(user_data={
                'id': user_id,
                'cookies': data['cookies'],
                'baseurl': data['baseurl'],
                'status': 1
            })
            return jsonify({
                'code': 0,
                'msg': '',
                'data': data
            })
        else:
            return jsonify({
                'code': 2,
                'msg': '二维码过期，需要刷新'
            })
    except Exception as e:
        print('微信登陆失败: ', e.args)


@app.route('/api/get_domain')
def get_domain():
    """
    获取数据
    实现get_domain接口, 在这里获取提取数据所需的参数并从域名数据库中取出数据
    :return:
    """
    # 提取请求中的参数
    where_condition = request.args.get('where_condition', type=str, default=None)
    row_count = request.args.get('row_count', type=int, default=None)
    offset = request.args.get('offset', type=int, default=None)
    # 从数据库提取数据
    db = DomainDB()
    count, data_list = db.get_domain(where_condition, row_count, offset)
    # 下一行用于测试页面加载效果
    # time.sleep(1)
    # 返回json格式的数据
    return jsonify({
        'code': 0,
        'msg': '',
        'data': {
            'count': count,
            'data': data_list,
        }
    })


@app.route('/api/get_user_information')
def get_user_information():
    """
    获取全部用户信息
    :return:
    """
    # 提取请求中的参数
    user_id = request.args.get('user_id', type=str, default=None)
    token = request.args.get('token', type=str, default=None)
    db = UserDB()
    if db.check_token(user_id, token):
        return jsonify({
            'code': 0,
            'msg': '',
            'data': db.get_users_information()
        })
