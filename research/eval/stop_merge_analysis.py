"""四表合并前分析：重叠、单字条目、对专业词表（E1/holdout 标注）的命中面。
判定合并规则用。结果落 stop_merge_analysis.txt（UTF-8）。"""
import io
import json

LISTS = {}
for name in ["hit_stopwords", "baidu_stopwords", "cn_stopwords", "scu_stopwords"]:
    LISTS[name] = set(l.strip() for l in open(f"eval/stopwords/{name}.txt", encoding="utf-8")
                      if l.strip())

OUT = io.StringIO()


def P(*a):
    OUT.write(" ".join(str(x) for x in a) + "\n")


for name, s in LISTS.items():
    singles = [w for w in s if len(w) == 1]
    P(f"{name}: total={len(s)} singles={len(singles)} ({''.join(sorted(singles))[:60]})")

union = set().union(*LISTS.values())
inter = set.intersection(*LISTS.values())
P(f"union={len(union)} intersection4={len(inter)}")

from collections import Counter

cnt = Counter()
for s in LISTS.values():
    for w in s:
        cnt[w] += 1
tier = Counter(cnt.values())
P("出现于 n 个表的词数:", dict(sorted(tier.items())))

# 对标注词的命中：整词命中
e1l = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
hl = json.load(open("eval/llm_labels.json", encoding="utf-8"))
kys = [k for lab in e1l for k in lab["keys"]] + [k for lab in hl for k in lab["keys"]]
hit_exact = sorted({k for k in kys if k in union})
P(f"标注词整词命中 union: {hit_exact}")

# 单字拆解命中：key 是否可被切出单字停用词（模拟半边规则的风险面）
singles = {w for w in union if len(w) == 1}
risky = []
for k in kys:
    if len(k) >= 2 and any(ch in singles for ch in k):
        risky.append(k)
P(f"含单字停用字的标注词 {len(risky)}: {sorted(set(risky))[:60]}")

open("eval/stop_merge_analysis.txt", "w", encoding="utf-8").write(OUT.getvalue())
print("wrote eval/stop_merge_analysis.txt")
