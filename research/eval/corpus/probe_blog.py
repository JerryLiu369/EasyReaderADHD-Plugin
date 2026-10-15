"""探：新浪博客（前大模型时代中文博客代表）可抓性。"""
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


for name, home in [
    ("hanhan", "http://blog.sina.com.cn/twocold"),
    ("wangxiaofeng", "http://blog.sina.com.cn/wangxiaofeng"),
    ("hecaitou", "http://blog.sina.com.cn/hecaitou"),
]:
    try:
        h = get(home)
        links = sorted(set(re.findall(r"(blog_\w{16}\.html)", h)))
        print(f"[{name}] len={len(h)} postlinks={len(links)} {links[:5]}")
    except Exception as e:  # noqa: BLE001
        print(f"[{name}] FAIL {str(e)[:150]}")
