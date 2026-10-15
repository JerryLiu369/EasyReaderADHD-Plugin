import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

h = get("http://www.hecaitou.net/")
links = re.findall(r'href="([^"]+)"', h)
posts = [l for l in set(links) if re.search(r'/\d{4}/\d{2}/', l) or 'p=' in l or re.search(r'/\d+\.html', l)]
print("post links:", len(posts), posts[:5])
if not posts:
    print("all links snippet:", links[:20])
