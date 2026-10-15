"""下载四公开停用词表原文到 eval/stopwords/（一次性；表更新时重跑）。"""
import os
import urllib.request

BASE = "https://raw.githubusercontent.com/goto456/stopwords/master/"
NAMES = ["hit_stopwords.txt", "baidu_stopwords.txt", "cn_stopwords.txt", "scu_stopwords.txt"]
os.makedirs("eval/stopwords", exist_ok=True)
for name in NAMES:
    raw = urllib.request.urlopen(BASE + name, timeout=60).read().decode("utf-8")
    open(f"eval/stopwords/{name}", "w", encoding="utf-8").write(raw)
    n = len([l for l in raw.splitlines() if l.strip()])
    print(f"saved {name}: {n} nonempty lines")
