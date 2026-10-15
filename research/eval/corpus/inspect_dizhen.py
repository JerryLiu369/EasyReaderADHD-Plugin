import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
req = urllib.request.Request(
    "http://blog.sina.com.cn/s/blog_4701280b0102egl0.html", headers=UA
)
h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
i = h.find('id="sina_keyword_ad_area2"')
print(h[i : i + 1000] if i > 0 else "not found")
