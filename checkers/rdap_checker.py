import requests
from loguru import logger

rdap_urls = {
        'so': ["https://rdap.nic.so/domain/", 'https://rdap.centralnic.com/so/'],
        'ai': ['https://rdap.whois.ai/domain/', 'https://rdap.nominet.uk/domain/'],
        'io': ['https://nic.io/whois.php'],
        'is': ['https://www.isnic.is/is/whois/search?query='],
        'com': ['https://rdap.verisign.com/com/v1/domain/']
}

def is_io_avaliable(domain_name, rdap_url):
    try:
        # headers = {'Content-Type' : 'application/x-www-form-urlencoded', 'Content-Length' : len(domain_name) + 5}
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'nic.io',
            'Referer': 'nic.io/whois-search.htm?domain_name=exampl.io',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        cookies = {
            '_ga': 'GA1.2.224370403.1735579067',
            '_gid': 'GA1.2.1810104247.1735579067',
            '_gat_gtag_UA_102560287_1': '1',
            'customerName': '',
            'isLogged': 'false'
        }
        data = {
            'whois': domain_name
        }
        response = requests.post(rdap_url, headers=headers, cookies=cookies, data=data, timeout=5)
        if response.status_code == 200:
            rdap_data = response.json()
            if 'Domain not found' in rdap_data['text']:
                return True
        else:
            logger.info(f"Return not right: {response.status_code}, {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.info(f"Error querying RDAP: {e}, domain: {domain_name}")
    return False

def is_is_avaliable(domain_name, rdap_url):
    try:
        proxy =
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get(rdap_url + domain_name, timeout=5)
        if response.status_code != 200:
            logger.info(f"Return status_code not right: {response.text}, domain: {domain_name}")
            return False
        if 'er laust' in response.text:
            return True
        elif 'Skráningarskírteini' in response.text:
            return False
        else:
            ret = 'Maður eða vél' in response.text
            logger.info(f"Return not right, too much query: {ret}, domain: {domain_name}")
    except requests.exceptions.RequestException as e:
        logger.info(f"Error querying RDAP: {e}, domain: {domain_name}")
    return False

def is_domain_avaliable(domain_name):
    """
    判断域名是否可以注册，使用简化 RDAP 响应。
    Returns:
        bool: 如果域名可以注册返回 True，如果已注册返回 False。
    """
    tld = domain_name.split('.')[1]
    if tld not in rdap_urls:
        logger.info(f"No rdap urls found for {tld}")
        return False

    rdap_url = rdap_urls[tld][0]
    try:
        # 添加简化查询参数
        if domain_name.endswith('.io'):
            return is_io_avaliable(domain_name, rdap_url)
        if domain_name.endswith('.is'):
            return is_is_avaliable(domain_name, rdap_url)

        query_url = f"{rdap_url}{domain_name}?fields=status,ldhName"  # 'https://rdap.nic.so/domain/
        response = requests.get(query_url, timeout=10)

        # 如果返回 404，域名可以注册
        if response.status_code == 404:
            return True

        # 如果返回 200，检查简化的 JSON 数据
        if response.status_code == 200:
            rdap_data = response.json()
            if "status" in rdap_data or "ldhName" in rdap_data:
                return False  # 已被注册，不能注册
    except requests.exceptions.RequestException as e:
        logger.info(f"Error querying RDAP: {e}, domain: {domain_name}")
        return False  # 如果请求失败，假定域名不可注册（保守策略）

    return False  # 如果没有明确信息，假定域名已注册



# 示例使用
if __name__ == '__main__':
    ret = is_domain_avaliable('test.is')
    logger.info(ret)