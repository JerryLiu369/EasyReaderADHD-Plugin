import re

h = open("eval/mvp_multi.html", encoding="utf-8").read()
parts = re.split(r"<h1>", h)[1:]
for p in parts:
    title = p.split("</h1>")[0]
    n_strong = p.count("<strong>")
    n_p = p.count("<p") - p.count("<p class")
    print(f"[{title[:30]}] paras={n_p} strongs={n_strong} per-para={n_strong/max(1,n_p):.1f}")
    first = re.search(r"<p>(.*?)</p>", p)
    if first:
        t = re.sub(r"<[^>]+>", "【", first.group(1))
        print("   ", t[:220])
