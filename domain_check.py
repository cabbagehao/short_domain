import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# from tlds import all_tlds
from common_utils.domain_generator import generate_domains
from database.supabase_crud import SupabaseCRUD
from checkers.rdap_checker import is_domain_avaliable

THREAD_CNT = 5
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

def main():
    # 生成domain
    ltd = 'so'
    rdap_url = "https://rdap.nic.so/domain/"
    print(f"Generating {ltd} domains")
    domains = generate_domains(ltd, max_len = 3)

    # 连接数据库
    print("Connecting db")
    db = SupabaseCRUD(url, key)
    res = db.table_manager.create_available_tdl_domains_table_if_not_exists(ltd)
    if res['status'] != 'success':
        print(res['message'])
        return

    # 并发执行
    print("Checking...")
    cached_ok_domains = []
    cnt = 0
    with ThreadPoolExecutor(max_workers=THREAD_CNT) as executor:
        futures = {executor.submit(is_domain_avaliable, rdap_url, domain): domain for domain in domains}
        with tqdm(total=len(domains), desc="Checking domains") as pbar:
            for future in as_completed(futures):
                domain = futures[future]
                try:
                    is_available = future.result()
                    if is_available:
                        cached_ok_domains.append({"domain": domain})
                except Exception as e:
                    print(f"Error checking {domain}: {e}")
                finally:
                    pbar.update(1)  # 更新进度条

                # 当前达到1000条，写入一次数据库tld info
                if cnt % 1000 == 0:
                    ltd_info = {
                        'ltd_name': ltd,
                        'last_check_domain': domain
                    }                
                    db.upsert_one('ltd_infos', ltd_info, 'ltd_name')
                    print(f"Insert {ltd} into ltd_infos")
                    # break
                cnt += 1

                # 当前available达到100条时，将缓存的域名批量写入数据库。
                if len(cached_ok_domains) == 100:
                    db.bulk_upsert(ltd, cached_ok_domains, 'domain')
                    cached_ok_domains.clear()
                    print(f"Insert new domains into {ltd}, current domain: {domain}")
            if cached_ok_domains:
                db.bulk_upsert(ltd, cached_ok_domains, 'domain')
                cached_ok_domains.clear()
            # 打印总条数。
            ltd_domains_cnt = db.util.count_records(ltd)
            print(f"{ltd} domains total:  {ltd_domains_cnt}")                
    return

# 主函数
if __name__ == "__main__":
    main()
    # 生成需要检查的域名
    # domains = generate_domains('so')
    # domains += ["example.com", "thisdomainprobablydoesnotexist123456.com"]
    # domains_prefix = ['xxed1299304', 'xxed129933304', 'd0300033d', 'notion', 'hello']
    # domains = []
    # for tld in all_tlds:
    #     for prefix in domains_prefix:
    #         domains.append(prefix + tld)

    # # 执行域名检查
    # available_domains = check_domains(domains, thread_count=30)

    # # 打印未注册的域名
    # print("\nAvailable domains:")
    # for domain in available_domains:
    #     print(domain)