import requests

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
    'whois': 'exampl.io'
}

response = requests.post('http://nic.io/whois.php', 
                        headers=headers, 
                        cookies=cookies, 
                        data=data)
