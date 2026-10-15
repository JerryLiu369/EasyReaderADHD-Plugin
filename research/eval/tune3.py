"""wording-v2：从“主旨”转向“转述 specificity”（归属+标签+例证），与我的标对齐。
同一 8 段 × 同一候选集，直接调 Jev（约 25 请求，不进缓存）。
"""
import json
import sys

sys.path.insert(0, "eval")
import mvp

mset = {m["job"]: m for m in json.load(open("eval/mylabels_set.json", encoding="utf-8"))}
mine = {m["job"]: m for m in json.load(open("eval/mylabels.json", encoding="utf-8"))}


def mk_q2(term):
    return {
        "type": "noul",
        "instructions": {
            "target": term,
            "question": "If a reader had to retell this paragraph's specific points — who, which theory or scheme, what mechanism or evidence — would missing `target` make the retelling vaguer?",
        },
        "criteria": {
            "true": "A name, theory/scheme label, mechanism, number, or example that carries the argument; removing it loses attribution or specifics",
            "false": "A general topic word, filler, scene-setting, or connective; removing it changes nothing specific",
        },
    }


def main():
    for job in sorted(mset):
        text = mset[job]["text"]
        segs = mvp.segment_all([text])[0]
        cand = mvp.build_candidates(text, segs)
        uniq = sorted({t for (_, _, t) in cand})
        score_of = {}
        for bi in range(0, len(uniq), mvp.MAX_Q_PER_REQ):
            batch = uniq[bi : bi + mvp.MAX_Q_PER_REQ]
            qs = {f"q{j}": mk_q2(t) for j, t in enumerate(batch)}
            raw, ms = mvp.call_jev(text, qs)
            for j, t in enumerate(batch):
                score_of[t] = raw["answers"][f"q{j}"]["noul"]
        scored = sorted(score_of.items(), key=lambda r: -r[1])
        rank_of = {t: i + 1 for i, (t, _) in enumerate(scored)}
        print(f"===== {job} cand={len(uniq)} =====")
        ranks = []
        for k in mine[job]["keys"]:
            cands = [t for t in rank_of if t == k or k in t or t in k]
            if not cands:
                print(f"  MISS(no cand) {k!r}")
                continue
            best = max(cands, key=lambda t: score_of[t])
            r = rank_of[best]
            ranks.append(r)
            print(f"  rank={r:3d} jev={score_of[best]:.2f} mine={k!r} -> {best!r}")
        print(f"  mean rank={sum(ranks)/len(ranks):.1f}")


if __name__ == "__main__":
    main()
