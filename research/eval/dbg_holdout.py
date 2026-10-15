"""归因：worst paras 的候选 Rank 前15 + 分数。结果写 dbg_holdout.txt（防控制台乱码）。"""
import io
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp


def main():
    hold = json.load(open("eval/holdout.json", encoding="utf-8"))["paras"]
    labs = json.load(open("eval/llm_labels.json", encoding="utf-8"))
    out = io.StringIO()
    for idx in [1, 4, 6, 17]:
        text = hold[idx]["text"]
        keys = labs[idx]["keys"]
        out.write(f"===== #{idx} TEXT: {text}\n  LLM keys: {keys}\n")
        segs = mvp.segment_all([text])[0]
        out.write(f"  SEGS: {[s['text'] for s in segs]}\n")
        cand = mvp.build_candidates(text, segs)
        uniq = sorted({t for (_, _, t) in cand})
        score_of = mvp.score_terms(text, uniq)
        ranked = sorted(score_of.items(), key=lambda r: -r[1])
        out.write(f"  cand_n={len(uniq)}\n")
        for t, s in ranked[:16]:
            mark = " <==LLM" if any((k in t or t in k) for k in keys) else ""
            out.write(f"    {s:.2f} {t}{mark}\n")
        html, npick, cov = mvp.render_para(
            text, [(s, e, t, score_of[t]) for (s, e, t) in cand])
        out.write(f"  rendered: {re.findall(r'<strong>(.*?)</strong>', html)}\n")
    open("eval/dbg_holdout.txt", "w", encoding="utf-8").write(out.getvalue())
    print("wrote eval/dbg_holdout.txt")


if __name__ == "__main__":
    main()
