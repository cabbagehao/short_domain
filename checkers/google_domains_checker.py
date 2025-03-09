from google.cloud import domains_v1
from google.oauth2 import service_account
from datetime import datetime
from loguru import logger

def get_domains_client(credentials_path):
    """
    创建认证客户端
    """
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    return domains_v1.DomainsClient(credentials=credentials)

def search_domains(client, project_id, domain_name):
    try:
        # 构建父级路径
        parent = f'projects/{project_id}/locations/global'

        logger.info(f"\n检查域名: {domain_name}")
        request = domains_v1.SearchDomainsRequest(
            location=parent,
            query=domain_name
        )

        response = client.search_domains(request=request)

        # 处理响应
        for result in response.register_parameters:
            if result.availability:
                price = None
                if hasattr(result, 'yearly_price'):
                    price = f"年费: {result.yearly_price.units}.{result.yearly_price.nanos/10000000} {result.yearly_price.currency_code}"
                logger.info(f"域名可注册: {result.domain_name}, price: {price}")
            else:
                logger.info(f"已注册: {result.domain_name}")

            if hasattr(result, 'notices'):
                logger.info("注意事项:")
                for notice in result.notices:
                    logger.info(f"- {notice}")

    except Exception as e:
        logger.info(f"发生错误: {str(e)}")

def check_domain_status(client, project_id: str, domain_name: str):
    """
    检查域名状态（包括是否已被注册）
    """
    try:
        parent = f'projects/{project_id}/locations/global'

        # 首先使用 search_domains 检查域名状态
        search_request = domains_v1.SearchDomainsRequest(
            location=parent,
            query=domain_name
        )

        search_response = client.search_domains(request=search_request)

        # 如果没有返回结果，说明域名可能已被注册
        if not list(search_response.register_parameters):
            return {
                "domain": domain_name,
                "is_available": False,
                "message": "Domain is already registered or not supported",
                "price": None,
                "currency": None
            }

        # 获取更详细的注册参数
        params_request = domains_v1.RetrieveRegisterParametersRequest(
            location=parent,
            domain_name=domain_name
        )

        params_response = client.retrieve_register_parameters(request=params_request)
        params = params_response.register_parameters

        result = {
            "domain": domain_name,
            "is_available": True,
            "message": "Domain is available for registration",
            "price": None,
            "currency": None,
            "notices": []
        }

        # 获取价格信息
        if hasattr(params, 'yearly_price'):
            price = params.yearly_price
            result["price"] = f"{price.units}.{price.nanos/10000000:.2f}"
            result["currency"] = price.currency_code

        # 获取注意事项
        if hasattr(params, 'notices'):
            result["notices"] = list(params.notices)

        return result

    except Exception as e:
        return {
            "domain": domain_name,
            "is_available": None,
            "message": f"Error checking domain: {str(e)}",
            "price": None,
            "currency": None
        }

if __name__ == "__main__":

    project_id = "river-wave-447307-h8"  # 替换为你的项目ID
    credentials_path = "river-wave-447307-h8-e1c6bc376e0d.json"  # 替换为你的JSON文件路径
    # 创建客户端
    client = get_domains_client(credentials_path)

    # 要查询的域名列表
    domains_to_check = [
        "example.com",
        "example.net",
        "yourdomain.com"
    ]
    tld_list = [".ai", ".am", ".so", ".io", ".im", ".is", ".me", ".ms",
                ".sh", ".gg", ".org", ".biz", ".app",
                ".dev", ".xyz", ".top", ".fun", ".dog", ".run", ".ink", ".cool",
                ".love", ".blue", ".tech", ".info"]  # ".to",".be",".tt",".free",".code",
                # ".cc", ".com",".net",

    for tld in tld_list:
        domain = f'x{tld}'
        if tld in ['dev', 'love', 'so']:
            domain = f'my{tld}'

        # 查询域名可用性
        res = check_domain_status(client, project_id, domain)
        if res['is_available']:
            logger.info(f"domain {domain} is avaliable")
        elif res['is_available'] is None:
            logger.info(f"domain {domain} is error: {res}")
        else:
            logger.info(f"domain {domain} is not avaliable")

        domain = f'he1llx322o31{tld}'
        res = check_domain_status(client, project_id, domain)
        if res['is_available']:
            logger.info(f"domain {domain} is avaliable")
        elif res['is_available'] is None:
            logger.info(f"domain {domain} is error: {res}")
        else:
            logger.info(f"domain {domain} is not avaliable")
