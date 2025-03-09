from itertools import product
from loguru import logger
import string

chars = string.ascii_lowercase + string.digits

def generate_domains_3(suffix):
    suffix = suffix.lstrip('.')
    # len 1
    for ch in chars:
        yield f'{ch}.{suffix}'
    # len 2
    for combo in product(chars, repeat=2):
        yield f"{''.join(combo)}.{suffix}"
    # len 3
    for combo in product(chars, repeat=3):
        yield f"{''.join(combo)}.{suffix}"
    # 3位数带连字符
    for ch1 in chars:
        for ch2 in chars:
            yield f"{ch1}-{ch2}.{suffix}"

def generate_domains_4letter(suffix):
    suffix = suffix.lstrip('.')
    for combo in product(string.ascii_lowercase, repeat=4):
        yield f"{''.join(combo)}.{suffix}"

def generate_domains_4digit(suffix):
    suffix = suffix.lstrip('.')
    for combo in product(string.digits, repeat=4):
        yield f"{''.join(combo)}.{suffix}"

# def generate_domains_4mix(suffix):
#     suffix = suffix.lstrip('.')
#     # 字母 + 数字,   字母 + 连字符,   数字 + 连字符,   字母 + 数字 + 连字符
#     domains = []
#     for combo in product(string.ascii_lowercase + string.digits, repeat=4):
#         # 4位长度的字母与数字组合只保留aa22, 11bb类型
#         prefix = ''.join(combo)
#         if  (not prefix.isdigit()) and (not prefix.isalpha()) and (prefix[0] != prefix[1] or prefix[2] != prefix[3]):
#             continue
#         domain = f"{prefix}.{suffix}"
#         if domain <= last:
#             continue
#         domains.append(domain)
#         if len(domains) > 100000:
#             break
#     return domains
