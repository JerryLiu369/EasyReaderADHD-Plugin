"""语料修复：文章内整段指纹去重；重抓观察者找“第二”段去哪了。"""
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
for c in corpus:
    seen, out = set(), []
    for p in c["paras"]:
        if p not in seen:
            seen.add(p)
            out.append(p)
    if len(out) != len(c["paras"]):
        print(f"dedup {c['source']}: {len(c['paras'])} -> {len(out)}")
        c["paras"] = out

# 观察者：找第二
gc = [c for c in corpus if c["source"] == "guancha"][0]
g = get(gc["url"])
i = g.find("all-txt")
seg = g[i : i + 300000]
raw_ps = re.findall(r"<p>(.*?)</p>", seg, re.S)
print("guancha raw <p> count:", len(raw_ps))
for p in raw_ps:
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip()
    if "第二" in t[:30] or len(t) < 80:
        print(f"  len={len(t)} {t[:70]}")
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
