"""MVP：txt 中文文章 → Intl.Segmenter 候选 → Jev 批量 noul → Top-K 加粗 → 自包含 HTML。
预算：与 E1 共用 eval/.usage.json，100 次封顶。Key：JEV_API_KEY 环境变量优先，否则 jev_key.txt（永不打印）。
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

EP = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
USAGE_FILE = "eval/.usage.json"
CACHE_FILE = "eval/.score_cache.json"
WORDING_VER = "en-v3"  # v3 = v2 + 通用粘连约束（动词开头/虚词收尾，零语料例子），E1 P@K 0.922->0.929
BUDGET = 1000000  # 用户已确认按量付费（90 次 ≈ $0.0066），只记账不限流
MAX_Q_PER_REQ = 50  # tune D 验证：50/批与 25/批同延迟，请求数减半
COV_TARGET = 0.12  # 加粗覆盖率：content 字符占比（所见即所得，比按词数更诚实）
# 预算/锚点双 floor（v12）：judge 自己都瞧不上的（<0.25）不买，句子空着。
# 动因：按句预算会强行给全弱句加粗（没做到 0.19/不甚明 0.20/多说一句 0.10），标错比不标更坏（05）。
# 不是阈值排序（E1 证明绝对阈值误杀好词）——floor 只拦 0.25 以下的地下室，E1 keys 均值 0.69，门测 E2E。
SCORE_FLOOR = 0.25

# 消融开关：全开 = 生产配置。use_trigram 已死（v9 删三字循环，此键仅留形，恒 False）。
CFG = {"use_stop": True, "use_func": True, "use_trigram": False, "use_runs": True,
       "use_substr": True, "use_mergecap": True, "use_sentbudget": True}


def get_key():
    if os.environ.get("JEV_API_KEY"):
        return os.environ["JEV_API_KEY"].strip()
    return open("jev_key.txt", encoding="utf-8").read().strip()


def usage():
    try:
        return json.load(open(USAGE_FILE, encoding="utf-8"))
    except FileNotFoundError:
        return {"requests": 0, "input_tokens": 0, "output_tokens": 0}


def save_usage(u):
    json.dump(u, open(USAGE_FILE, "w", encoding="utf-8"), indent=1)


def call_jev(state, questions):
    u = usage()
    if u["requests"] >= BUDGET:
        raise RuntimeError(f"budget exhausted: {u['requests']}/{BUDGET}")
    body = json.dumps(
        {"model": MODEL, "state": state, "questions": questions}, ensure_ascii=False
    ).encode("utf-8")
    key = get_key()
    last = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(
                EP,
                data=body,
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            )
            t = time.time()
            resp = urllib.request.urlopen(req, timeout=90)
            raw = json.loads(resp.read().decode("utf-8"))
            u["requests"] += 1
            u["input_tokens"] += raw.get("usage", {}).get("input_tokens", 0)
            u["output_tokens"] += raw.get("usage", {}).get("output_tokens", 0)
            save_usage(u)
            return raw, int((time.time() - t) * 1000)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 529):
                time.sleep(2**attempt * 2)
                continue
            raise
        except Exception as e:  # noqa: BLE001 — 网络抖动（SSL EOF 等），退避重试
            last = e
            time.sleep(min(30, 2**attempt * 2))
            continue
    raise last


def load_cache():
    try:
        return json.load(open(CACHE_FILE, encoding="utf-8"))
    except FileNotFoundError:
        return {}


def save_cache(c):
    json.dump(c, open(CACHE_FILE, "w", encoding="utf-8"), ensure_ascii=False)


def cache_key(state, term):
    import hashlib

    return hashlib.sha1(f"{WORDING_VER}|{state}|{term}".encode("utf-8")).hexdigest()[:20]


def score_terms(state, uniq):
    """先查缓存，未命中才调 Jev。返回 {term: noul}。"""
    cache = load_cache()
    missing = [t for t in uniq if cache_key(state, t) not in cache]
    for bi in range(0, len(missing), MAX_Q_PER_REQ):
        batch = missing[bi : bi + MAX_Q_PER_REQ]
        qs = {f"q{j}": mk_q(t) for j, t in enumerate(batch)}
        raw, ms = call_jev(state, qs)
        for j, t in enumerate(batch):
            cache[cache_key(state, t)] = raw["answers"][f"q{j}"]["noul"]
        save_cache(cache)
        print(f"  batch {bi//MAX_Q_PER_REQ} ms={ms} n={len(batch)} toks={raw.get('usage')}")
    return {t: cache[cache_key(state, t)] for t in uniq}


# ---- 候选器：Node Intl.Segmenter（复用系统 ICU，无需依赖） ----
NODE_SEG_JS = r"""
const segs = JSON.parse(require('fs').readFileSync(0, 'utf-8'));
const s = new Intl.Segmenter('zh', {granularity: 'word'});
const out = segs.map(t => [...s.segment(t)].map(x => ({text: x.segment, off: x.index})));
console.log(JSON.stringify(out));
"""


def segment_all(paras):
    import subprocess

    p = subprocess.run(
        ["node", "-e", NODE_SEG_JS],
        input=json.dumps(paras, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", "ignore")[:500])
    return json.loads(p.stdout.decode("utf-8"))


PUNCT = set(
    "，。！？；：、（）【】《》「」『』…—·,.!?;:()[]<>\"' \t\n　"
    "“”‘’〈〉‹›〔〕［］｛｝～￥§©®※☆★○●◎◇◆□■△▲→←↑↓＊＆＃＠"
)
# 单字虚词：永不作为候选（E1 已证它们得分垫底，这里直接省掉问题数）
# 按：介词，与把被给对从同类，v10 补齐（holdout：按风格筛选被按风格切散，风格筛选才是锚点）。
# v12 拿掉“地”：地是内容语素（地缘/地球/地址）兼结构助词，单字过滤把“地|缘|竞争”拦腰截断，
# 地缘这个 pair 永远组不出来，只剩缘竞争等碎缝（demo3 cssn 目检）。
# 助词用法下游兜底：单字<2丢、Jev wording 压虚词尾、E1/multi 门。E1 keys 零地头，multi 地头全是正经词。
FUNC_CHARS = set("的了着过和与或但而在个得是很最太都就才把被给对从向往由及若如因果是这那我你他她它您怎哪谁此彼之乎者也矣焉哉乃即既且亦仍还又再更已曾将正便按")
# 说明：只收代词/指示/文言虚词/典型副词性单字；刻意排除“就”（就业类整词风险），E2E 回归兜底。
# v13 删“利”：审计发现它是全表唯一内容名单字（利润/利益），误混入；HIT 无，E1/multi/LLM 零依赖。
# 便保留（以便/顺便类副词用法，HIT 以便在列）。
DIGITS = set("0123456789０１２３４５６７８９")
# 停用词：公开表合并，零手写（v14）。
# 来源：哈工大/百度/中文/四川大学四表（原文本落 eval/stopwords/，见 merged_stopwords.txt 头注释）。
# 合并规则（确定性，无人工挑选）：四表共识 = 同时出现于全部四表、去重。
# 用途分两档（动因：单字条目如 一/个/中 若当半边用会把 一个中国/本质 类真词全杀）：
#   STOP        ：合并全表（338 条），候选整词精确命中即丢（单字永远进不了候选，等价无害）。
#   STOP_MULTI  ：仅多字条目（315 条），用于双字半边、runs 首尾、数量短语名词单元。
#     （另有 23 个四表共识单字——乎/了/们/你/俺/别/及/吧/哎/哦/唉/啊/啦/嘿/她/它/您/我/或/把/按/既——
#      单独并入 HALF_BAD：它们本身就是功能字，单用合法。）
STOP_PATH = "eval/stopwords/merged_stopwords.txt"
STOP = set(
    l.strip() for l in open(STOP_PATH, encoding="utf-8")
    if l.strip() and not l.startswith("#")
)
STOP_MULTI = {w for w in STOP if len(w) >= 2}
STOP_SINGLE_CONSENSUS = {w for w in STOP if len(w) == 1}
# 量词（Fix A 数量短语用）：标准现代汉语常用量词小表。NUM+量词(+名词)直组候选，
# 治“183|个|国家”被个拦腰截断（个是单字虚词，通用规则下数量短语永不可建）。
CLF = set("个位名只条张件项次种类型款台部篇本笔单批轮场届任年月日号周岁时分秒度米块元角分倍番通阵趟顿头匹辆艘架枚封则首曲出间所家座栋层户双对副套组群堆串排列表波回章节点线面片块堆群")
# 注：set 去重后约 70 字，宁多勿少——误收的后果只是多一个候选（Jev 排序兜底），漏收则是召回死角。
NUM_CJK = set("一二三四五六七八九十百千万亿两几多半")
DIGITS_ALL = set("0123456789０１２３４５６７８９.,%％．")


def is_content(seg):
    t = seg["text"].strip()
    if not t or all(ch in PUNCT for ch in t):
        return False
    if CFG["use_func"] and len(t) == 1 and t in FUNC_CHARS:
        return False
    return True


def clean_span(text, s, e):
    """剔掉 span 两端粘上的引号括号等，还回干净 offsets。"""
    while s < e and text[s] in PUNCT:
        s += 1
    while e > s and text[e - 1] in PUNCT:
        e -= 1
    return s, e


def build_candidates(text, seg_list):
    """单词 + 相邻双字（中间无任何字符才拼，不跨标点）。返回 [(s, e, text)]。
    卫生：两端修剪标点；单字一律丢（05 规定 span≥2）；纯数字/单字母丢；
    功能词 exact 丢；双字任一半是功能词则整条丢。
    """
    HALF_BAD = STOP_MULTI | STOP_SINGLE_CONSENSUS | FUNC_CHARS
    content = [s for s in seg_list if is_content(s)]
    # 每个候选附带首单元文本，用于首虚规则
    raw = [((s["off"], s["off"] + len(s["text"])), s["text"]) for s in content]
    pairs = []
    units = [(s["off"], s["off"] + len(s["text"]), s["text"]) for s in content]


    def gap_ok(xe, ys):
        gap = text[xe:ys]
        return gap == "" or re.fullmatch(r"[\s·・‧•/．]+", gap)


    for a, b in zip(units, units[1:]):
        # 双字：任一半功能词则整条丢
        if gap_ok(a[1], b[0]):
            if CFG["use_stop"] and (a[2] in HALF_BAD or b[2] in HALF_BAD):
                continue
            # 有+纯数字（如 有|183）恒为存在句胶水，信息全在后面的数量短语里（Fix A 组）。
            # 只杀“有+数字”，不动有线/有效类（第二半是 CJK）和近800类（首字不是有）。
            # multi 全量 1587 锚点中零“有+数字”picked，E1 keys 零命中，孤证不成立但无回归面。
            if len(a[2]) == 1 and a[2] == "有" and all(ch in DIGITS_ALL for ch in b[2]):
                continue
            pairs.append(((a[0], b[1]), a[2]))
    # 注：三字候选已删除（消融结论：no-trigram E2E 0.465→0.500，且 E1-00/01 的粘连碎片
    # 几乎全是三字拼出来的。异地代缴类由“词+单字”双字 + 首单元规则覆盖，不需要三字。）

    def cjk_single(t):
        return len(t) == 1 and "\u4e00" <= t <= "\u9fff"

    def cjk_unit2(t):
        # 短多字单元（2 字 CJK 词）：runs 扩展用。3 字以上不许进（锦标赛类走 pairs）。
        return len(t) == 2 and all("\u4e00" <= ch <= "\u9fff" for ch in t)

    def ascii_initial(t):
        # 英文首字母缩写（W./J/A）：后接 CJK 单字串时一起成块（W.布莱恩·阿瑟类，demo3 目检漏网）。
        return re.fullmatch(r"[A-Za-z]\.?", t) is not None

    # 单字串 + v12 混合串：连续 gap_ok 单元，每个是单字 CJK 或 2 字 CJK 词，
    # 其中单字 ≥1、多字 ≤1、CJK 总量 ≤6。治混合切碎：地缘+竞争/空间+维度/保护+伞/
    # 中+美元+首/整+条+航道/海报+样+张。
    # 防粘连复活线：最多 1 个多字——位来自全球（1单+2多）、全国锦标（0单）永不可建，
    # 三字禁令不破；约定不以实际靠“以”被滤断双保险。word+单字的拼接仍走 pairs。
    runs = []
    if CFG["use_runs"]:
        i, n = 0, len(content)

        def extend_from(j, multis):
            while j + 1 < n:
                nt = content[j + 1]["text"]
                if cjk_single(nt):
                    pass
                elif cjk_unit2(nt) and multis < 1:
                    multis += 1
                else:
                    break
                if not re.fullmatch(
                    r"[\s·・‧•/．]*",
                    text[content[j]["off"] + len(content[j]["text"]):content[j + 1]["off"]],
                ):
                    break
                j += 1
            return j

        while i < n:
            t0 = content[i]["text"]
            start, j, multis, ok = i, i, 0, False
            if cjk_single(t0):
                ok = True
            elif ascii_initial(t0) and i + 1 < n and cjk_single(content[i + 1]["text"]) \
                    and re.fullmatch(r"[\s·・‧•/．.]*",
                                     text[content[i]["off"] + len(t0):content[i + 1]["off"]]):
                # ASCII 开头：点号走 gap 类；两种切分 W.|布 / W|.|布都兼容
                j = i + 1
                ok = True
            elif cjk_unit2(t0) and i + 1 < n and cjk_single(content[i + 1]["text"]):
                # 多字开头：后必须紧跟单字（全国|锦标类纯多字组合不进，仍是 pairs 的活）
                ok = True
            if ok:
                j = extend_from(j, multis)
                span = (content[start]["off"], content[j]["off"] + len(content[j]["text"]))
                cjk_n = sum(1 for ch in text[span[0]:span[1]] if "\u4e00" <= ch <= "\u9fff")
                nunits = j - start + 1
                nsingle = sum(1 for k in range(start, j + 1) if cjk_single(content[k]["text"]))
                if nunits >= 2 and nsingle >= 1 and 2 <= cjk_n <= 6:
                    # 首尾单元禁 STOP 多字词：runs 是 licensed 通道（跳过半边检查），
                    # 不加这道闸，我们/自己会借 runs 还魂（我们屈髋抬腿/自己挂/一间自己，multi 目检）。
                    # 中间夹 STOP 多字不管（罕见，Jev 裁决）；单字虚词进不了串（扫的是过滤后序列+gap 断）。
                    if content[start]["text"] not in STOP_MULTI and content[j]["text"] not in STOP_MULTI:
                        runs.append((span, content[start]["text"]))
                i = j + 1
            else:
                i += 1

    # 数量短语（v10）：NUM + 量词 + 1-2 个名词，直组候选。
    # 动因：通用规则（个/款是单字虚词）把“183|个|国家”拦腰截断，数量短语永不可建，
    # 而它是跨体裁最高频的信息锚（183个国家/四款字体/30分钟/两度会晤/十年前）。
    # 类规则（数词+量词+名词），非语料例表。CJK 总量 ≤8。
    # 注意：必须扫未过滤的 seg（含单字虚词——量词本身就是虚词），在过滤后的 units 上扫永远对不上。
    def is_num_unit(u):
        return bool(u) and all(ch in DIGITS_ALL or ch in NUM_CJK for ch in u)

    def is_clf_unit(u):
        return 1 <= len(u) <= 2 and all(ch in CLF for ch in u)

    def is_noun_unit(u):
        return bool(u) and u not in STOP_MULTI and not (len(u) == 1 and u in FUNC_CHARS)

    full = [(s["off"], s["off"] + len(s["text"]), s["text"]) for s in seg_list
            if s["text"].strip() and not all(ch in PUNCT for ch in s["text"].strip())]
    qty = []
    k, nu = 0, len(full)
    while k < nu:
        if is_num_unit(full[k][2]):
            j = k
            while (j + 1 < nu and is_num_unit(full[j + 1][2])
                   and gap_ok(full[j][1], full[j + 1][0])):
                j += 1
            # 可选一个量词
            if (j + 1 < nu and is_clf_unit(full[j + 1][2])
                    and gap_ok(full[j][1], full[j + 1][0])):
                j += 1
            # 1-2 个名词单元。两个变体都建（1 名词 + 2 名词），防“国家|坚持”把动词吸进来：
            # 变体间是子串关系，渲染侧 contained() 只留高分者。
            nn = 0
            variants = []
            while (nn < 2 and j + 1 < nu
                   and gap_ok(full[j][1], full[j + 1][0])
                   and is_noun_unit(full[j + 1][2])):
                j += 1
                nn += 1
                variants.append(j)
            for v in variants:
                s, e = full[k][0], full[v][1]
                cjk_n = sum(1 for ch in text[s:e] if "\u4e00" <= ch <= "\u9fff")
                if 2 <= cjk_n <= 8:
                    qty.append(((s, e), None))  # first=None： licensed，跳过首虚/半边检查
            k = j + 1 if j > k else k + 1
        else:
            k += 1
    cand = []
    for (s, e), first in raw + pairs + runs + qty:
        s, e = clean_span(text, s, e)
        t = text[s:e]
        if not t or len(t) < 2:
            continue
        # 首单元是单字虚词（如 是|大国）则整条丢；的/是开头一律丢（的确类弱锚点可舍）。
        # 不用 t[0] 判：地方/地球类首字虽虚但首单元是整词，必须保留。
        # first=None 是数量短语 licensed 通道，跳过本条。
        if first is not None and CFG["use_func"] and ((len(first) == 1 and first in FUNC_CHARS) or t[0] in "的是"):
            continue
        if first is not None and len(t) > 2 and t[0] in FUNC_CHARS and t[1] not in FUNC_CHARS:
            # 单 token 首字虚词 + 后跟非虚词：只有“后跟 ASCII/数字”才剥头（如 有183→183，
            # 分词器没切开的粘连）。纯 CJK 不动（有用/地方类整词风险）。
            # 的/是开头已在上条整条丢，这里只处理其他虚词。
            if re.match(r"[A-Za-z0-9０-９]", t[1]):
                s, e = s + 1, e
                t = text[s:e]
                if len(t) < 2:
                    continue
        if all(ch in DIGITS for ch in t):
            continue  # 纯数字不成锚点（含单位的如 60Kstar 不受影响）
        if CFG["use_stop"] and t in STOP:
            continue
        cand.append((s, e, t))
    # 宁粗勿碎：任一候选 occurrence 若被另一个更长的候选完全覆盖则丢掉（01 §1.4-4）。
    # 如 蒂利⊂查尔斯·蒂利，只留后者参选；重叠但互不包含（如 AB/BC）的不动，交给贪心。
    spans = [(s, e) for (s, e, _) in cand]
    drop = {
        (s, e, t)
        for (s, e, t) in cand
        if any((s2, e2) != (s, e) and s2 <= s and e <= e2 for (s2, e2) in spans)
    }
    return [c for c in cand if c not in drop]


def mk_q(term):
    return {
        "type": "noul",
        "instructions": {
            "target": term,
            "question": "If a reader had to retell this paragraph's specific points — who, which theory or scheme, what mechanism or evidence — would missing `target` make the retelling vaguer?",
        },
        "criteria": {
            "true": "A name, theory/scheme label, mechanism, number, or example that carries the argument; removing it loses attribution or specifics",
            "false": "A general topic word, filler, scene-setting, or connective; removing it changes nothing specific. Also a phrase that begins with a verb or trails off with a particle, conjunction, or demonstrative",
        },
    }


def split_sentences(text):
    # 锚点单位细化到子句（群友建议：目光跟踪的负担来自长连续字符）。
    # 按句读标点切分；锚点补足只管内容 ≥15 字的长子句，短子句不强制。
    spans, cur, start = [], "", 0
    for i, ch in enumerate(text):
        if not cur:
            start = i
        cur += ch
        if ch in "。！？…\n；：，、":
            if cur.strip():
                spans.append((start, cur))
            cur = ""
    if cur.strip():
        spans.append((start, cur))
    return spans or [(0, text)]


MIN_CLAUSE_FOR_ANCHOR = 15


def split_top_sentences(text):
    # 顶层句（只按 。！？…\n 切，不按 ，；：、）：v12 预算分配单位。
    spans, cur, start = [], "", 0
    for i, ch in enumerate(text):
        if not cur:
            start = i
        cur += ch
        if ch in "。！？…\n":
            if cur.strip():
                spans.append((start, cur))
            cur = ""
    if cur.strip():
        spans.append((start, cur))
    return spans or [(0, text)]


MIN_SENT_CONTENT = 8


def content_len(s):
    return sum(1 for ch in s if ch not in PUNCT)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_para(text, scores):
    # scores: [(s,e,t,n)]，同文本同分。预算按顶层句分配（。，！？…，每句 12% 字符覆盖率），
    # 句内按分贪心取不重叠 span；同词只取首次（全段去重）；长子句无命中补锚点；相邻 span 外观合并。
    # v12：全局贪心改按句贪心——全局抢预算必然前密后疏（demo3 韩寒段 17% 全堆前 60%），
    # 按句分配密度天然铺平，总量仍是 12%（+锚点+短句上溢，见 v3 记录）。
    total = sum(1 for ch in text if ch not in PUNCT) or 1
    tscore = {}
    for (s, e, t, n) in scores:
        tscore[t] = n
    ranked = sorted(tscore, key=lambda t: -tscore[t])
    picked = []
    picked_texts = []

    def overlaps(s, e):
        return any(s < pe and ps < e for (ps, pe) in picked)

    def contained(t):
        # 已选词的子串/超串一律抑制：缴纳社会保险 vs 缴纳社会保险费只留一个（全段生效，跨句去重）
        if not CFG["use_substr"]:
            return False
        return any(t in pt or pt in t for pt in picked_texts)

    def take(s0, s1, budget):
        cov = 0
        for t in ranked:
            if cov >= budget:
                break
            if tscore[t] < SCORE_FLOOR:
                break  # 按分降序，此后全在地下室——预算有剩也不买弱词
            if contained(t):
                continue
            for (s, e, tt, _) in sorted([r for r in scores if r[2] == t and s0 <= r[0] and r[1] <= s1]):
                if not overlaps(s, e):
                    picked.append((s, e))
                    picked_texts.append(t)
                    cov += e - s
                    break
        return cov

    cov_all = 0
    if CFG.get("use_sentbudget", True):
        for s0, sent in split_top_sentences(text):
            cl = content_len(sent)
            if cl < MIN_SENT_CONTENT:
                continue  # 太短的句子不参与（防“没关系。”式 67% 上溢；锚点规则同样够不着它）
            cov_all += take(s0, s0 + len(sent), COV_TARGET * cl)
    else:
        cov_all = take(0, len(text), COV_TARGET * total)
    cov = cov_all
    for s0, sent in split_sentences(text):
        s1 = s0 + len(sent)
        if content_len(sent) < MIN_CLAUSE_FOR_ANCHOR:
            continue  # 短子句不强制锚点，防密度膨胀
        if not any(s < s1 and s0 < e for (s, e) in picked):
            # 锚点补足不复用已加粗的词（含子串关系）：重复零信息，宁缺勿滥（优先于每句有锚）。
            # 同受 SCORE_FLOOR：judge 打进地下室的候选不配当锚点。
            cands = [
                r
                for r in scores
                if s0 <= r[0] and r[1] <= s1 and r[3] >= SCORE_FLOOR
                and not overlaps(r[0], r[1]) and not contained(r[2])
            ]
            if cands:
                b = max(cands, key=lambda r: r[3])
                picked.append((b[0], b[1]))
                picked_texts.append(b[2])
                cov += b[1] - b[0]
    picked.sort()
    merged = []
    for s, e in picked:
        # 外观合并，上限 6 字：防 10 字长串（酸痛的是大腿前侧类）
        if merged and text[merged[-1][1] : s] == "" and (
            e - merged[-1][0] <= 6 or not CFG["use_mergecap"]):
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    html, cur = [], 0
    for s, e in merged:
        html.append(esc(text[cur:s]))
        html.append(f"<strong>{esc(text[s:e])}</strong>")
        cur = e
    html.append(esc(text[cur:]))
    return "".join(html), len(merged), cov / total


def main(inp, outp):
    paras = [p.strip() for p in open(inp, encoding="utf-8").read().split("\n") if p.strip()]
    seg_lists = segment_all(paras)
    out_paras, total_req = [], usage()["requests"]
    for pi, (text, seg_list) in enumerate(zip(paras, seg_lists)):
        content = [s for s in seg_list if is_content(s)]
        cand = build_candidates(text, seg_list)
        # 去重 + 缓存：同段同词只问一次，跑过的不再花钱
        seen, uniq = {}, []
        for (_, _, t) in cand:
            if t not in seen:
                seen[t] = True
                uniq.append(t)
        print(f"para {pi}: unique {len(uniq)}/{len(cand)}")
        score_of = score_terms(text, uniq)
        scores = [(s, e, t, score_of[t]) for (s, e, t) in cand]
        html, npick, cov = render_para(text, scores)
        out_paras.append(html)
        print(f"para {pi}: picked {npick} spans, cov={cov:.0%}")
    u = usage()
    doc = (
        "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
        "<style>body{max-width:34em;margin:3em auto;line-height:2;font-size:18px;"
        "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif}"
        "strong{font-weight:700;padding:0 .08em}header{color:#888;font-size:14px;border-bottom:1px solid #ddd;"
        "margin-bottom:2em;padding-bottom:1em}</style></head><body>"
        f"<header>MVP demo · 覆盖率目标 {COV_TARGET:.0%} · Jev 请求累计 {u['requests']}</header>"
        + "".join(f"<p>{p}</p>" for p in out_paras)
        + "</body></html>"
    )
    open(outp, "w", encoding="utf-8").write(doc)
    print("wrote", outp, "requests used:", u["requests"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
