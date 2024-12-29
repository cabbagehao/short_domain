import requests

def is_domain_avaliable(rdap_url, domain_name):
    """
    判断域名是否可以注册，使用简化 RDAP 响应。
    Returns:
        bool: 如果域名可以注册返回 True，如果已注册返回 False。
    """
    try:
        # 添加简化查询参数
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
        print(f"Error querying RDAP: {e}")
        return False  # 如果请求失败，假定域名不可注册（保守策略）

    return False  # 如果没有明确信息，假定域名已注册



# 示例使用
if __name__ == '__main__':
    rdap_url = "https://rdap.nic.so/domain/"

    from domain_generator import generate_domains
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed

    domains = generate_domains('so')
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(is_domain_avaliable, rdap_url, domain): domain for domain in domains}
        with tqdm(total=len(domains), desc="Checking domains") as pbar:
            for future in as_completed(futures):
                domain = futures[future]
                try:
                    is_avaliable = future.result()
                    if is_avaliable:
                        print(f"{domain} is avaliable.")
                    else:
                        print(f"{domain} registed.")
                except Exception as e:
                    print(f"Error checking {domain}: {e}")
                finally:
                    pbar.update(1)  # 更新进度条
    # for domain_name in tqdm(domains):
    #     if is_domain_avaliable(rdap_url, domain_name):
    #         print(f"The domain '{domain_name}' is available for registration.")
    #     else:
    #         print(f"The domain '{domain_name}' is already registered.")