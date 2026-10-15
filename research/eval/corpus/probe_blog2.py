import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


try:
    h = get("http://blog.sina.com.cn/lianyue")
    links = sorted(set(re.findall(r"(blog_\w{16}\.html)", h)))
    print("[lianyue] len=", len(h), "links=", len(links), links[:5])
except Exception as e:  # noqa: BLE001
    print("[lianyue] FAIL", str(e)[:150])

for pid in ["blog_4701280b0102eb6w.html", "blog_4701280b0102ec39.html", "blog_53f02cd2010003t1.html"]:
    try:
        author = "twocold" if "4701280b" in pid else "hecaitou"
        h = get(f"http://blog.sina.com.cn/s/{pid}")
        t = re.search(r"<title>(.*?)</title>", h, re.S)
        d = re.search(r"(\d{4}-\d{2}-\d{2})", h)
        print(pid, "|", strip(t.group(1))[:40] if t else "?", "|", d.group(1) if d else "?",
              "| p:", len(re.findall(r"<p[ >]", h)))
    except Exception as e:  # noqa: BLE001
        print(pid, "FAIL", str(e)[:150])
