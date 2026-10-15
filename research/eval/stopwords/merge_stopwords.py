"""生成 eval/stopwords/merged_stopwords.txt：四公开表共识合并（确定性，无人工挑选）。
来源：goto456/stopwords 仓库的 hit/baidu/cn/scu 四表（原文由 fetch_stopwords.py 下载）。
规则：同时出现于全部四表 → 去重 → 排序 → 落文件（含表头注释，加载时跳过头注释行）。"""
from collections import Counter

NAMES = ["hit_stopwords", "baidu_stopwords", "cn_stopwords", "scu_stopwords"]
LISTS = {}
for n in NAMES:
    LISTS[n] = set(l.strip() for l in open(f"eval/stopwords/{n}.txt", encoding="utf-8") if l.strip())

cnt = Counter()
for s in LISTS.values():
    for w in s:
        cnt[w] += 1

all4 = sorted(w for w, c in cnt.items() if c == 4)
multi = [w for w in all4 if len(w) >= 2]
single = [w for w in all4 if len(w) == 1]
assert len(all4) == len(multi) + len(single)

header = [
    "# merged_stopwords.txt —— 四公开中文停用词表共识（合并脚本 eval/stopwords/merge_stopwords.py）",
    "# 来源：goto456/stopwords · hit_stopwords + baidu_stopwords + cn_stopwords + scu_stopwords",
    "# 规则：同时出现于全部四表的词（去重后 %d 条；多字 %d、单字 %d）。无人工增删。"
    % (len(all4), len(multi), len(single)),
    "# 用法（mvp.py）：全表查 exact；多字条目另用于双字半边/串首尾/数量短语名词单元；",
    "# 单字条目仅 exact（单字候选本就进不了候选集）。",
]
open("eval/stopwords/merged_stopwords.txt", "w", encoding="utf-8").write(
    "\n".join(header) + "\n" + "\n".join(all4) + "\n")
print(f"merged: {len(all4)} (multi {len(multi)}, single {len(single)})")
