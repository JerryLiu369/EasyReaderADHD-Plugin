import re
import urllib.request
from collections import Counter

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


h = get("https://www.guancha.cn/")
pats = sorted(set(re.findall(r'href="((?:/[^"]*?)?/([A-Za-z0-9]+)/\d+_\d+_\d+\.shtml)"', h)))
print(Counter(ch for _, ch in pats).most_common(20))

# 找一篇时政/国际向的：优先含 politics/internation，否则取最长的那篇试
cands = [p for p, _ in pats if "/Video" not in p and "/Live" not in p][:6]
for p in cands:
    try:
        g = get("https://www.guancha.cn" + p)
        t = re.search(r"<title>(.*?)</title>", g, re.S)
        print(p, "len=", len(g), strip(t.group(1))[:55] if t else "?")
    except Exception as e:  # noqa: BLE001
        print(p, "FAIL", str(e)[:100])
