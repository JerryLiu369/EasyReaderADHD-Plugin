import re
import urllib.request
from collections import Counter

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


h = get("https://www.guancha.cn/")
pats = sorted(set(re.findall(r'href="([^"]*?/[^"]*?\.shtml)"', h)))
print("total:", len(pats))
chs = Counter()
for p in pats:
    m = re.search(r"//www\.guancha\.cn/([A-Za-z0-9]+)/", p) or re.search(r"^/([A-Za-z0-9]+)/", p)
    chs[m.group(1) if m else "?"] += 1
print(chs.most_common(25))
