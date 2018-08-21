from _md5 import md5


def get_md5(text):
    """
    对密码进行加密处理
    :param text: 原密码
    :return: 加密后的密码
    """
    return md5((text + 'DomainManagerSystem').encode('utf-8')).hexdigest()
