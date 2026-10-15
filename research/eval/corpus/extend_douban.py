"""豆瓣再抓 3 篇书评，stanza 阈值放宽到 50，凑成书评集。"""
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    s = re.sub(r"<[^>]+>", "\n", s)
    return s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
for rid in ["17852957", "17852963", "17852971"]:
    try:
        r = get(f"https://book.douban.com/review/{rid}/")
        i = r.find("review-content")
        stanzas = [s for s in re.split(r"\n+", strip(r[i : i + 100000])) if s.strip()]
        ps = [re.sub(r"\s+", " ", p).strip() for p in stanzas]
        ps = [p for p in ps if 50 <= len(p) <= 600]
        m = re.search(r"<title>(.*?)</title>", r, re.S)
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()[:50]
        print(rid, len(ps), t)
        if ps:
            corpus.append({"source": "douban", "id": rid, "title": t, "url": f"https://book.douban.com/review/{rid}/", "paras": ps})
    except Exception as e:  # noqa: BLE001
        print("FAIL", rid, str(e)[:120])
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n = sum(len(c["paras"]) for c in corpus if c["source"] == "douban")
print("douban total paras:", n, "| articles:", len(corpus))
