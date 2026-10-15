import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

# 看看 mindhacks.cn
try:
    mh = get("http://mindhacks.cn/")
    links = re.findall(r'href="(http://mindhacks.cn/\d{4}/\d{2}/\d{2}/[^"]+)"', mh)
    print("mindhacks links:", len(links), links[:3])
except Exception as e:
    print("mindhacks fail:", e)

# 看看阮一峰博客首页
try:
    ryf = get("https://www.ruanyifeng.com/blog/")
    links = re.findall(r'href="(https://www.ruanyifeng.com/blog/\d{4}/\d{2}/[^"]+)"', ryf)
    print("ryf links:", len(links), links[:3])
except Exception as e:
    print("ryf fail:", e)
