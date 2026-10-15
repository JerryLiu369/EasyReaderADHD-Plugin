"""语料抓取：从真实网站首页找文章链接，抓正文，存 raw HTML + 抽正文。"""
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


if __name__ == "__main__":
    for home, pat in [
        ("https://sspai.com/", r"/post/\d+"),
        ("https://www.guokr.com/", r"/article/\d+/"),
    ]:
        try:
            html = get(home)
            links = sorted(set(re.findall(pat, html)))
            print(home, "links:", len(links), links[:15])
        except Exception as e:  # noqa: BLE001
            print("FAIL", home, str(e)[:200])
