"""消融：逐个关规则，看 E2E coverage 与 E1-00/01 粘连。只认数字，不认故事。
新候选会产生少量新请求（已记账）。
"""
import copy
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

BASE = copy.deepcopy(mvp.CFG)
CONFIGS = {
    "full": {},
    "no-stop": {"use_stop": False},
    "no-func": {"use_func": False},
    "no-trigram": {"use_trigram": False},
    "no-runs": {"use_runs": False},
    "no-substr": {"use_substr": False},
    "no-mergecap": {"use_mergecap": False},
    "no-sentbudget": {"use_sentbudget": False},
    "minimal": {"use_stop": False, "use_func": False, "use_trigram": False,
                "use_runs": False, "use_substr": False, "use_mergecap": False,
                "use_sentbudget": False},
}

e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
labels = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))

for name, patch in CONFIGS.items():
    mvp.CFG = dict(BASE)
    mvp.CFG.update(patch)
    th, tk, spans = 0, 0, 0
    picks01 = {}
    for i, (para, lab) in enumerate(zip(e1, labels)):
        text = para["text"]
        segs = mvp.segment_all([text])[0]
        cand = mvp.build_candidates(text, segs)
        uniq = sorted({t for (_, _, t) in cand})
        score_of = mvp.score_terms(text, uniq)
        scores = [(s, e, t, score_of[t]) for (s, e, t) in cand]
        html, npick, cov = mvp.render_para(text, scores)
        picked = re.findall(r"<strong>(.*?)</strong>", html)
        spans += len(picked)
        if i in (0, 1):
            picks01[i] = picked
        for k in lab["keys"]:
            tk += 1
            th += any(k in p or p in k for p in picked)
    print(f"[{name}] coverage={th}/{tk}={th/tk:.3f} spans={spans} reqs={mvp.usage()['requests']}")
    print(f"   E1-00: {picks01[0]}")
    print(f"   E1-01: {picks01[1]}")

mvp.CFG = dict(BASE)
print("CFG restored to full.")
