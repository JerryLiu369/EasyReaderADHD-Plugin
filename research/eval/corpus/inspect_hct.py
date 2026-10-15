import urllib.request, re

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

try:
    h = get("http://www.hecaitou.net/")
    titles = re.findall(r'<h[12][^>]*><a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', h)
    print("hecaitou titles:", len(titles))
    for link, t in titles[:8]:
        print("  ", link, t)
except Exception as e:
    print("hecaitou fail:", e)
