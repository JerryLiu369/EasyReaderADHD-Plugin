import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


h = get("https://www.guancha.cn/")
pats = sorted(set(re.findall(r'href="((?:/[^"]*?)?/(?:politics|internation|industry|science)/[^"]*?\.shtml)"', h)))
print("channels:", len(pats))
for p in pats[:10]:
    print("  ", p)

url = "https://www.guancha.cn" + pats[0]
g = get(url)
print("[guancha] len=", len(g))
t = re.search(r"<title>(.*?)</title>", g, re.S)
print("   title:", strip(t.group(1))[:60] if t else "?")
for m in ["article-txt", "article_content", "content", "all-txt", "txt"]:
    print("   ", m, g.count(m))
