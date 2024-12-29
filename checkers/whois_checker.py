import subprocess

# 使用 WHOIS 检查域名是否注册
# TBD: 需要根据不同的域名后缀使用不同的关键字判断
def whois_check(domain):
    try:
        result = subprocess.run(["whois", domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        if "no match" in output or "not found" in output or "No Object Found" in output:
            return False  # WHOIS 查询结果表明域名未注册
        return True  # WHOIS 查询表明域名已注册
    except Exception as e:
        print(f"WHOIS 查询失败: {e}")
        return False