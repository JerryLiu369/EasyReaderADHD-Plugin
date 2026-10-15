# research/ —— 中文阅读加粗算法（Jev 版）· 工作存档

> 本目录是 EasyReaderADHD 的后续研究：用 Jev（typesafe.ai 的判断模型）解决
> 「中文阅读该加粗哪些词」的问题。项目定位未定，此处先存全部工作记录，后续统一整理。
> 存放日期 2026-10-15，算法版本 v14。

## 入口（按顺序读）

1. `docs/00-README.md` —— 文档地图与总览（概念 → 老方案病根 → Jev 机制 → 架构 → 呈现设计 → 算法管线）。
2. `eval/README.md` —— 评测地图：闭环矩阵（prompt × 语料）、文件地图、指标口径。
3. `eval/00-results.md` —— 编年史：E0 连通性 → E1 评测 → MVP v1–v14 每次改了什么、为什么、花了多少。
4. `eval/mvp.py` —— 生产管线唯一实现（实现与 `docs/06-算法管线.md` 逐条对应）。

## 效果（v14 冻结）

- 管线：候选器（本地高召回）→ Jev 法官（批量打分排序，prompt en-v3 冻结）→ 渲染器（按句预算 Top-K 加粗）。
- 数：E1 排序 P@K 0.929 / 端到端 E2E 0.518；全新 holdout-20（LLM 盲标互证）P@K 0.642 / E2E 0.462。
- 渲染页（浏览器直接打开）：`eval/demo3.html`、`eval/mvp_multi.html`、`eval/mvp_holdout.html`。
- 成本：约 3400 次 Jev 请求 ≈ $0.25（全部记账在 `eval/.usage.json`）。

## 怎么跑

```bash
cd research
python eval/demo3.py        # 三篇演示（走缓存，零新请求）
python eval/run_multi.py    # 7 篇批跑 → eval/mvp_multi.html
```

- 需要 `research/jev_key.txt`（一行，Jev API key；**本仓库不包含，请自备**——脚本读环境变量
  `JEV_API_KEY` 优先，其次读该文件；已加入 .gitignore）。
- 脚本内路径均相对 `research/` 工作目录。
- `eval/.score_cache.json` 是打分缓存（state+词 → 分），带着它重渲染零成本。

## 说明

- 语料（`eval/corpus/`，含 `raw/`）为公开网站文章抓取存档，仅供研究对照使用。
- `eval/stopwords/` 为四公开停用词表（哈工大/百度/中文/川大）原文 + 共识合并脚本（生成 `merged_stopwords.txt`）。
- 详细变更史见 `eval/00-results.md`；已知弱项与过拟合审计记录同在其中（"过拟合审计 + v13/v14"节）。
