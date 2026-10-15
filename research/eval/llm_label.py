"""LLM二评：deepseek-flash独立标holdout 20段关键词。与Jev wording异构（中文指令+JSON整段标），盲测。
输出 eval/llm_labels.json：[{doc, text, keys}]"""
import json
import re
import time
import urllib.request

CFG = json.load(open(r"C:\Users\ljw\.config\opencode\opencode.json", encoding="utf-8"))
PROV = CFG["provider"]["axon-completions"]["options"]
EP = PROV["baseURL"] + "/chat/completions"
KEY = PROV["apiKey"]

PROMPT = """你是中文阅读辅助标注员。读下面段落，列出5-8个最关键的词/短语。
标准：删掉它，转述这段话会丢失具体信息（谁、哪个东西、什么机制、什么数字例证）。
排除：泛泛的话题词、语气词、连接词、单字虚词。
要求：每个关键词必须在原文中逐字出现，2-6字，只回JSON数组，如["词1","词2"]，不要其他字。
段落：
{para}"""


def label(para):
    body = json.dumps({
        "model": "deepseek-flash",
        "messages": [{"role": "user", "content": PROMPT.format(para=para)}],
        "max_tokens": 2000, "reasoning_effort": "low", "temperature": 0.2,
    }, ensure_ascii=False).encode()
    last = None
    for att in range(6):
        try:
            req = urllib.request.Request(EP, data=body, headers={
                "Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
            raw = json.loads(urllib.request.urlopen(req, timeout=90).read().decode())
            txt = raw["choices"][0]["message"]["content"] or ""
            m = re.search(r"\[.*?\]", txt, re.S)
            keys = json.loads(m.group(0)) if m else []
            keys = [k for k in keys if isinstance(k, str) and 2 <= len(k) <= 8 and k in para][:8]
            if len(keys) >= 3:
                return keys, raw.get("usage", {})
            last = f"too few({len(keys)}): {txt[:150]}"
        except Exception as e:
            last = str(e)[:150]
        time.sleep(3 * (att + 1))
    # 降级：实在标不出也要落盘，记fail待查，不中断整批
    print(f"  WARN label fail, keep empty: {last}")
    return [], {}


if __name__ == "__main__":
    hold = json.load(open("eval/holdout.json", encoding="utf-8"))
    out = []
    for i, p in enumerate(hold["paras"]):
        keys, usage = label(p["text"])
        out.append({"i": i, "doc": p["doc"], "text": p["text"], "keys": keys})
        print(f"{i:02d} doc={p['doc'][-8:]} keys={keys}")
    json.dump(out, open("eval/llm_labels.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", len(out))
