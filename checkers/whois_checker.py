import subprocess
import sys
import re
from datetime import datetime
import time
from loguru import logger

DOMAIN_PATTERNS = {
    # 通用商业域名
    'com': {
        'unregistered': ['No match for domain', 'No match for', 'NOT FOUND'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'net': {
        'unregistered': ['No match for domain', 'No match for', 'NOT FOUND'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'org': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match for domain'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'info': {
        'unregistered': ['NOT FOUND', 'DOMAIN NOT FOUND', 'no matching record'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'biz': {
        'unregistered': ['No Data Found', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },

    # 技术相关域名
    'io': {
        'unregistered': ['is available for purchase', 'DOMAIN NOT FOUND', 'NOT FOUND'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar URL:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'ai': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'The queried object does not exist'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'app': {
        'unregistered': ['Domain not found', 'The queried object does not exist', 'NOT FOUND'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'dev': {
        'unregistered': ['Domain not found', 'The queried object does not exist', 'NOT FOUND'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'tech': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'code': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'The queried object does not exist'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },

    # 国家和地区域名
    'am': {
        'unregistered': ['NO MATCH', 'Domain not found', 'No match found'],
        'registered': [
            'Domain name:',
            'Registrar:',
            'Status:',
            'Registration date:',
            'Reserved name',
            'Reserved one-symbol'
        ]
    },
    'be': {
        'unregistered': ['Status:\tAVAILABLE', 'No such domain', 'Status: FREE'],
        'registered': [
            'Domain:',
            'Status: NOT AVAILABLE',
            'NOT ALLOWED',
            'Registered:',
            'Registrant:'
        ]
    },
    'so': {
        'unregistered': ['Not found:', 'NO MATCH', 'No Object Found', 'Domain Cannot Be Registered'],
        'registered': [
            'Domain Name:',
            'Domain ID:',
            'Sponsoring Registrar:',
            'Created On:'
        ]
    },
    'im': {
        'unregistered': ['not found', 'NOT FOUND', 'Domain not found'],
        'registered': [
            'Domain Name:',
            'Domain Managers',
            'Registration Status:',
            'Record Created:'
        ]
    },
    'is': {
        'unregistered': ['No entries found', 'Not found', 'Status: free'],
        'registered': [
            'domain:',
            'registrant:',
            'admin-c:',
            'created:'
        ]
    },
    'to': {
        'unregistered': ['is available', 'Congratulations', 'curl post: https://www.tonic.to/newcustform1.htm?F5C983A5;;;'],
        'registered': [
            'So sorry',
            "that one's taken",
        ]
    },
    'me': {
        'unregistered': ['NOT FOUND', 'no matching record', 'Domain not found'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'ms': {
        'unregistered': ['No match for', 'NOT FOUND', 'No Object Found'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },
    'cc': {
        'unregistered': ['No match for', 'NOT FOUND', 'Domain Status: Available'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'sh': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:',
            'This name is',
            'reserved by the Registry'
        ]
    },
    'gg': {
        'unregistered': ['no matching record', 'NOT FOUND', 'Domain not found'],
        'registered': [
            'Domain Status:',
            'Registrant:',
            'Registrar:',
            'Registration status:'
        ]
    },
    'tt': {
        'unregistered': ['No match', 'NOT FOUND', 'Domain Status: Available'],
        'registered': [
            'Domain Name:',
            'Registrar:',
            'Creation Date:',
            'Registry Expiry Date:'
        ]
    },

    # 创意域名
    'xyz': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'top': {
        'unregistered': ['does not exist', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'fun': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'dog': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'The queried object does not exist'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'run': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'The registration of this domain is restricted',
            'it is protected by',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'ink': {
        'unregistered': ['NOT FOUND', 'No Data Found', 'No match'],
        'registered': [
            'Domain Name',
            'Reserved'
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'cool': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'The registration of this domain is restricted',
            'available for purchase',
            'it is protected by',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'love': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'is available'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'blue': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match', 'is available for purchase'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    },
    'free': {
        'unregistered': ['NOT FOUND', 'Domain not found', 'No match'],
        'registered': [
            'Domain Name:',
            'Registry Domain ID:',
            'Registrar:',
            'Creation Date:'
        ]
    }
}

def run_whois(domain):
    """执行whois命令并返回结果"""
    try:
        cmd_list = ['whois', domain]
        if domain.endswith('.to'):
            prefix = domain.split('.to')[0]
            cmd_list = ["curl", "-X", "POST", "https://www.tonic.to/newcustform1.htm?F5C983A5;;;", "-H", "Content-Type: application/x-www-form-urlencoded", "-d", f"command=findandhold&error=nametaken.htm&sld={prefix}&B1.x=45&B1.y=20"]
        process = subprocess.Popen(cmd_list,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        output, error = process.communicate(timeout=5)

        if process.returncode not in [0, 1]:  # ['cc', 'com', 'net']
            return None, f"{domain} WHOIS查询失败: {error}, {process.returncode}"

        return output, None
    except subprocess.TimeoutExpired:
        return None, f"{domain} WHOIS查询超时"
    except Exception as e:
        return None, f"{domain} 执行WHOIS命令时出错: {str(e)}"

def is_not_registered(whois_text, tld):
    """检查域名是否已注册"""
    if not whois_text:
        return None, "无WHOIS信息"

    whois_text_upper = whois_text.upper()
    patterns = DOMAIN_PATTERNS.get(tld, {
        'unregistered': ['NO MATCH', 'NOT FOUND', 'DOMAIN NOT FOUND'],
        'registered': ['Domain Name:', 'Registrar:']
    })

    # 检查未注册特征
    for pattern in patterns['unregistered']:
        if pattern.upper() in whois_text_upper:
            return True, "域名未注册"

    # 检查已注册特征
    matches = 0
    required_matches = min(2, len(patterns['registered']))

    for pattern in patterns['registered']:
        if pattern.upper() in whois_text_upper:
            matches += 1
            if matches >= required_matches:
                return False, "域名已注册"

    # 特殊处理某些TLD
    # special_tlds = ['im', 'is']
    # if tld in special_tlds:
    #     if len(whois_text.split('\n')) > 5:  # 如果响应包含多行信息
    #         return True, "域名已注册"

    return None, "无法确定注册状态"

def is_domain_avaliable(domain):
    """检查域名状态"""
    tld = domain.strip().lower().split('.')[-1]
    if not tld:
        logger.info(f"无效的域名格式: {domain}")
        return None, f"无效的域名格式: {domain}"

    whois_text, error = run_whois(domain)
    if error:
        logger.info(f"whois error: {error}")
        return None, error

    ret, status = is_not_registered(whois_text, tld)

    if ret is None:
        logger.info(f""" {domain} 无法确定注册状态, 原始WHOIS信息: {whois_text}\n""")
        return None, "无法确定注册状态"
    return ret, status

if __name__ == "__main__":
    logger.add("whois.log", rotation="500 MB")
    # tld_list = [".ai", ".am", ".so", ".io", ".im", ".is", ".me", ".ms",
    #             ".sh", ".gg", ".org", ".biz", ".app",
    #             ".dev", ".xyz", ".top", ".fun", ".dog", ".run", ".ink", ".cool",
    #             ".love", ".blue", ".tech", ".info"]  # ".tt",".code", ".free" 不支持
    #             # ".cc", ".com",".net",
    tld_list = [".cc", ".com",".net", "is",  "top", "biz", ".ink", ".be", ".to"]
    # tld_list = [".to"]

    for tld in tld_list:
        tld = tld.strip('.')
        valid_domain = f'x.{tld}'
        if tld in ['dev', 'love', 'so']:
            valid_domain = f'my.{tld}'
        invalid_domain = f'he1llx322o31.{tld}'
        ret1, msg1 = is_domain_avaliable(valid_domain)
        time.sleep(5)
        ret2, msg2 = is_domain_avaliable(invalid_domain)
        time.sleep(5)
        if ret1 is None:
            logger.info(f"{valid_domain} error: {msg1}")
        elif not ret1:
            logger.info(f"{valid_domain} ok")
        else:
            logger.info(f"valid_domain not right: {valid_domain}")

        if ret2 is None:
            logger.info(f"{invalid_domain} error: {msg2}")
        elif ret2:
            logger.info(f"{invalid_domain} ok")
        else:
            logger.info(f"invalid_domain not right: {invalid_domain}")