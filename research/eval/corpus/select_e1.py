"""从 corpus.json 选 E1 20 段：3 篇各 7/7/6，长度 120-450 字，尽量叙述性段落。"""
import json

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
e1 = []
plan = [7, 7, 6]
for art, n in zip(corpus, plan):
    cands = [p for p in art["paras"] if 120 <= len(p) <= 450]
    # 均匀抽取，避免全挤在开头
    step = max(1, len(cands) // n)
    sel = cands[::step][:n]
    for p in sel:
        e1.append({"article": art["title"][:20], "url": art["url"], "text": p})

json.dump(e1, open("eval/corpus/e1_set.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for i, e in enumerate(e1):
    print(f"--- E1-{i:02d} [{e['article']}] len={len(e['text'])}")
    print(e["text"][:160])
