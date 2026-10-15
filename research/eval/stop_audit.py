"""STOP 逐条审计：关 STOP 全量重渲染（E1+holdout+multi），数每条目“救了几次”
（无 STOP 时被 picked 的次数）。0 次的条目 = 死重（从未开火），候选删除。
新增 Jev 请求：复活词补分（一次性）。"""
import copy
import json
import re
import sys
from collections import Counter

sys.path.insert(0, "eval")
import mvp

entries = sorted(mvp.STOP)
print(f"STOP entries: {len(entries)}")

mvp.CFG = dict(mvp.CFG)
mvp.CFG["use_stop"] = False

e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
hold = json.load(open("eval/holdout.json", encoding="utf-8"))["paras"]
corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}
multi_ids = ["115568", "114821", "13163796", "/ZhengZhi/2026_10_11_903878.shtml",
             "17852957", "cssn-2022", "thepaper-7963367"]


def paras_of(cid, limit=None):
    ps = by_id[cid]["paras"]
    ps = [p for p in ps if sum(1 for ch in p if "\u4e00" <= ch <= "\u9fff") >= 15]
    return ps[:limit] if limit else ps


texts = ([p["text"] for p in e1] + [p["text"] for p in hold] +
         [p for cid in multi_ids for p in paras_of(cid, 12 if by_id[cid]["source"] == "douban" else None)])
print(f"paras: {len(texts)}")


def render_all():
    out = []
    seg_lists = []
    B = 12
    for bi in range(0, len(texts), B):
        seg_lists.extend(mvp.segment_all(texts[bi:bi + B]))
    for text, seg_list in zip(texts, seg_lists):
        cand = mvp.build_candidates(text, seg_list)
        uniq = sorted({t for (_, _, t) in cand})
        sc = mvp.score_terms(text, uniq)
        html, _, _ = mvp.render_para(text, [(s, e, t, sc[t]) for (s, e, t) in cand])
        out.append(re.findall(r"<strong>(.*?)</strong>", html))
    return out


picked_all = render_all()
saves = Counter()
for picked in picked_all:
    for s in picked:
        for e in entries:
            if s == e or e in s:
                saves[e] += 1
                break
print(f"total picked spans: {sum(len(p) for p in picked_all)} reqs={mvp.usage()['requests']}")
zero = [e for e in entries if saves[e] == 0]
print(f"ZERO-save entries ({len(zero)}): {zero}")
print("top saves:", saves.most_common(25))
json.dump({"saves": dict(saves), "zero": zero},
          open("eval/stop_audit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote eval/stop_audit.json")
