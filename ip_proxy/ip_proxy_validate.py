import requests
import concurrent.futures
import time
import json
import os
from typing import Dict, List, Tuple
from urllib3.exceptions import InsecureRequestWarning
from loguru import logger

class ProxyPool:
    def __init__(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.timeout = 10
        self.max_workers = 50
        self.test_url = 'https://httpbin.org/ip'  # 只保留HTTPS测试
        self.cache_file = 'https_proxies.json'
        self.cache_ttl = 24 * 60 * 60  # 24小时缓存

    def _verify_proxy(self, proxy: str) -> Tuple[bool, str]:
        """验证代理是否支持HTTPS"""
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }

        try:
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=self.timeout,
                verify=False
            )
            return response.status_code == 200, proxy
        except:
            return False, proxy

    def _load_cache(self) -> List[dict]:
        """加载缓存的HTTPS代理"""
        try:
            if not os.path.exists(self.cache_file):
                return []

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # 检查缓存是否过期
            current_time = int(time.time())
            valid_proxies = [
                proxy for proxy in cache_data
                if current_time - proxy['verified_time'] < self.cache_ttl
            ]

            return valid_proxies
        except Exception as e:
            logger.info(f"加载缓存失败: {str(e)}")
            return []

    def _save_cache(self, proxies: List[str]):
        """保存有效的HTTPS代理到缓存"""
        try:
            cache_data = [
                {
                    'proxy': proxy,
                    'verified_time': int(time.time())
                }
                for proxy in proxies
            ]
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.info(f"保存缓存失败: {str(e)}")

    def load_and_verify_proxies(self, file_path: str) -> List[str]:
        """从文件加载并验证代理IP，返回有效的HTTPS代理列表"""
        # 尝试从缓存加载
        cached_proxies = self._load_cache()
        if cached_proxies:
            proxy_list = [proxy['proxy'] for proxy in cached_proxies]
            logger.info(f"从缓存加载了 {len(proxy_list)} 个HTTPS代理")
            return proxy_list

        logger.info("缓存无效或过期，开始重新验证代理...")

        try:
            # 读取代理列表
            with open(file_path, 'r') as f:
                proxy_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            logger.info(f"Error: {file_path} not found!")
            return []

        valid_proxies = []
        total = len(proxy_list)
        logger.info(f"开始验证 {total} 个代理...")

        # 并发验证代理
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {
                executor.submit(self._verify_proxy, proxy): proxy
                for proxy in proxy_list
            }
            completed = 0

            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                is_valid, proxy = future.result()
                if is_valid:
                    valid_proxies.append(proxy)

                # 打印进度
                logger.info(f"\r验证进度: {completed}/{total} ({completed/total*100:.1f}%)", end='')

        logger.info("\n验证完成!")
        logger.info(f"总代理数: {total}")
        logger.info(f"有效HTTPS代理数: {len(valid_proxies)}")
        logger.info(f"有效率: {len(valid_proxies)/total*100:.1f}%")

        # 保存有效代理到缓存
        self._save_cache(valid_proxies)

        return valid_proxies
if __name__ == "__main__":
    proxy_pool = ProxyPool()
    https_proxies = proxy_pool.load_and_verify_proxies("proxy_list.txt")

    logger.info("\n有效的HTTPS代理列表:")
    for proxy in https_proxies:
        logger.info(proxy)