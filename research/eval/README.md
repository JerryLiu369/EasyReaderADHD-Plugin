# Eval 地图（一页纸：测了什么、在哪、数是多少）

> 读不懂从这里开始。所有结论以本页为准，细节链到各文件。

##  closed-loop 总表（prompt × 语料，同一指标 P@K；探针用 top-k hit，单独注明）

| prompt | E1-20（现代网文，P@K） | my-8（混合难例） | preLLM（top-3 hit） | preModern（top-k hit） | holdout-20（LLM盲标） |
|---|---|---|---|---|---|
| en-v1（主旨） | 0.881 | 基线（`align.py`） | — | — | — |
| en-v2（转述-specificity） | 0.922 | 6/8 提升（`tune3.py`） | — | — | — |
| en-v3（v2+通用粘连约束） | **0.929** | —（未重跑） | 10/25=0.40 | 25/62=0.403 | P@K 0.642 / E2E 0.462（`xcheck.py`） |
| role-choice（Jev 出角色，代码选） | 0.910（否决，见 00-results 架构复核） | — | — | — | — |

结论冻结：当前生产管线 = en-v3 + v14 算法。改 prompt 必须先填满 E1 列，再谈其他列。
v14 起停用词全公有化：四公开表（哈工大/百度/中文/川大）共识合并 338 条，见 `stopwords/`，零手写。

## 文件地图

- `eval/00-results.md` —— 编年史（v1→v8 每次改了什么、为什么、花了多少）。长，但只读这一节就够：**MVP v8**。
- `eval/README.md` —— 本页。
- 语料：`corpus/corpus.json`（14 篇现代 + 3 篇前 AI + 3 篇 sina-blog）+ `corpus/raw/*.txt`（原文）。
- 标注：`corpus/e1_labels.json`（E1-20）、`mylabels.json`（难例 8 段）、`prellm_labels.json`（韩寒）、`classic_labels.json`（鲁迅等）。
- 管线：`mvp.py`（候选→打分→渲染唯一实现）、`run_multi.py`（多篇批跑）、`e2e_e1.py`（端到端覆盖率）。
- 调参：`tune.py`（B/C/D 否决记录）、`tune2.py`（choice 放量失败记录）、`tune3/4/5.py`（v2/v3 验证）、`tune6.py`（role-choice）。
- 渲染页：`mvp_multi.html`（主，7 篇）、`mvp_prellm.html`（韩寒）、`mvp_classic.html`（鲁迅等）。
- 设计文档：`docs/00-README.md`（地图）、`01-概念`、`02-老方案病根`、`03-jev机制`、`04-架构`、`05-呈现设计`。

## 指标口径（别混用）

- **P@K**：E1 专用。每段 keys 数 K，top-K 里 keys 占比。基线随机 ≈0.6。
- **top-k hit**：探针专用（my-8/preLLM/preModern）。我的标进 top-k（k=max(3,标数)）占比。
- **E2E coverage**：完整管线渲染后，E1 标被命中的词占比。0.465（含密度截断效应，不是纯排序分）。
- **mean rank**：我的标在候选里的平均排名。越小越好。
