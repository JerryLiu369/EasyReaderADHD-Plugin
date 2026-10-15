"""敏感度扫描：FLOOR × COV × MIN_SENT × sentbudget，E1-E2E + holdout-E2E。
纯渲染（候选与分数预计算一次），零新 Jev 请求。
 cliff  hunting：哪个阈值一动数字就崩，哪个就是过拟合负载点。"""
import copy
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

mvp.CFG = dict(mvp.CFG)
BASE_CFG = copy.deepcopy(mvp.CFG)


def load_data():
    e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
    e1l = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
    hold = json.load(open("eval/holdout.json", encoding="utf-8"))["paras"]
    lll = json.load(open("eval/llm_labels.json", encoding="utf-8"))
    return (e1, e1l, hold, lll)


def precache():
    e1, e1l, hold, lll = load_data()
    E, H = [], []
    for para, lab in zip(e1, e1l):
        text = para["text"]
        segs = mvp.segment_all([text])[0]
        cand = mvp.build_candidates(text, segs)
        uniq = sorted({t for (_, _, t) in cand})
        sc = mvp.score_terms(text, uniq)
        E.append((text, [(s, e, t, sc[t]) for (s, e, t) in cand], lab["keys"]))
    for p, lab in zip(hold, lll):
        text = p["text"]
        segs = mvp.segment_all([text])[0]
        cand = mvp.build_candidates(text, segs)
        uniq = sorted({t for (_, _, t) in cand})
        sc = mvp.score_terms(text, uniq)
        H.append((text, [(s, e, t, sc[t]) for (s, e, t) in cand], lab["keys"]))
    return E, H


def match(a, b):
    a = a.replace(" ", "").replace("　", "")
    b = b.replace(" ", "").replace("　", "")
    return a == b or a in b or b in a


def e2e(dataset):
    th, tk = 0, 0
    for text, scores, keys in dataset:
        html, _, _ = mvp.render_para(text, scores)
        picked = re.findall(r"<strong>(.*?)</strong>", html)
        for k in keys:
            tk += 1
            th += any(match(k, p) for p in picked)
    return th, tk


if __name__ == "__main__":
    E, H = precache()
    print(f"precached E1={len(E)} holdout={len(H)} reqs={mvp.usage()['requests']}")
    base_cov, base_floor, base_ms = mvp.COV_TARGET, mvp.SCORE_FLOOR, mvp.MIN_SENT_CONTENT
    rows = []
    for floor in [0.15, 0.20, 0.25, 0.30, 0.35]:
        for cov in [0.10, 0.12, 0.14]:
            for ms in [6, 8, 12]:
                mvp.SCORE_FLOOR, mvp.COV_TARGET, mvp.MIN_SENT_CONTENT = floor, cov, ms
                mvp.CFG = dict(BASE_CFG)
                eh, ek = e2e(E)
                hh, hk = e2e(H)
                rows.append((floor, cov, ms, eh / ek, hh / hk))
                print(f"floor={floor} cov={cov} ms={ms}: E1={eh}/{ek}={eh/ek:.3f} hold={hh}/{hk}={hh/hk:.3f}")
    for sb in [True, False]:
        mvp.SCORE_FLOOR, mvp.COV_TARGET, mvp.MIN_SENT_CONTENT = base_floor, base_cov, base_ms
        mvp.CFG = dict(BASE_CFG)
        mvp.CFG["use_sentbudget"] = sb
        eh, ek = e2e(E)
        hh, hk = e2e(H)
        print(f"sentbudget={sb}: E1={eh}/{ek}={eh/ek:.3f} hold={hh}/{hk}={hh/hk:.3f}")
    mvp.SCORE_FLOOR, mvp.COV_TARGET, mvp.MIN_SENT_CONTENT = base_floor, base_cov, base_ms
    mvp.CFG = dict(BASE_CFG)
    print("restored.")
