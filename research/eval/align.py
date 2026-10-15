"""对齐基线：我的标 vs 当前 wording（走缓存，0 新请求）。"""
import json
import sys

sys.path.insert(0, "eval")
import mvp

mset = {m["job"]: m for m in json.load(open("eval/mylabels_set.json", encoding="utf-8"))}
mine = {m["job"]: m for m in json.load(open("eval/mylabels.json", encoding="utf-8"))}
cache = mvp.load_cache()


def jev_score(state, term):
    return cache.get(mvp.cache_key(state, term))


for job in sorted(mset):
    text = mset[job]["text"]
    segs = mvp.segment_all([text])[0]
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    scored = sorted(
        [(t, jev_score(text, t)) for t in uniq if jev_score(text, t) is not None],
        key=lambda r: -r[1],
    )
    rank_of = {t: i + 1 for i, (t, _) in enumerate(scored)}
    print(f"===== {job} len={len(text)} cand={len(uniq)} scored={len(scored)} =====")
    hits, ranks = 0, []
    for k in mine[job]["keys"]:
        # 映射：exact > 包含（取分最高的重叠候选）
        cands = [t for t in rank_of if t == k or k in t or t in k]
        if not cands:
            print(f"  MISS(no cand) {k!r}")
            continue
        best = max(cands, key=lambda t: scored[rank_of[t] - 1][1])
        r = rank_of[best]
        ranks.append(r)
        mark = "OK " if r <= max(3, len(mine[job]["keys"])) else "LOW"
        print(f"  [{mark}] rank={r:3d} jev={scored[r-1][1]:.2f} mine={k!r} -> {best!r}")
    print(f"  mean rank={sum(ranks)/len(ranks):.1f} n={len(ranks)}/{len(mine[job]['keys'])}")
