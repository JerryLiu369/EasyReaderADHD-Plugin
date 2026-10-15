import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

h = get("http://blog.sina.com.cn/s/articlelist_1191258123_0_1.html")
print("len:", len(h))
links = re.findall(r'href="([^"]+)"', h)
at_links = [l for l in links if 'blog_' in l]
print("blog links count:", len(at_links), at_links[:5])
for l in set(at_links)[:10]:
    # 查找链接附近的文本
    idx = h.find(l)
    print("  ", l, repr(h[idx-30:idx+80]))
