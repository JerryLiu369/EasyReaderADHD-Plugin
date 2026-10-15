"""提取韩寒《春萍，我做到了》(2012) 与 《地震思考录》(2013)，以及检查阮一峰/刘未鹏早期博客"""
import re
import urllib.request
import json

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = re.sub(r"\s+", " ", s).strip()
    return s

# 1. 韩寒《春萍，我做到了》
h1 = get("http://blog.sina.com.cn/s/blog_4701280b0102ec39.html")
m1 = re.search(r'id="sina_keyword_ad_area2"(.*)', h1, re.S)
body1 = m1.group(1)[:200000] if m1 else h1
paras1 = [strip(p) for p in re.split(r"</?[Dd][Ii][Vv][^>]*>", body1)]
paras1 = [p for p in paras1 if 80 <= len(p) <= 600 and "新浪BLOG意见反馈" not in p and "About Sina" not in p]
print("韩寒 春萍 paras:", len(paras1))

# 2. 韩寒《地震思考录》
h2 = get("http://blog.sina.com.cn/s/blog_4701280b0102egl0.html")
m2 = re.search(r'id="sina_keyword_ad_area2"(.*)', h2, re.S)
body2 = m2.group(1)[:200000] if m2 else h2
paras2 = [strip(p) for p in re.split(r"</?[Dd][Ii][Vv][^>]*>", body2)]
paras2 = [p for p in paras2 if 80 <= len(p) <= 600 and "新浪BLOG意见反馈" not in p and "About Sina" not in p]
print("韩寒 地震思考录 paras:", len(paras2))

# 3. 阮一峰博客 2011/2012
try:
    ruan = get("https://www.ruanyifeng.com/blog/2011/10/steve_jobs.html")
    m_ruan = re.search(r'<div class="asset-body"[^>]*>(.*?)<div id="more"', ruan, re.S) or re.search(r'<article[^>]*>(.*?)</article>', ruan, re.S)
    body_r = m_ruan.group(1) if m_ruan else ruan
    paras_r = [strip(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", body_r, re.S)]
    paras_r = [p for p in paras_r if 80 <= len(p) <= 600]
    print("阮一峰 乔布斯传 paras:", len(paras_r))
except Exception as e:
    print("阮一峰 fail:", e)
