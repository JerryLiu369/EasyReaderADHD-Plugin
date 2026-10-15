"""合并阈值对比：all4 / any3 / any2 三个候选合并规则，各跑 E1+holdout 渲染门 + multi junk 计数。
纯分析：候选/分数走缓存；若新词触发请求会记账。结果落 stop_merge_gates.txt。"""
import io
import json
import re
import sys
from collections import Counter

sys.path.insert(0, "eval")
import mvp

OUT = io.StringIO()


def P(*a):
    OUT.write(" ".join(str(x) for x in a) + "\n")


NAMES = ["hit_stopwords", "baidu_stopwords", "cn_stopwords", "scu_stopwords"]
L = {n: set(l.strip() for l in open(f"eval/stopwords/{n}.txt", encoding="utf-8") if l.strip())
     for n in NAMES}
cnt = Counter()
for s in L.values():
    for w in s:
        cnt[w] += 1

VARIANTS = {
    "all4": {w for w, c in cnt.items() if c == 4},
    "any3": {w for w, c in cnt.items() if c >= 3},
    "any2": {w for w, c in cnt.items() if c >= 2},
}

e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
e1l = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
hold = [x["text"] for x in json.load(open("eval/holdout.json", encoding="utf-8"))["paras"]]
hl = json.load(open("eval/llm_labels.json", encoding="utf-8"))
corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}
multi_ids = ["115568", "114821", "13163796", "/ZhengZhi/2026_10_11_903878.shtml",
             "17852957", "cssn-2022", "thepaper-7963367"]


def paras_of(cid, limit=None):
    ps = [p for p in by_id[cid]["paras"] if sum(1 for ch in p if "\u4e00" <= ch <= "\u9fff") >= 15]
    return ps[:limit] if limit else ps


multi_texts = [p for cid in multi_ids for p in paras_of(cid, 12 if by_id[cid]["source"] == "douban" else None)]


def match(a, b):
    a = a.replace(" ", "").replace("　", "")
    b = b.replace(" ", "").replace("　", "")
    return a == b or a in b or b in a


def set_stop(stop):
    mvp.STOP = stop
    mvp.STOP_MULTI = {w for w in stop if len(w) >= 2}
    mvp.STOP_SINGLE_CONSENSUS = {w for w in stop if len(w) == 1}


def renders(texts, batch=12):
    out = []
    segs_all = []
    for i in range(0, len(texts), batch):
        segs_all.extend(mvp.segment_all(texts[i:i + batch]))
    for idx, (text, segs) in enumerate(zip(texts, segs_all)):
        try:
            cand = mvp.build_candidates(text, segs)
        except Exception as e:
            P(f"BUILD FAIL idx={idx} {type(e).__name__}: {e}")
            P(f"  text={text[:60]!r}")
            P(f"  segs[0:3]={segs[:3]}")
            raise
        uniq = sorted({t for (_, _, t) in cand})
        sc = mvp.score_terms(text, uniq)
        html, _, _ = mvp.render_para(text, [(s, e, t, sc[t]) for (s, e, t) in cand])
        out.append(re.findall(r"<strong>(.*?)</strong>", html))
    return out


JUNK = re.compile("为什么|相比于|但是|不是|没有|无法|不要|是否|如何|什么|怎么|它们|我们|你们|他们|这些|那些|这个|那个|这里|那里|或者|以及|最多|最少|他人|自己")

for name, stop in VARIANTS.items():
    set_stop(stop)
    re1 = renders([x["text"] for x in e1])
    rh = renders(hold)
    rm = renders(multi_texts)
    eh = sum(1 for picked, lab in zip(re1, e1l) for k in lab["keys"] if any(match(k, p) for p in picked))
    ek = sum(len(lab["keys"]) for lab in e1l)
    hh = sum(1 for picked, lab in zip(rh, hl) for k in lab["keys"] if any(match(k, p) for p in picked))
    hk = sum(len(lab["keys"]) for lab in hl)
    sp = [s for picked in rm for s in picked]
    junk = [s for s in sp if s in stop or JUNK.search(s)]
    P(f"[{name}] size={len(stop)} multi={len(mvp.STOP_MULTI)} "
      f"E1={eh}/{ek}={eh/ek:.3f} hold={hh}/{hk}={hh/hk:.3f} "
      f"multi strongs={len(sp)} junk={len(junk)}")
    P(f"   junk样例: {sorted(set(junk))[:12]}")
    P(f"   单字样例: {''.join(sorted(w for w in stop if len(w)==1))[:70]}")

P(f"reqs={mvp.usage()['requests']}")
open("eval/stop_merge_gates.txt", "w", encoding="utf-8").write(OUT.getvalue())
print("wrote eval/stop_merge_gates.txt")
