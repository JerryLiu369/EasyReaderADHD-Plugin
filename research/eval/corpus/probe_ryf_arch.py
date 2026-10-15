import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

try:
    arch = get("https://www.ruanyifeng.com/blog/archives.html")
    # 找 2011 或 2012 年的文章
    links = re.findall(r'href="(https://www.ruanyifeng.com/blog/201[12]/\d{2}/[^"]+)"', arch)
    print("ryf 2011-2012 links:", len(links), links[:5])
    if links:
        post = get(links[0])
        print("title:", re.search(r'<title>(.*?)</title>', post).group(1))
        # 提取正文
        m = re.search(r'<div class="asset-body"[^>]*>(.*?)</div>', post, re.S)
        print("asset-body found:", bool(m))
except Exception as e:
    print("arch fail:", e)
