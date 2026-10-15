"""客观层：重复率 / 单字率 / 相邻碎片率 / 覆盖率分布。机器算的，不偏。"""
import re
from collections import Counter

h = open("eval/mvp_multi.html", encoding="utf-8").read()
parts = re.split(r"<h1>", h)[1:]
all_rep, all_single, all_adj, covs = [], [], [], []
for p in parts:
    title = p.split("</h1>")[0][:30]
    paras = re.findall(r"<p>(.*?)</p>", p)
    reps, singles, adjs, n = 0, 0, 0, 0
    for para in paras:
        strongs = re.findall(r"<strong>(.*?)</strong>", para)
        n += len(strongs)
        c = Counter(strongs)
        reps += sum(v - 1 for v in c.values() if v > 1)
        singles += sum(1 for s in strongs if len(s) == 1)
        # 相邻：</strong> 后紧跟 <strong>
        adjs += len(re.findall(r"</strong><strong>", para))
    print(f"[{title}] paras={len(paras)} strongs={n} 重复={reps} 单字={singles} 相邻={adjs}")
    all_rep.append(reps / max(1, n))
    all_single.append(singles / max(1, n))
print("mean 重复率=%.2f 单字率=%.2f" % (
    sum(all_rep) / len(all_rep), sum(all_single) / len(all_single)))
