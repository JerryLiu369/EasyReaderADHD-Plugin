import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

h = get("http://blog.sina.com.cn/s/articlelist_1191258123_0_1.html")
# 提取带有 title 属性或者 <a> 包含的链接
matches = re.findall(r'<a[^>]+href="([^"]*blog_4701280b\w+\.html)"[^>]*>(.*?)</a>', h)
print("matches:", len(matches))
for link, text in matches:
    text_clean = re.sub(r'<[^>]+>', '', text).strip()
    if text_clean:
        print("  ", text_clean, link)
