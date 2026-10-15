import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


h = get("https://www.guancha.cn/")
pats = sorted(set(re.findall(r'href="([^"]*?/[^"]*?\.shtml)"', h)))
print("guancha shtml links:", len(pats))
for p in pats[:12]:
    print("  ", p)

a = get("https://www.jiemian.com/article/13163796.html")
print("[jiemian] len=", len(a), "p=", len(re.findall(r"<p[ >]", a)))
for m in ["article-content", "article_content", "__NEXT_DATA__", "content-body", "article-body"]:
    print("  ", m, a.count(m))

r = get("https://book.douban.com/review/17852978/")
print("[douban] len=", len(r), "p=", len(re.findall(r"<p[ >]", r)))
for m in ["review-content", "review_content", "main-bd", "review-bd"]:
    print("  ", m, r.count(m))
