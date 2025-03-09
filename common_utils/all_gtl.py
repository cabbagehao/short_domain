import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter
from loguru import logger

# Step 1: 抓取 IANA 页面内容
url = "https://www.iana.org/domains/root/db"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: 提取所有顶级域名后缀
tlds = []
for link in soup.select("table tbody tr td:first-child a"):
    tld = link.text.strip()  # 提取域名后缀
    tlds.append(tld)

# Step 3: 统计每个后缀的字符长度（不包括前面的"."）
lengths = [len(tld.lstrip(".")) for tld in tlds]

# Step 4: 统计字符长度分布
length_distribution = Counter(lengths)  # 统计每个长度的出现次数
sorted_distribution = sorted(length_distribution.items())  # 按长度排序

# Step 5: 数据分离（用于绘图）
lengths, counts = zip(*sorted_distribution)

# Step 6: 绘制条形图并保存为图片
plt.figure(figsize=(10, 6))
plt.bar(lengths, counts, color="skyblue", edgecolor="black")
plt.xlabel("域名后缀字符长度", fontsize=12)
plt.ylabel("数量", fontsize=12)
plt.title("顶级域名后缀字符长度分布", fontsize=14)
plt.xticks(lengths)  # 设置 x 轴刻度为字符长度
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# 保存为图片
output_file = "tld_length_distribution.png"  # 输出文件名
plt.savefig(output_file, format="png", dpi=300)  # 指定格式为 PNG，分辨率为 300 DPI
plt.show()

logger.info(f"图表已保存为 {output_file}")