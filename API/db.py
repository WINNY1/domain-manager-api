import pymysql
from API.get_md5 import get_md5
from config import *

"""
DomainManager.users:

+----------+-------------+------+-----+-------------------+-----------------------------+
| Field    | Type        | Null | Key | Default           | Extra                       |
+----------+-------------+------+-----+-------------------+-----------------------------+
| id       | int(11)     | NO   | PRI | NULL              | auto_increment              |
| username | varchar(45) | NO   |     | NULL              |                             |
| password | varchar(45) | NO   |     | NULL              |                             |
| cookies  | text        | YES  |     | NULL              |                             |
| endtime  | timestamp   | NO   |     | CURRENT_TIMESTAMP |                             |
| userrank | varchar(45) | NO   |     | NULL              |                             |
| status   | int(11)     | NO   |     | NULL              |                             |
| baseurl  | varchar(45) | YES  |     | NULL              |                             |
| update   | timestamp   | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
| token    | varchar(45) | YES  |     | NULL              |                             |
+----------+-------------+------+-----+-------------------+-----------------------------+
"""


# 用户数据库
class UserDB(object):
    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB):
        """
        MYSQL初始化
        :param host: 地址
        :param port: 端口
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库
        """
        try:
            self.db = pymysql.connect(
                host=host,
                port=port,
                user=user,
                passwd=passwd,
                db=db,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
            print(e.args)

    def __del__(self):
        self.db.close()

    def check_user(self, username, password):
        """
        检查用户名密码是否正确
        :param username: 用户名
        :param password: 密码
        :return:
        """
        try:
            with self.db.cursor() as cursor:
                sql_query = "select * from users where username=%s and password=%s"
                cursor.execute(sql_query, (username, get_md5(text=password)))
                data = cursor.fetchall()
            if data:
                return data[0]
            else:
                return False
        except pymysql.MySQLError as e:
            print(e.args)
            return False

    def check_token(self, user_id, token):
        """
        检查用户是否已登陆
        :param user_id: 用户ID
        :param token: token
        :return:
        """
        try:
            with self.db.cursor() as cursor:
                sql_query = "select * from users where id=%s and token=%s"
                cursor.execute(sql_query, (user_id, token))
                data = cursor.fetchall()
            if data:
                return data[0]
            else:
                return False
        except pymysql.MySQLError as e:
            print(e.args)
            return False

    def update_information(self, user_data):
        condition = 'set'
        for key, value in user_data.items():
            if key == 'cookies':
                value = pymysql.escape_string(str(value))
            condition += " {0}='{1}',".format(key, value)
        condition = condition[:-1]
        try:
            with self.db.cursor() as cursor:
                sql_query = "update users %s where id=%s" % (condition, user_data['id'])
                cursor.execute(sql_query)
            self.db.commit()
            return True
        except pymysql.MySQLError as e:
            print(e.args)
            return False

    def take_token(self):
        """
        获取2号用户的token
        :return:
        """
        try:
            with self.db.cursor() as cursor:
                sql_query = "select token from users where id=2"
                cursor.execute(sql_query)
                data = cursor.fetchone()
            if data:
                return data
            else:
                return False
        except pymysql.MySQLError as e:
            print(e.args)
            return False

    def get_users_information(self):
        try:
            with self.db.cursor() as cursor:
                sql_query = "select * from users"
                cursor.execute(sql_query)
                data_list = cursor.fetchall()
            if data_list:
                return data_list
            else:
                return False
        except pymysql.MySQLError as e:
            print(e.args)
            return False


"""
DomainManager.domain:

+---------+-------------+------+-----+-------------------+-----------------------------+
| Field   | Type        | Null | Key | Default           | Extra                       |
+---------+-------------+------+-----+-------------------+-----------------------------+
| id      | int(11)     | NO   | PRI | NULL              | auto_increment              |
| domain  | varchar(45) | NO   |     | NULL              |                             |
| price   | varchar(45) | NO   |     | NULL              |                             |
| date    | varchar(45) | NO   |     | NULL              |                             |
| status  | int(11)     | NO   |     | 3                 |                             |
| status2 | int(11)     | NO   |     | 3                 |                             |
| site    | text        | YES  |     | NULL              |                             |
| update  | timestamp   | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
+---------+-------------+------+-----+-------------------+-----------------------------+
"""


# 域名信息数据库
class DomainDB(object):
    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB):
        """
        MYSQL初始化
        :param host: 地址
        :param port: 端口
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库
        """
        try:
            # 连接数据库
            self.db = pymysql.connect(
                host=host,
                port=port,
                user=user,
                passwd=passwd,
                db=db,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
            print(e.args)

    def __del__(self):
        # 关闭数据库连接
        self.db.close()

    def get_domain(self, where_condition, row_count, offset):
        """
        获取数据
        :param where_condition: 筛选规则
        :param row_count: 起始行
        :param offset: 偏移量
        :return: 数据总数和数据内容
        """
        with self.db.cursor() as cursor:
            # 获取总数
            sql_query = "select count(*) from domain %s" % where_condition
            cursor.execute(sql_query)
            count = cursor.fetchone()['count(*)']
            # 获取数据
            sql_query = "select * from domain %s order by id desc limit %s, %s" % (where_condition, row_count, offset)
            cursor.execute(sql_query)
            data_list = cursor.fetchall()

            for data in data_list:
                # 把update格式化为字符串
                data['update'] = data['update'].strftime('%Y-%m-%d %H:%M:%S')
            return count, data_list
