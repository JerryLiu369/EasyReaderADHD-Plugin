import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


r = get("https://book.douban.com/review/17852978/")
i = r.find("review-content")
seg = r[i : i + 8000]
print(seg[:1500])
print("...")
print("p tags:", len(re.findall(r"<p", seg)), "| br:", seg.count("<br"), "| div:", seg.count("<div"))
open("eval/corpus/raw/douban_sample.html", "w", encoding="utf-8").write(r)
