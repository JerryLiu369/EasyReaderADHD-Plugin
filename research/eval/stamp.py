import re
import time

p = "eval/mvp_multi.html"
h = open(p, encoding="utf-8").read()
h = re.sub(r"<div style='background:#eef;[^>]*>.*?</div>", "", h, count=10)
parts = re.split(r"<h1>", h)[1:]
info = []
for part in parts:
    title = part.split("</h1>")[0][:24]
    n_p = part.count("<p>") - part.count("<p class")
    n_s = part.count("<strong>")
    info.append(f"{title}…：{n_p}段/{n_s}处加粗")
banner = (
    "<div style='background:#eef;border:1px solid #99c;padding:8px 12px;font-size:14px;color:#333'>"
    f"v14 版 · 生成时间 {time.strftime('%m-%d %H:%M')} · " + "｜".join(info) + "</div>"
)
h = h.replace("<body>", "<body>" + banner, 1)
open(p, "w", encoding="utf-8").write(h)
print("stamped v14")
