import os
import re
import json
import datetime
import urllib.request

# ---------- دریافت کلید ----------
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: API Key not found.")
    raise SystemExit(1)

MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest", "gemini-1.5-flash"]
PROMPT = """
You are an expert in Civil Engineering and Lean Construction.
Write a 600-word professional article on a practical topic related to Lean Construction in the Persian language.
Return ONLY raw HTML. No markdown formatting.
Use <h1> for the title, <h2> for sections, and <p> for paragraphs.
"""

def call_gemini(model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": PROMPT}]}], "generationConfig": {"temperature": 0.8}}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["candidates"][0]["content"]["parts"][0]["text"]

# ---------- تولید مقاله ----------
article_html = None
for model in MODELS:
    try:
        raw = call_gemini(model)
        article_html = raw.replace("```html", "").replace("```", "").strip()
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")

if not article_html:
    raise SystemExit(1)

today = datetime.datetime.now().strftime("%Y-%m-%d")

# استخراج عنوان برای استفاده در تب مرورگر
def get_title(html):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Lean Construction Article"

def get_excerpt(html):
    m = re.search(r"<p[^>]*>(.*?)</p>", html, re.S | re.I)
    s = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Latest insights on Lean Construction."
    return (s[:150] + "...") if len(s) > 150 else s

title = get_title(article_html)
excerpt = get_excerpt(article_html)
filename = f"post-{today}.html"

# ---------- ساخت ظاهر صفحه مقاله (با هدر و فوتر — هم‌قالب با بقیه سایت) ----------
full_article_page = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | محمد بلوچی</title>
<meta name="description" content="{excerpt}">
<meta name="theme-color" content="#0a0a0c">
<link rel="icon" type="image/svg+xml" href="../images/favicon.svg">
<link rel="stylesheet" href="../css/style.css">
</head>
<body>
<header class="site-header">
  <nav class="nav">
    <a href="../index.html" class="brand">
      <span class="brand-mark">MB</span>
      <span class="brand-text"><b>محمد بلوچی</b><span>CONSTRUCTION MGMT.</span></span>
    </a>
    <button class="nav-toggle" aria-label="باز کردن منو">☰</button>
    <ul class="nav-links">
      <li><a href="../index.html">درباره مشاور</a></li>
      <li><a href="../services.html">خدمات</a></li>
      <li><a href="../resume.html">رزومه مشاور</a></li>
      <li><a href="../blog/index.html" class="active">مقالات</a></li>
      <li><a href="../contact.html" class="nav-cta">تماس با من</a></li>
    </ul>
  </nav>
</header>

<section style="padding:56px 0 20px;">
  <div class="wrap article">
    <div class="eyebrow">LEAN CONSTRUCTION</div>
    <h1>{title}</h1>
{article_html}
    <div class="alt" style="margin-top:40px;border-radius:var(--radius);padding:32px;text-align:center;">
      <h2 style="margin-top:0;font-size:19px;">می‌خواهید این موضوع را در پروژه‌ی خود پیاده‌سازی کنید؟</h2>
      <p style="color:var(--ink-soft);margin:10px 0 20px;">در یک جلسه مشاوره کوتاه، وضعیت فعلی پروژه‌ی شما را بررسی می‌کنم.</p>
      <a href="../contact.html" class="btn btn-amber">درخواست مشاوره</a>
    </div>
  </div>
</section>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="brand" style="color:var(--ink-on-navy);">
        <span class="brand-mark">MB</span>
        <span class="brand-text"><b>محمد بلوچی</b><span>مشاور مدیریت ساخت</span></span>
      </div>
      <ul class="footer-links">
        <li><a href="../index.html">درباره مشاور</a></li>
        <li><a href="../services.html">خدمات</a></li>
        <li><a href="../resume.html">رزومه مشاور</a></li>
        <li><a href="../blog/index.html">مقالات</a></li>
        <li><a href="../contact.html">تماس</a></li>
      </ul>
    </div>
    <div class="footer-bottom">
      <span>© ۲۰۲۶ محمد بلوچی — تمامی حقوق محفوظ است</span>
      <span>balouchi@gmail.com · +98 912 820 0682</span>
    </div>
  </div>
</footer>
<script src="../js/main.js"></script>
</body>
</html>"""

os.makedirs("articles", exist_ok=True)
with open(f"articles/{filename}", "w", encoding="utf-8") as f:
    f.write(full_article_page)

# ---------- ثبت مقاله در data/posts.json (منبع واحد نمایش مقالات در کل سایت) ----------
# مقاله‌ها در صفحه اصلی، صفحه مقالات و نسخه انگلیسی همه از data/posts.json خوانده می‌شوند؛
# بنابراین به‌جای تزریق HTML در صفحات، فقط همین فایل به‌روزرسانی می‌شود.
posts_path = "data/posts.json"
if os.path.exists(posts_path):
    with open(posts_path, encoding="utf-8") as f:
        posts_data = json.load(f)

    slug = filename.replace(".html", "")
    if not any(p.get("id") == slug for p in posts_data.get("posts", [])):
        posts_data["posts"].insert(0, {
            "id": slug,
            "status": "published",
            "date": today,
            "icon": "lean",
            "tag_fa": "یادداشت هوش مصنوعی",
            "tag_en": "AI NOTE",
            "title_fa": title,
            "title_en": title,
            "excerpt_fa": excerpt,
            "excerpt_en": excerpt,
            "link_fa": f"articles/{filename}",
            "link_en": ""
        })
        with open(posts_path, "w", encoding="utf-8") as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)
        print("Success! Article registered in data/posts.json (نمایش خودکار در صفحه اصلی و صفحه مقالات).")
    else:
        print("Skipped: this article id is already in posts.json.")
else:
    print("WARNING: data/posts.json not found.")
