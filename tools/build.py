#!/usr/bin/env python3
"""Build article pages and data/posts.json from content/posts/*.md

File naming:  content/posts/<slug>.fa.md  and  content/posts/<slug>.en.md
Files starting with "_" are ignored (templates).
Only pages for posts found in content/posts are written. Older articles
(hand-made HTML) are listed in data/posts-legacy.json and are not touched.
"""
import json, re
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lean-construction.ir"
CONTENT = ROOT / "content" / "posts"
TPL = ROOT / "templates"
MANIFEST = ROOT / "tools" / "generated.txt"
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

CFG = {
  "fa": {"tpl": "article.fa.html", "dir": "blog", "css": "../css/style.css", "js": "../js/main.js",
         "htmllang": "fa", "htmldir": "rtl", "locale": "fa_IR", "other": "en",
         "read": lambda n: "%s دقیقه مطالعه" % str(n).translate(FA_DIGITS),
         "cta_h": "می‌خواهید فرایند برنامه‌ریزی هفتگی کارگاهتان را بررسی کنیم؟",
         "cta_p": "در یک بررسی یک‌هفته‌ای، فهرست محدودیت‌ها، look-ahead و PPC شما را با رویه LPS مقایسه می‌کنم و می‌گویم اول چه چیزی را باید درست کرد.",
         "cta_b": "درخواست مشاوره", "cta_l": "/fa/contact.html", "title_suffix": " | محمد بلوچی"},
  "en": {"tpl": "article.en.html", "dir": "en/blog", "css": "../../css/style.css", "js": "../../js/main.js",
         "htmllang": "en", "htmldir": "ltr", "locale": "en_US", "other": "fa",
         "read": lambda n: "%s MIN READ" % n,
         "cta_h": "Want a review of how your site plans its week?",
         "cta_p": "In a one-week review, I compare your constraint log, look-ahead and PPC with LPS practice and tell you what to fix first.",
         "cta_b": "Request a Consultation", "cta_l": "/contact.html", "title_suffix": " | Mohammad Balouchi"},
}


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise SystemExit("ERROR: %s must start with a --- frontmatter block" % path.name)
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip()] = v
    for req in ("slug", "date", "title", "excerpt"):
        if not meta.get(req):
            raise SystemExit("ERROR: %s is missing '%s'" % (path.name, req))
    if not re.fullmatch(r"[a-z0-9-]+", meta["slug"]):
        raise SystemExit("ERROR: slug in %s must use a-z, 0-9 and - only" % path.name)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"]):
        raise SystemExit("ERROR: date in %s must look like 2026-11-23" % path.name)
    return meta, m.group(2).strip()


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def main():
    posts = {}
    for f in sorted(CONTENT.glob("*.md")):
        if f.name.startswith("_"):
            continue
        m = re.match(r"^(.+)\.(fa|en)\.md$", f.name)
        if not m:
            print("skip (name must end .fa.md or .en.md):", f.name)
            continue
        meta, body = parse(f)
        if meta["slug"] != m.group(1):
            raise SystemExit("ERROR: slug in %s must equal the file name (%s)" % (f.name, m.group(1)))
        posts.setdefault(meta["slug"], {})[m.group(2)] = (meta, body)

    written, entries = [], []
    for slug, langs in posts.items():
        base = langs.get("en", langs.get("fa"))[0]
        if base.get("status", "published") != "published":
            print("draft, skipped:", slug)
            continue
        links = {lang: "%s/%s.html" % (CFG[lang]["dir"], slug) for lang in langs}
        for lang, (meta, body) in langs.items():
            c = CFG[lang]
            tpl = (TPL / c["tpl"]).read_text(encoding="utf-8")
            html_body = markdown.markdown(body, extensions=["extra"])
            full = meta["title"] + c["title_suffix"]
            url = "%s/%s" % (SITE, links[lang])
            read = c["read"](meta.get("read_time", "5"))
            eyebrow = ("%s · %s" % (meta.get("tag", "").strip(), read)).strip(" ·")
            alt = "".join('<link rel="alternate" hreflang="%s" href="%s/%s" />\n' % (l, SITE, p) for l, p in links.items())
            alt += '<link rel="alternate" hreflang="x-default" href="%s/%s" />' % (SITE, links.get("en", links.get("fa")))
            o = c["other"]
            switch = "/" + links[o] if o in links else ("/fa/blog/index.html" if o == "fa" else "/blog/index.html")
            ld = json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": full,
                "description": meta["excerpt"], "inLanguage": lang, "datePublished": meta["date"],
                "image": SITE + "/images/og-image.jpg", "mainEntityOfPage": url,
                "author": {"@type": "Person", "name": "Dr. Mohammad Balouchi", "url": SITE + "/",
                           "sameAs": ["https://www.linkedin.com/in/mohammad-balouchi"]}}, ensure_ascii=False)
            lead = ('<p class="lead">%s</p>' % meta["lead"]) if meta.get("lead") else ""
            rep = {"htmllang": c["htmllang"], "htmldir": c["htmldir"], "title": esc(meta["title"]),
                   "full_title": esc(full), "desc": esc(meta["excerpt"]), "url": url, "css": c["css"], "js": c["js"],
                   "alternates": alt, "og_locale": c["locale"], "ld": ld, "eyebrow": esc(eyebrow), "lead": lead,
                   "body": html_body, "cta_h": c["cta_h"], "cta_p": c["cta_p"], "cta_b": c["cta_b"],
                   "cta_l": c["cta_l"], "switch_url": switch}
            for k, v in rep.items():
                tpl = tpl.replace("{{%s}}" % k, v)
            left = re.findall(r"\{\{\w+\}\}", tpl)
            if left:
                raise SystemExit("ERROR: unreplaced placeholders %s in template" % left)
            out = ROOT / links[lang]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(tpl, encoding="utf-8")
            written.append(links[lang])
        fa = langs.get("fa", (None, None))[0]
        en = langs.get("en", (None, None))[0]

        def pick(key, a, b):
            return (a or b or {}).get(key, "")

        entries.append({
            "id": slug, "status": "published", "date": base["date"], "icon": base.get("icon", "lean"),
            "tag_fa": pick("tag", fa, en), "tag_en": pick("tag", en, fa),
            "title_fa": pick("title", fa, en), "title_en": pick("title", en, fa),
            "excerpt_fa": pick("excerpt", fa, en), "excerpt_en": pick("excerpt", en, fa),
            "link_fa": links.get("fa", links.get("en")), "link_en": links.get("en", links.get("fa"))})

    old = MANIFEST.read_text().split() if MANIFEST.exists() else []
    for p in old:
        if p not in written and (ROOT / p).exists():
            (ROOT / p).unlink()
            print("removed", p)
    MANIFEST.write_text("\n".join(sorted(written)) + "\n")

    legacy = json.loads((ROOT / "data" / "posts-legacy.json").read_text(encoding="utf-8"))["posts"]
    ids = {e["id"] for e in entries}
    legacy = [p for p in legacy if p["id"] not in ids]
    pub = [p for p in legacy if p.get("status") == "published"]
    rest = [p for p in legacy if p.get("status") != "published"]
    allp = sorted(entries + pub, key=lambda e: e["date"], reverse=True) + rest
    readme = ("این فایل خودکار از content/posts ساخته می‌شود؛ دستی ویرایش نکن. مقاله‌های قدیمی (HTML دستی) در "
              "data/posts-legacy.json هستند. برای مقاله جدید فقط فایل‌های .fa.md و .en.md را در content/posts بساز.")
    (ROOT / "data" / "posts.json").write_text(
        json.dumps({"_readme": readme, "posts": allp}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("built:", ", ".join(written) or "(nothing)")


if __name__ == "__main__":
    main()
