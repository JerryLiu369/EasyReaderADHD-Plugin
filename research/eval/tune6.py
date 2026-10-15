"""role-choice 实验：Jev 不再直出重要性，改为输出每个词的语义角色（choice 6 类），
选择逻辑全放代码里（权重可调免费、可审计）。与 v3（P@K 0.929）在 E1-20 上同场对比。
约 20 请求。
"""
import json
import sys

sys.path.insert(0, "eval")
import mvp

ROLES = {
    "entity": "人名、地名、机构名、作品名等专名实体",
    "term": "术语、概念、理论名、方案名",
    "action": "承载关键动作的动词性成分",
    "evidence": "数字、时间、例证、引文等证据性成分",
    "topic": "一般话题词，删掉不影响具体理解",
    "filler": "虚词、语气词、连接成分、套话",
}


def mk_qr(term):
    return {"type": "choice",
            "instructions": {
                "target": term,
                "question": "What role does `target` play in this paragraph?",
            },
            "criteria": ROLES}


def main():
    e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
    labels = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
    pks, details = [], []
    for i, (para, lab) in enumerate(zip(e1, labels)):
        terms = [(t, 1) for t in lab["keys"]] + [(t, 0) for t in lab["distractors"]]
        qs = {f"q{j}": mk_qr(t) for j, (t, _) in enumerate(terms)}
        raw, ms = mvp.call_jev(para["text"], qs)
        ans = raw["answers"]
        rows = []
        for j, (t, lb) in enumerate(terms):
            p = ans[f"q{j}"]["probabilities"]
            m1 = 1 - p.get("topic", 0) - p.get("filler", 0)  # 无权重映射
            rows.append((t, lb, m1, max(p, key=p.get)))
        rows.sort(key=lambda r: -r[2])
        nk = len(lab["keys"])
        p_at_k = sum(r[1] for r in rows[:nk]) / nk
        pks.append(p_at_k)
        details.append((i, p_at_k, [(t, lb, round(s, 2), role) for (t, lb, s, role) in rows[:nk]]))
        print(f"E1-{i:02d} P@K={p_at_k:.2f} toks={raw.get('usage', {}).get('input_tokens')}")
    print("ROLE MEAN P@K=%.3f (V3 BASE 0.929)" % (sum(pks) / len(pks)))
    for i, pk, top in details:
        if pk < 1.0:
            print(f"  E1-{i:02d} P@K={pk:.2f} top:", [(t, r) for (t, lb, s, r) in top if not lb])


if __name__ == "__main__":
    main()
