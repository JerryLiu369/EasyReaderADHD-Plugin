"""wording-v3：在 v2 上只加一条通用粘连约束（动词开头/虚词收尾），无任何语料例子。
E1-20 验证 P@K + E1-00/01 render 看粘连率。直接调，不进缓存。
"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

V3Q = "If a reader had to retell this paragraph's specific points — who, which theory or scheme, what mechanism or evidence — would missing `target` make the retelling vaguer?"
V3T = "A name, theory/scheme label, mechanism, number, or example that carries the argument; removing it loses attribution or specifics"
V3F = (
    "A general topic word, filler, scene-setting, or connective; removing it changes nothing specific. "
    "Also a phrase that begins with a verb or trails off with a particle, conjunction, or demonstrative"
)


def mk_q3(term):
    return {"type": "noul",
            "instructions": {"target": term, "question": V3Q},
            "criteria": {"true": V3T, "false": V3F}}


def main():
    e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
    labels = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
    res = []
    saved = {}
    for i, (para, lab) in enumerate(zip(e1, labels)):
        terms = [(t, 1) for t in lab["keys"]] + [(t, 0) for t in lab["distractors"]]
        qs = {f"q{j}": mk_q3(t) for j, (t, _) in enumerate(terms)}
        raw, ms = mvp.call_jev(para["text"], qs)
        ans = raw["answers"]
        scored = sorted(
            [(t, lb, ans[f"q{j}"]["noul"]) for j, (t, lb) in enumerate(terms)],
            key=lambda r: -r[2],
        )
        nk = len(lab["keys"])
        p_at_k = sum(r[1] for r in scored[:nk]) / nk
        res.append(p_at_k)
        saved[i] = (para["text"], terms, ans)
        print(f"E1-{i:02d} P@K={p_at_k:.2f}")
    print("V3 MEAN P@K=%.3f (V2 BASE 0.922)" % (sum(res) / len(res)))
    # E1-00/01 用 v3 分数 render，看粘连
    for i in [0, 1]:
        text, terms, ans = saved[i]
        segs = mvp.segment_all([text])[0]
        cand = mvp.build_candidates(text, segs)
        smap = {t: ans[f"q{j}"]["noul"] for j, (t, _) in enumerate(terms)}
        scores = [(s, e, t, smap[t]) for (s, e, t) in cand if t in smap]
        html, _, _ = mvp.render_para(text, scores)
        print(f"E1-{i:02d} v3 picks:", re.findall(r"<strong>(.*?)</strong>", html))


if __name__ == "__main__":
    main()
