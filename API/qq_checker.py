import re
from datetime import datetime

import requests


class QQChecker(object):
    def __init__(self):
        self.base_url = 'https://cgi.urlsec.qq.com/index.php'
        self.base_data = {
            'm': 'check',
            'a': 'check',
            'callback': 'jQuery17208847999825797728_1533381652775',
            '_': int(datetime.now().timestamp() * 1000),
            'url': None,
        }
        self.base_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'pgv_pvi=2302749696; pt2gguin=o1352234718; RK=7xj4GKvhS5; ptcz=8cc0655717165881c02786bf0a12b8bc808249589067b2ad24309316051f0432; pgv_pvid=307346945; tvfe_boss_uuid=c82c986f57121afa; o_cookie=1352234718; pgv_si=s2217801728; pgv_info=ssid=s9741839518',
            'Host': 'cgi.urlsec.qq.com',
            'Referer': None,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        }
        self.base_results = {
            '1': '未知网站',
            '2': '危险网站',
            '3': '安全网站',
        }

    def check(self, url):
        self.base_data['url'] = url
        self.base_headers['Referer'] = 'https://guanjia.qq.com/online_server/result.html?url={url}&='.format(url=url)
        response = requests.get(url=self.base_url, params=self.base_data, headers=self.base_headers)
        if response.status_code == requests.codes.ok:
            # 解析数据
            data = eval(re.search(r'\((.*?)\)', response.text).group(1))
            if data['reCode'] == 0:
                data = data['data']['results']
                return {
                    'url': url,
                    'status': data['whitetype'],
                    'errmsg': self.base_results[str(data['whitetype'])],
                }
            return {
                'status': 0,
                'errmsg': '格式错误, 请重新输入',
                'url': url
            }
        else:
            return {
                'status': 0,
                'errmsg': '请求失败, 请稍后再试',
                'url': url
            }
