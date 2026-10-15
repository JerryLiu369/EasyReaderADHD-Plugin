"""抽 8 段做人工对齐集：print 全文供精读打标。"""
import json

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}


def find(cid, needle):
    c = by_id[cid]
    for i, p in enumerate(c["paras"]):
        if needle in p:
            return c, i, p
    raise SystemExit(f"not found {needle}")


wants = [
    ("cssn-2022", "肯尼思·华尔兹"),
    ("cssn-2022", "人造卫星的设计"),
    ("cssn-2022", "哈里·怀特"),
    ("thepaper-7963367", "查尔斯·蒂利"),
    ("thepaper-7963367", "求异法比求同法"),
    ("13163796", "潜规则”是指严格意义"),
    ("/ZhengZhi/2026_10_11_903878.shtml", "黄精五黑粉"),
    ("114821", "全美达"),
]
sel = []
for k, (cid, needle) in enumerate(wants):
    c, i, p = find(cid, needle)
    sel.append({"job": f"M{k}", "article": c["id"], "idx": i, "text": p})
    print(f"===== M{k} [{c['source']}/{c['id']}#{i}] len={len(p)} =====")
    print(p)
    print()
json.dump(sel, open("eval/mylabels_set.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
