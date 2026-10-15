import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


h = get("http://blog.sina.com.cn/s/blog_4701280b0102ec39.html")
open("eval/corpus/raw/sina_sample.html", "w", encoding="utf-8").write(h[:300000])
print("len:", len(h))
for m in ["sina_keyword_ad_area2", "articalContent", "content", "blog_article", "artical-content"]:
    print("  ", m, h.count(m))
i = h.find("sina_keyword_ad_area2")
print(h[i : i + 1200] if i > 0 else "no ad area")
