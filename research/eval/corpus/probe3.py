import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


g = get("https://www.guancha.cn/politics/2026_10_11_903800.shtml")
print("[guancha] len=", len(g))
i = g.find("all-txt")
print("   all-txt at", i)
if i > 0:
    seg = g[i : i + 3000]
    ps = [strip(p) for p in re.findall(r"<p>(.*?)</p>", seg, re.S)]
    print("   paras in seg:", len(ps), "chars:", sum(len(p) for p in ps))

j = get("https://www.jiemian.com/article/13163796.html")
i = j.find("article-content")
seg = j[i : i + 200000]
ps = [strip(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", seg, re.S)]
ps = [p for p in ps if len(p) >= 40]
print("[jiemian] paras:", len(ps), "chars:", sum(len(p) for p in ps))

r = get("https://book.douban.com/review/17852978/")
i = r.find("review-content")
seg = r[i : i + 100000] if i > 0 else r
print("[douban] review-content chars:", len(seg) if i > 0 else -1)
