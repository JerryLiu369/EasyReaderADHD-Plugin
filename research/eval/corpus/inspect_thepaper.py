import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

h = (
    urllib.request.urlopen(
        urllib.request.Request(
            "https://www.thepaper.cn/newsDetail_forward_34231106", headers=UA
        ),
        timeout=30,
    )
    .read()
    .decode("utf-8", "ignore")
)
print("len:", len(h))
for pat in ["news_txt", "__NEXT_DATA__", "article", "content__", "_params", "newscontent"]:
    print(pat, h.count(pat))
open("eval/corpus/raw/thepaper_sample.html", "w", encoding="utf-8").write(h[:200000])
