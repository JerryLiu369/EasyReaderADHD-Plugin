import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

# 爬取韩寒博客文章目录页
try:
    h = get("http://blog.sina.com.cn/s/articlelist_1191258123_0_1.html")
    # 提取文章列表
    articles = re.findall(r'<a[^>]+href="(http://blog\.sina\.com\.cn/s/blog_[^"]+\.html)">([^<]+)</a>', h)
    print("hh articles page 1:", len(articles))
    for link, title in articles[:10]:
        print("  ", title, link)
except Exception as e:
    print("fail:", e)
