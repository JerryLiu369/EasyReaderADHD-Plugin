"""C-choice 放量测试：30 个 option/题，真随机词做填充干扰项，看 keys 是否还在顶部。"""
import json
import random
import sys

sys.path.insert(0, "eval")
from mvp import call_jev, segment_all, is_content

E1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
LAB = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
random.seed(7)

for i in [2, 18]:
    text = E1[i]["text"]
    lab = LAB[i]
    keys = list(lab["keys"])
    # 填充：段内 content 词去重后随机取 20 个，排除已标词（含子串 relations 也算命中 key）
    segs = [s["text"] for s in segment_all([text])[0] if is_content({"text": s["text"]})]
    pool = sorted({s for s in segs if len(s) > 1 and not any(s in k or k in s for k in keys)})
    fill = random.sample(pool, min(20, len(pool)))
    terms = [(t, 1) for t in keys] + [(t, 0) for t in lab["distractors"] + fill]
    print(f"E1-{i:02d} options={len(terms)} fill={fill}")
    qs = {"rank": {"type": "choice",
                   "instructions": "Which term is most essential to this paragraph's main point?",
                   "criteria": {t: None for (t, _) in terms}}}
    raw, ms = call_jev(text, qs)
    probs = raw["answers"]["rank"]["probabilities"]
    ranked = sorted([(t, lb, probs[t]) for (t, lb) in terms], key=lambda r: -r[2])
    nk = len(keys)
    p_at_k = sum(lb for _, lb, _ in ranked[:nk]) / nk
    print(f"  P@K={p_at_k:.2f} conf={raw['answers']['rank'].get('confidence')} toks={raw.get('usage')}")
    for t, lb, p in ranked[:10]:
        print(f"    {p:.3f} [{'K' if lb else ' '}] {t}")
