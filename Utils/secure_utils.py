# -*- coding: UTF-8 -*-
# 安全相关的方法集合
# import hashlib
# import datetime
# import time
# import base64
# import xxtea
import string
import random

# XXTEA_KEY = "klicen_lxt4565"

# # 缺省的编解码版本
# DEF_CODEC_VER = 'a'


# def base64_url_decode(inp):
#     # 通过url传输时去掉了=号，所以需要补上=号
#     return base64.urlsafe_b64decode(str(inp + '=' * (4 - len(inp) % 4)))


# def base64_url_encode(inp):
#     return base64.urlsafe_b64encode(str(inp)).rstrip('=')


# def get_random_salt():
#     """
#     生成随机盐
#     """
#     now = time.time()
#     m = hashlib.md5(str(now))
#     return m.hexdigest()


# def get_encrypt_password(password, salt):
#     """加密算法，获得加密后的密码"""
#     m = hashlib.md5(password + salt + 'klicen')
#     return m.hexdigest()


# def get_active_token(email):
#     """生成激活码"""
#     plain = email + get_random_salt()
#     return hashlib.md5(plain).hexdigest()


# def get_email_from_token(token):
#     """从激活码里解密得到邮箱地址"""
#     plain = xxtea.decrypt(base64_url_decode(token.encode("utf-8")), XXTEA_KEY)
#     email = plain.split('#')[0]
#     return email


# class Codec():
#     """
#     名片ID加解密工具
#     """

#     def __init__(self,):
#         self.codec_ver = DEF_CODEC_VER

#     def encode(self, id):
#         """
#         根据设置的加密算法版本选择加密方法
#         加密字符串
#         """
#         id = str(id)
#         if self.codec_ver == 'a':
#             return self._alpha_encode(id)
#         else:
#             return id

#     def _alpha_encode(self, id):
#         """
#         a版的加密算法
#         xxtea算法加密之后，添加'a'作为前缀
#         """
#         ori_code = base64_url_encode(xxtea.encrypt(id, XXTEA_KEY))
#         code =DEF_CODEC_VER + ori_code
#         return code
    
#     def decode(self, code):
#         """
#         解密字符串
#         根据code版本选择解码算法
#         """
#         ver = code[0]
#         ori_code = code[1:]
#         if ver == 'a':
#             return self._alpha_decode(ori_code)
#         else:
#             raise ValueError
        
#     def _alpha_decode(self, code):
#         id = xxtea.decrypt(base64_url_decode(code.encode("utf-8")), XXTEA_KEY)
#         return id


def id_generator(size=6, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for x in range(size))


# def coupon_generator(size=6):
#     """
#     生成优惠码的算法
#     随机字符中删除Il1oO0等易造成混淆的字符
#     """
#     chars = 'abcdefghijkmnpqrstuvwxyz23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
#     return ''.join(random.choice(chars) for x in range(size))


# def random_digits_generator(size=16, chars=string.digits):
#     """随机数字"""
#     return ''.join(random.choice(chars) for x in range(size))


# if __name__ == '__main__':
#     salt = get_random_salt()
#     print "salt = "+salt+"\n" + get_encrypt_password("123456", salt)
#     active_token = get_active_token("istry@163.com")
#     print active_token
#     print get_email_from_token('ZjBkNDU1OGU5Zjk2YjY1NGRlMzIxODk0ZjEzODZmMTJmNTFiN2JkMGVmZWUyYjcw')
