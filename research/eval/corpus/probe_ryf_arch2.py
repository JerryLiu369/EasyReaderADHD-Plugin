import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

arch = get("https://www.ruanyifeng.com/blog/archives.html")
print("len:", len(arch))
links = re.findall(r'href="([^"]+)"', arch)
blog_links = [l for l in links if '/blog/' in l and '.html' in l]
print("blog_links count:", len(blog_links))
for l in blog_links[10:20]:
    print("  ", l)
