import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger

def get_proxies_from_free_proxy_list():
    proxies = []
    try:
        response = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    if ip and port:
                        proxies.append(f"{ip}:{port}")
    except Exception as e:
        logger.info(f"Error fetching from free-proxy-list.net: {e}")
    return proxies

def get_proxies_from_sslproxies():
    proxies = []
    try:
        response = requests.get('https://www.sslproxies.org/')
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    if ip and port:
                        proxies.append(f"{ip}:{port}")
    except Exception as e:
        logger.info(f"Error fetching from sslproxies.org: {e}")
    return proxies

def get_proxies_from_proxyscrape():
    proxies = []
    try:
        response = requests.get('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all')
        if response.status_code == 200:
            proxy_list = response.text.strip().split('\n')
            proxies.extend([proxy.strip() for proxy in proxy_list if proxy.strip()])
    except Exception as e:
        logger.info(f"Error fetching from proxyscrape.com: {e}")
    return proxies

def save_proxies_to_file(proxies):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = 'proxy_list.txt'

    try:
        with open(filename, 'w') as f:
            f.write(f"# Proxy List generated at {datetime.now()}\n")
            f.write(f"# Total proxies: {len(proxies)}\n\n")
            for proxy in sorted(set(proxies)):  # Remove duplicates and sort
                f.write(f"{proxy}\n")
        logger.info(f"Successfully saved {len(proxies)} proxies to {filename}")
    except Exception as e:
        logger.info(f"Error saving to file: {e}")

def main():
    all_proxies = []

    logger.info("Fetching proxies...")

    # Get proxies from all sources
    proxies1 = get_proxies_from_free_proxy_list()
    logger.info(f"Found {len(proxies1)} proxies from free-proxy-list.net")
    all_proxies.extend(proxies1)

    proxies2 = get_proxies_from_sslproxies()
    logger.info(f"Found {len(proxies2)} proxies from sslproxies.org")
    all_proxies.extend(proxies2)

    proxies3 = get_proxies_from_proxyscrape()
    logger.info(f"Found {len(proxies3)} proxies from proxyscrape.com")
    all_proxies.extend(proxies3)

    # Remove duplicates
    unique_proxies = list(set(all_proxies))
    logger.info(f"\nTotal unique proxies found: {len(unique_proxies)}")

    # Save to file
    save_proxies_to_file(unique_proxies)

if __name__ == "__main__":
    main()