import time
import requests
import re
from config import *


class WeChatChecker(object):
    def __init__(self, data=None):
        if data is None:
            data = {'cookies': None, 'uuid': None, 'baseurl': None}
        self.headers = HEADERS  # 请求头，统一来自Config
        self.cookies = data['cookies']  # Cookies，一个对象维持一个可用cookies
        self.session = requests.Session()  # 会话，一个对象维持一个微信会话
        self.uuid = data['uuid']  # 存储登录需要的uuid
        self.base_url = data['baseurl']  # 存储查询需要的url

    def get_qr(self):
        """
        获取登录需要的二维码
        :return:
        """
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': 'wx782c26e4c19acffb',
            'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
            'fun': 'new',
            'lang': 'en_US',
            '_': int(time.time()),
        }
        r = self.session.get(url, headers=self.headers, params=params)
        # 提取uuid
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'

        data = re.search(regx, r.text)
        if data and data.group(1) == '200':
            self.uuid = data.group(2)
        # print('uuid: %s' % self.uuid)

        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        r = self.session.get(url, stream=True)
        data = {
            'url': r.url,
            'uuid': self.uuid
        }
        return data

    def loading(self):
        """
        等待扫码登录
        :return:
        """
        while True:
            url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login'
            params = 'tip=1&uuid=%s&_=%s' % (self.uuid, int(time.time()))
            r = self.session.get(url, headers=self.headers, params=params)
            regx = r'window.code=(\d+)'
            data = re.search(regx, r.text)
            if not data:
                continue
            if data.group(1) == '200':
                # 为了获取登录信息做准备
                uri_regex = r'window.redirect_uri="(\S+)";'
                redirect_uri = re.search(uri_regex, r.text).group(1)
                r = self.session.get(redirect_uri, allow_redirects=False)

                # 一下两行信息不影响功能
                # redirect_uri = redirect_uri[:redirect_uri.rfind('/')]
                # baseRequestText = r.text

                # 获取base_url
                regx = r'https://(\S+?)/'
                self.base_url = re.search(regx, r.url).group(1)
                break
            elif data.group(1) == '201':
                # print('You have scanned the QRCode')
                time.sleep(1)
            elif data.group(1) == '408':
                # raise Exception('QRCode should be renewed')
                return False
        # 保存cookies
        self.cookies = self.session.cookies.get_dict()
        return {
            'msg': '登陆成功',
            'cookies': self.cookies,
            'baseurl': self.base_url
        }

    def check(self, domain):
        """
        利用当前登录的微信号检查域名
        :param domain: 域名
        :return: 检测结果:dict
        """
        url = 'https://{baseurl}/cgi-bin/mmwebwx-bin/webwxcheckurl?requrl=http%3A%2F%2F{domain}'

        res = requests.get(url.format(baseurl=self.base_url, domain=domain), cookies=self.cookies, headers=self.headers,
                           allow_redirects=False)
        regx = r'https://weixin110.qq.com/cgi-bin+'
        try:
            if re.match(regx, res.headers['location']):
                status = 2
            else:
                status = 0
        except KeyError:
            status = 3
        return {
            'status': status,
            'errmsg': WECHAT_ERRMSG[str(status)],
            'domain': domain,
        }
