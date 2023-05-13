import hashlib
from django.conf import settings


# # 这是标准的MD5加密程序
# def md5(data_string):
#     obj1 = hashlib.md5()  # 常规md5加密
#
#     salt = 'xxxxxxxx'    # 加了一个盐，因为常规md5加密是固定的
#     obj2 = hashlib.md5(salt.encode('utf-8'))
#
#     obj2.update(data_string.encode('utf-8'))
#     return obj2.hexdigest()


def md5(data_string):
    # 这里的盐引入了django自带的一个secret_key的字符串，是自动生成的。
    obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()
