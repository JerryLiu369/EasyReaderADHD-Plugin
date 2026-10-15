import re

c = open("C:/Users/ljw/.config/opencode/opencode.json", encoding="utf-8").read()
low = c.lower()
for kw in ["ark", "deepseek", "volc", "flash"]:
    j = low.find(kw)
    if j >= 0:
        seg = c[max(0, j - 120) : j + 200]
        seg = re.sub(
            r'"(apiKey|api_key|key|secret|token)"\s*:\s*"[^"]+"', r'"\1": "<redacted>"', seg
        )
        print("---", kw, "---")
        print(seg[:320])
