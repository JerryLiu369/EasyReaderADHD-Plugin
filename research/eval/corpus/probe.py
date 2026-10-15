"""探：各站抓取可行性。首页找文章链接 → 抓一篇 → 报 <p> 段数。"""
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def show(name, url, linkpat=None):
    try:
        h = get(url)
        title = re.search(r"<title>(.*?)</title>", h, re.S)
        n_p = len(re.findall(r"<p[ >]", h))
        print(f"[{name}] len={len(h)} p={n_p} title={(title.group(1)[:45] if title else '?')}")
        if linkpat:
            links = sorted(set(re.findall(linkpat, h)))
            print(f"   links: {len(links)} {links[:8]}")
    except Exception as e:  # noqa: BLE001
        print(f"[{name}] FAIL {str(e)[:150]}")


if __name__ == "__main__":
    show("guancha-home", "https://www.guancha.cn/", r"/politics/\d+_\d+_\d+\.shtml")
    show("jiemian-home", "https://www.jiemian.com/", r"/article/\d+\.html")
    show("dxy-home", "https://www.dxy.cn/", r"/bbs/newweb/pc/post/\d+")
    show("douban-review", "https://book.douban.com/review/latest/", r"/review/\d+/")
