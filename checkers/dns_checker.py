import socket
from loguru import logger

# 判断域名是否已注册（基于 DNS 查询）
def is_domain_registered(domain):
    try:
        socket.gethostbyname(domain)
        return True  # 如果解析成功，域名已注册
    except socket.gaierror:
        return False  # 如果解析失败，域名可能未注册