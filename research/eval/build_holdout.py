"""Holdout：全新真实文章，不进 corpus.json。2x sspai新帖 + 1x 观察者新文，共20段。"""
import json
import re
import sys
import urllib.request

sys.path.insert(0, "eval/corpus")
from build_corpus import sspai_paras

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
OLD = {"113843", "114821", "115566", "115568"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


items = []
# sspai 新帖
home = get("https://sspai.com/")
ids = [i for i in sorted(set(re.findall(r"/post/(\d+)", home))) if i not in OLD]
print("fresh sspai:", ids)
for aid in ids[:6]:
    try:
        t, ps = sspai_paras(aid)
        print(aid, len(ps), t[:40])
        if len(ps) >= 6:
            items.append({"source": "sspai-holdout", "id": aid, "title": t,
                          "url": f"https://sspai.com/post/{aid}", "paras": ps})
        if sum(len(x["paras"]) for x in items) >= 14:
            break
    except Exception as e:
        print("FAIL", aid, str(e)[:120])

# 观察者新文
h = get("https://www.guancha.cn/")
zz = sorted(set(re.findall(r'href="(/ZhengZhi/[^"]*?\.shtml)"', h)))
print("guancha links:", len(zz))
for link in zz[:10]:
    try:
        g = get("https://www.guancha.cn" + link)
        i = g.find("all-txt")
        seg = g[i:i + 300000] if i >= 0 else g[:300000]
        ps = [p for p in (strip(p) for p in re.findall(r"<p>(.*?)</p>", seg, re.S)) if 80 <= len(p) <= 600]
        m = re.search(r"<title>(.*?)</title>", g, re.S)
        t = strip(m.group(1))[:60] if m else link
        print("guancha", link, len(ps), t[:30])
        if len(ps) >= 6:
            items.append({"source": "guancha-holdout", "id": link, "title": t,
                          "url": "https://www.guancha.cn" + link, "paras": ps})
            break
    except Exception as e:
        print("FAIL guancha", link, str(e)[:120])

# 拼20段：每篇最多8段，保证跨篇
paras = []
for it in items:
    paras.extend([{"doc": it["id"], "title": it["title"], "text": p} for p in it["paras"][:8]])
# 去样板：Matrix社区模板 + 版权行
paras = [p for p in paras if "Matrix 是少数派的写作社区" not in p["text"] and "All rights reserved" not in p["text"]]
# 回填同批未用实段
used = {p["text"] for p in paras}
for it in items:
    for p in it["paras"]:
        if len(paras) >= 20:
            break
        if p not in used and "Matrix 是少数派的写作社区" not in p and "All rights reserved" not in p:
            paras.append({"doc": it["id"], "title": it["title"], "text": p})
            used.add(p)
paras = paras[:20]
json.dump({"items": items, "paras": paras},
          open("eval/holdout.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("docs:", [(x["id"], len(x["paras"])) for x in items], "holdout paras:", len(paras))
