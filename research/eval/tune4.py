"""wording-v2 在 E1-20 上的独立验证（E1 人标 ground truth，非我的标）。"""
import json
import sys

sys.path.insert(0, "eval")
import mvp
from tune3 import mk_q2

def main():
    e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
    labels = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
    res = []
    for i, (para, lab) in enumerate(zip(e1, labels)):
        terms = [(t, 1) for t in lab["keys"]] + [(t, 0) for t in lab["distractors"]]
        qs = {f"q{j}": mk_q2(t) for j, (t, _) in enumerate(terms)}
        raw, ms = mvp.call_jev(para["text"], qs)
        scored = sorted(
            [(t, lb, raw["answers"][f"q{j}"]["noul"]) for j, (t, lb) in enumerate(terms)],
            key=lambda r: -r[2],
        )
        nk = len(lab["keys"])
        p_at_k = sum(r[1] for r in scored[:nk]) / nk
        mk = sum(r[2] for r in scored if r[1]) / nk
        md = sum(r[2] for r in scored if not r[1]) / (len(scored) - nk)
        res.append((p_at_k, mk, md))
        print(f"E1-{i:02d} P@K={p_at_k:.2f} key={mk:.2f} dis={md:.2f}")
    n = len(res)
    print("V2 MEAN P@K=%.3f key=%.3f dis=%.3f" % (
        sum(r[0] for r in res) / n, sum(r[1] for r in res) / n, sum(r[2] for r in res) / n))
    print("V1 BASE P@K=0.881 key=0.616 dis=0.269")


if __name__ == "__main__":
    main()
