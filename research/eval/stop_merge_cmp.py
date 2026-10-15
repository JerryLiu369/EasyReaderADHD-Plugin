"""合并规则候选的比较（不含渲染门，先做静态误伤面分析）：
变体：all4 / any2 / hit-only / union
用途分两类：
  EXACT：候选整词命中即丢（所有条目）。
  HALF ：双字半边规则用（只取"功能词"性质的受害者）。
本脚本度量：各变体在 HALF 用途下，会吃掉多少标注词（keys）与多少渲染锚（以旧 hand 基线为参照）；
以及各变体 HALF 词集里有几个单字。结果落 stop_merge_cmp.txt。
"""
import io
import json

L = {n: set(l.strip() for l in open(f"eval/stopwords/{n}.txt", encoding="utf-8") if l.strip())
     for n in ["hit_stopwords", "baidu_stopwords", "cn_stopwords", "scu_stopwords"]}
OUT = io.StringIO()


def P(*a):
    OUT.write(" ".join(str(x) for x in a) + "\n")


union = set().union(*L.values())
all4 = set.intersection(*L.values())

from collections import Counter

cnt = Counter()
for s in L.values():
    for w in s:
        cnt[w] += 1
any2 = {w for w, c in cnt.items() if c >= 2}
any3 = {w for w, c in cnt.items() if c >= 3}

e1l = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
hl = json.load(open("eval/llm_labels.json", encoding="utf-8"))
kys = [k for lab in e1l for k in lab["keys"]] + [k for lab in hl for k in lab["keys"]]

for name, s in [("all4", all4), ("any3", any3), ("any2", any2), ("union", union), ("hit", L["hit_stopwords"])]:
    singles = {w for w in s if len(w) == 1}
    # 标注词风险：整词命中
    exact_hit = [k for k in kys if k in s]
    # 半边风险：key 含"HALF词集任一 2 字词"（近似：含任一 【多字条目】 作为子串，或含单字）
    risk_multi = [k for k in kys if len(k) >= 2 and any(w in k for w in s if len(w) >= 2)]
    risk1 = [k for k in kys if len(k) >= 2 and any(ch in k for ch in singles)]
    P(f"{name}: size={len(s)} singles={len(singles)}")
    P(f"   exact命中标注词: {len(exact_hit)} {exact_hit[:12]}")
    P(f"   多字内嵌命中: {len(risk_multi)} {sorted(set(risk_multi))[:12]}")
    P(f"   含单字命中: {len(risk1)}")
    P(f"   单字样例: {''.join(sorted(singles))[:80]}")

open("eval/stop_merge_cmp.txt", "w", encoding="utf-8").write(OUT.getvalue())
print("wrote eval/stop_merge_cmp.txt")
