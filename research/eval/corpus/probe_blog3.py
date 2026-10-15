import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


# 韩寒首页再取 3 个帖子看日期
h = get("http://blog.sina.com.cn/twocold")
links = sorted(set(re.findall(r"(blog_4701280b\w{8}\.html)", h)))
print("links:", len(links))
for pid in links[5:8]:
    try:
        p = get(f"http://blog.sina.com.cn/s/{pid}")
        t = re.search(r"<title>(.*?)</title>", p, re.S)
        d = re.search(r"(\d{4}-\d{2}-\d{2})", p)
        ndiv = len(re.findall(r"</[Dd][Ii][Vv]>", p))
        print(pid, "|", strip(t.group(1))[:35] if t else "?", "|", d.group(1) if d else "?",
              "| divs:", ndiv)
    except Exception as e:  # noqa: BLE001
        print(pid, "FAIL", str(e)[:120])

# 和菜头独立域名试一次
try:
    w = get("http://www.hecaitou.net/")
    print("[hecaitou.net] len=", len(w))
except Exception as e:  # noqa: BLE001
    print("[hecaitou.net] FAIL", str(e)[:150])
