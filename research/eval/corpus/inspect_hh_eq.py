import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

h = get("http://blog.sina.com.cn/s/blog_4701280b0102egl0.html")
print("len:", len(h))
m = re.search(r'id="sina_keyword_ad_area2"[^>]*>(.*?)</div>\s*<!--', h, re.S)
if m:
    content = m.group(1)
    print("content len:", len(content))
    print(content[:500])
else:
    i = h.find("sina_keyword_ad_area2")
    print(h[i:i+800])
