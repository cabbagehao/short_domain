import os, time
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from configs import log_config
# from tlds import all_tlds
from common_utils.domain_generator import *
from database.supabase_crud import SupabaseCRUD
# from checkers.rdap_checker import is_domain_avaliable
from checkers.whois_checker import is_domain_avaliable

THREAD_CNT = 1
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

def pbar_log(pbar):
    elapsed_time = time.time() - pbar.start_t
    remaining_tasks = pbar.total - pbar.n
    eta = 1.0 * elapsed_time / pbar.n * remaining_tasks if pbar.n > 0 else 0  # 避免除零

    # 格式化时间
    def format_time(seconds):
        if seconds >= 3600:  # 如果时间大于或等于 1 小时
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            seconds = int(seconds % 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:  # 时间小于 1 小时
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02}:{seconds:02}"
    elapsed_str = format_time(elapsed_time)
    eta_str = format_time(eta)
    return f"{pbar.n}/{pbar.total} ({(pbar.n / pbar.total) * 100:.0f}%), {elapsed_str} < {eta_str}"
class NoOpStream:
    def write(self, _):
        pass
    def flush(self):
        pass
def tld_2_table_name(tld):
    return 'domain_' + tld

def check_with_thread_pool(tld_domains):
    cached_ok_domains = defaultdict(list)
    with ThreadPoolExecutor(max_workers=THREAD_CNT) as executor:
        futures = {}  # 存储 Future 和域名的映射
        with tqdm(desc="Checking domains", total=len(tld_domains) * 49284, file=NoOpStream()) as pbar:
            i = 0
            while tld_domains:
                i %= len(tld_domains)
                tld, domains_gen, tld_table = tld_domains[i]
                try:
                    domain = next(domains_gen)
                except StopIteration:
                    del tld_domains[i]
                    continue
                i = i + 1
                future = executor.submit(is_domain_avaliable, domain)
                futures[future] = (tld, domain, tld_table)

                # 如果达到最大线程数，等待这一批任务都完成
                if len(futures) == THREAD_CNT:
                    for completed_future in as_completed(futures):
                        tld, domain, tld_table = futures.pop(completed_future)
                        try:
                            if completed_future.result()[0]:
                                cached_ok_domains[tld].append({"domain": domain})
                            # 当前available达到100条时，将缓存的域名批量写入数据库。
                            if len(cached_ok_domains[tld]) == 10:
                                db.bulk_upsert(tld_table, cached_ok_domains[tld], 'domain')
                                cached_ok_domains[tld].clear()
                                logger.info(f"Insert new domains into {tld_table}, current domain: {domain}")
                        except Exception as e:
                            logger.info(f"Error checking {domain}: {e}")
                        finally:
                            pbar.update(1)
                            logger.info(f"domain: {domain}, {completed_future.result()[0]}, {pbar_log(pbar)}")
                    time.sleep(10)

            for tld in cached_ok_domains:
                tld_table = tld_2_table_name(tld)
                db.bulk_upsert(tld_table, cached_ok_domains[tld], 'domain')
                cached_ok_domains.clear()
            # 打印总条数。
            # tld_domains_cnt = db.util.count_records(tld_table)
            # logger.info(f"{tld} domains total:  {tld_domains_cnt}")

# 连接数据库
logger.info("Connecting db")
db = SupabaseCRUD(url, key)


def main():
    # 生成domain
    # tld_list = ["ai", "am", "so", "io", "im", ".me", ".ms", "sh", "gg", "org", "app", "dev", "xyz","fun", "dog", "run", ".cool", "love", "blue", "tech", "info"]
    tld_list = [".cc", ".net", "is",  "top", "biz", ".ink", ".be", ".to"]  # ".com"
    tld_list = [x.strip('.') for x in tld_list]
    tld_domains = []
    for tld in tld_list:
        # tld = 'dev'
        tld_table = tld_2_table_name(tld)
        logger.info(f"Generating {tld} domains")
        domains = generate_domains_3(tld)         # 49284
        tld_domains.append([tld, domains, tld_table])

        # 创建tld表
        res = db.table_manager.create_available_tdl_domains_table_if_not_exists(tld_table)
        if res['status'] != 'success':
            logger.warning(res['message'])
            return
    #     db.table_manager.truncate_table(tld_table)
    # return
    logger.info("Checking...")
    check_with_thread_pool(tld_domains)
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
    # logger.info("\nAvailable domains:")
    # for domain in available_domains:
    #     logger.info(domain)