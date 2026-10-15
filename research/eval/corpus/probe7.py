import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


h = get("https://www.guancha.cn/")
pats = sorted(set(re.findall(r'href="(/ZhengZhi/[^"]*?\.shtml)"', h)))
print("zhengzhi:", len(pats), pats[0] if pats else None)
g = get("https://www.guancha.cn" + pats[0])
t = re.search(r"<title>(.*?)</title>", g, re.S)
print("title:", strip(t.group(1))[:60] if t else "?", "len=", len(g))
for m in ["all-txt", "article-txt", 'class="content"', "article_content", "user-main"]:
    print("  ", m, g.count(m))
