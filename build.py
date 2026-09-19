#!/usr/bin/env python3
"""MASU PHOTO の写真集ページを books.json と photobooks/ から生成する。

使い方:
    python3 build.py                 # 全冊を生成し直す
    python3 build.py import <slug> <画像フォルダ>
                                     # フォルダの画像をファイル名順に photobooks/<slug>/ へ取り込む
    python3 build.py indexnow        # 公開後に全URLを Bing 等へ通知する

写真集を1冊足す手順:
    1. books.json に1冊分を追記する（番号・国名・年など）
    2. python3 build.py import <slug> ~/Downloads/<フォルダ>
    3. python3 build.py
    4. git add して push

生成・更新するもの:
    photobooks/<slug>/sm, th   … スマホ・サムネ用の軽い WebP（元画像は触らない）
    covers-thumb, covers-lg    … 表紙が無い冊だけ 1 ページ目から作る
    books/<slug>/, ja/books/<slug>/
    index.html / ja/index.html / partnership/index.html の <!-- BUILD:... --> の間
    トップ・partnership の冊数・国数、sitemap.xml
"""
import datetime
import html
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://masuphoto.fomus.jp"
SRC_EXT = (".jpg", ".jpeg", ".png", ".webp")
SM_WIDTH, TH_WIDTH = 800, 200
TODAY = datetime.date.today().isoformat()
NUM_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
             "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
             "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three",
             "twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight",
             "twenty-nine", "thirty"]


def path(*parts):
    return os.path.join(ROOT, *parts)


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def ver(rel):
    """CSS/JS の更新がブラウザのキャッシュに阻まれないよう、中身のハッシュを ?v= に付ける"""
    import hashlib
    return hashlib.md5(open(path(rel), "rb").read()).hexdigest()[:8]


def esc(s):
    return html.escape(str(s), quote=True)


def write_if_changed(p, text):
    old = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    if old != text:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        print("  updated", os.path.relpath(p, ROOT))


# ---------------------------------------------------------------- 画像

def import_pages(slug, folder):
    """フォルダ内の画像をファイル名の自然順で 001.jpg, 002.jpg … として取り込む。
    JPEG はバイト単位でそのままコピー。PNG 等は元の解像度のまま高品質 JPEG(q92) にする。"""
    folder = os.path.expanduser(folder)
    files = sorted((f for f in os.listdir(folder) if f.lower().endswith(SRC_EXT)), key=natural_key)
    if not files:
        sys.exit(f"画像が見つかりません: {folder}")
    dst = path("photobooks", slug)
    if os.path.isdir(dst) and any(f.lower().endswith(SRC_EXT) for f in os.listdir(dst)):
        sys.exit(f"{dst} には既にページがあります。差し替えるなら先に中身を退避してください。")
    os.makedirs(dst, exist_ok=True)
    for i, f in enumerate(files, 1):
        src = os.path.join(folder, f)
        out = os.path.join(dst, f"{i:03d}.jpg")
        if f.lower().endswith((".jpg", ".jpeg")):
            shutil.copy2(src, out)
        else:
            Image.open(src).convert("RGB").save(out, "JPEG", quality=92, optimize=True, progressive=True)
        print(f"  {f} -> {os.path.basename(out)}")
    print(f"{len(files)} ページを取り込みました。books.json を確認して python3 build.py を実行してください。")


def is_blank(im):
    small = im.convert("RGB").resize((30, 30))
    raw = small.tobytes()
    white = sum(1 for i in range(0, len(raw), 3) if raw[i] > 235 and raw[i + 1] > 235 and raw[i + 2] > 235)
    return white / (len(raw) // 3) > 0.88


def derived(src, dst, width, quality):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=6)


def prepare_pages(book):
    slug = book["slug"]
    folder = path("photobooks", slug)
    files = sorted((f for f in os.listdir(folder) if f.lower().endswith(SRC_EXT)), key=natural_key)
    if not files:
        sys.exit(f"photobooks/{slug}/ にページがありません")
    pages = []
    for f in files:
        src = os.path.join(folder, f)
        stem = os.path.splitext(f)[0]
        im = Image.open(src)
        derived(src, os.path.join(folder, "sm", stem + ".webp"), SM_WIDTH, 82)
        derived(src, os.path.join(folder, "th", stem + ".webp"), TH_WIDTH, 70)
        pages.append({"file": f, "stem": stem, "w": im.width, "h": im.height, "blank": is_blank(im)})
    return pages


def prepare_covers(book, pages):
    """表紙画像が無い冊（新しく足した冊）だけ、1ページ目から作る。"""
    slug = book["slug"]
    first = Image.open(path("photobooks", slug, pages[0]["file"])).convert("RGB")
    for rel, (w, h) in (("covers-thumb", (440, 605)), ("covers-lg", (640, 880))):
        out = path(rel, slug + ".webp")
        if os.path.exists(out):
            continue
        ratio = w / h
        if first.width / first.height > ratio:
            cw = round(first.height * ratio)
            box = ((first.width - cw) // 2, 0, (first.width - cw) // 2 + cw, first.height)
        else:
            ch = round(first.width / ratio)
            box = (0, (first.height - ch) // 2, first.width, (first.height - ch) // 2 + ch)
        first.crop(box).resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=82)
        print("  created", rel + "/" + slug + ".webp")


# ---------------------------------------------------------------- シェア用カード（og:image）
# WebP の og:image は LINE などで表示されないことがあるため、1200x630 の JPEG を作る

OG_W, OG_H = 1200, 630
FONT_EN = "/System/Library/Fonts/Supplemental/Didot.ttc"
FONT_JA = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOLD, TEXT, MUTED = (215, 188, 117), (245, 241, 230), (170, 164, 150)


def _og_canvas():
    from PIL import ImageDraw
    im = Image.new("RGB", (OG_W, OG_H), (13, 13, 13))
    d = ImageDraw.Draw(im)
    for y in range(OG_H):  # 上から下へ、ごく薄い木の色のグラデーション
        t = y / OG_H
        d.line([(0, y), (OG_W, y)], fill=(int(26 - 13 * t), int(20 - 7 * t), int(14 - 1 * t)))
    return im, d


def _font(p, size):
    from PIL import ImageFont
    return ImageFont.truetype(p, size)


def _paste_cover(im, cover, x, y, h):
    from PIL import ImageFilter
    c = Image.open(cover).convert("RGB")
    w = round(c.width * h / c.height)
    c = c.resize((w, h), Image.LANCZOS)
    shadow = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 170), (30, 38, 30 + w, 38 + h))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    im.paste(shadow, (x - 30, y - 30), shadow)
    im.paste(c, (x, y))
    return w


def og_book(book, pages):
    out = path("og", book["slug"] + ".jpg")
    cover = path("covers-lg", book["slug"] + ".webp")
    if os.path.exists(out) and os.path.getmtime(out) >= max(os.path.getmtime(cover), os.path.getmtime(path("books.json"))):
        return
    os.makedirs(path("og"), exist_ok=True)
    im, d = _og_canvas()
    w = _paste_cover(im, cover, 96, 45, 540)
    x = 96 + w + 72
    d.text((x, 150), "MASU  PHOTO", font=_font(FONT_EN, 26), fill=GOLD)
    d.text((x, 196), book["name_en"], font=_font(FONT_EN, 96), fill=TEXT)
    d.text((x, 322), f"Photo Book {book['number']}  ·  {book['year']}  ·  {len(pages)} pages",
           font=_font(FONT_EN, 30), fill=MUTED)
    d.text((x, 380), f"枡フォト写真集｜{book['name_ja']}", font=_font(FONT_JA, 34), fill=TEXT)
    d.text((x, 530), "masuphoto.fomus.jp", font=_font(FONT_EN, 24), fill=GOLD)
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    print("  created og/" + book["slug"] + ".jpg")


def og_site(books):
    """トップ・依頼・作者・枡のページ共通。最新の表紙を並べる"""
    out = path("og", "site.jpg")
    covers = [path("covers-lg", b["slug"] + ".webp") for b in books[-5:]]
    if os.path.exists(out) and os.path.getmtime(out) >= max(os.path.getmtime(c) for c in covers + [path("books.json")]):
        return
    os.makedirs(path("og"), exist_ok=True)
    im, d = _og_canvas()
    x = 60
    for c in covers:
        x += _paste_cover(im, c, x, 160, 270) + 22
    d.text((60, 42), "MASU  PHOTO", font=_font(FONT_EN, 30), fill=GOLD)
    d.text((60, 86), "A wooden vessel traveling the world", font=_font(FONT_EN, 34), fill=TEXT)
    d.text((60, 490), f"{len(books)} photo books  ·  free to read", font=_font(FONT_EN, 30), fill=MUTED)
    d.text((60, 540), "枡フォト写真集 — 枡と旅する写真集", font=_font(FONT_JA, 30), fill=TEXT)
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    print("  created og/site.jpg")


# ---------------------------------------------------------------- 共通パーツ

def reader_html(book, pages, prefix, lang):
    """prefix: ページから見たサイトルートへの相対パス（例 '../../'）"""
    slug = book["slug"]
    ratio = round(pages[0]["w"] / pages[0]["h"], 4)
    name = book["name_en"] if lang == "en" else book["name_ja"]
    imgs = []
    for i, p in enumerate(pages, 1):
        base = f"{prefix}photobooks/{slug}/"
        alt = f"MASU PHOTO {name} — page {i}" if lang == "en" else f"枡フォト写真集 {name} {i}ページ目"
        cls = ' class="is-blank"' if p["blank"] else ""
        loading = "eager" if i <= 2 else "lazy"
        imgs.append(
            f'                <img{cls} src="{base}{p["file"]}" '
            f'srcset="{base}sm/{p["stem"]}.webp {SM_WIDTH}w, {base}{p["file"]} {p["w"]}w" '
            f'sizes="(max-width: 760px) 100vw, 760px" width="{p["w"]}" height="{p["h"]}" '
            f'data-thumb="{base}th/{p["stem"]}.webp" alt="{esc(alt)}" loading="{loading}" decoding="async">')
    head = "Photo Book" if lang == "en" else "写真集を読む"
    prev_l, next_l = ("Previous pages", "Next pages") if lang == "en" else ("前のページ", "次のページ")
    hint = "Drag a page corner, or use the arrow keys" if lang == "en" else "ページの角をつまんで捲れます（矢印キーでも操作できます）"
    return f'''        <section class="reader" id="read" data-reader style="--pr: {ratio}">
            <p class="reader-head">{head}</p>
            <p class="reader-hint">{hint}</p>
            <div class="reader-spread-wrap">
                <div class="reader-spread">
                    <div class="reader-edge reader-edge-left" aria-hidden="true"></div>
                    <div class="reader-book"></div>
                    <div class="reader-edge reader-edge-right" aria-hidden="true"></div>
                    <button class="reader-nav prev" type="button" aria-label="{prev_l}">‹</button>
                    <button class="reader-nav next" type="button" aria-label="{next_l}">›</button>
                </div>
                <p class="reader-indicator" aria-live="polite"></p>
                <div class="reader-thumbs"></div>
            </div>
            <div class="reader-scroll">
{chr(10).join(imgs)}
            </div>
        </section>'''


def shelf_cards(books, lang, href_prefix, cover_prefix, year_key, alt_style):
    out = []
    for b in books:
        name = b["name_en"] if lang == "en" else b["name_ja"]
        cls = "book-cover book-cover-flat" if b.get("flat_cover") else "book-cover"
        if lang == "en":
            alt, title = f"MASU PHOTO {name} cover", f"MASU PHOTO｜{name}"
        else:
            alt = f"枡フォト写真集 {name}（{b['name_en']}）の表紙" if alt_style == "home" else f"枡フォト写真集 {name}の表紙"
            title = f"MASU PHOTO｜{b['name_en']}"  # 日本語版も英語表記でそろえる（2026-09 MaSU 指示）
        out.append(f'''                <a class="book-card" href="{href_prefix}{b['slug']}/">
                    <div class="{cls}">
                        <img src="{cover_prefix}covers-thumb/{b['slug']}.webp" width="440" height="605" alt="{esc(alt)}" loading="lazy">
                    </div>
                    <div class="book-meta">
                        <h3>{esc(title)}</h3>
                        <span class="book-year">{esc(b[year_key])}</span>
                    </div>
                </a>
''')
    return "\n".join(out)


# ---------------------------------------------------------------- 書籍ページ

def book_page_en(book, pages, books, countries):
    s, n, y, name = book["slug"], book["number"], book["year"], book["name_en"]
    cnt = len(pages)
    url = f"{SITE}/books/{s}/"
    edition = f'\n                    <dt>Edition</dt><dd>{esc(book["edition"])}</dd>' if book.get("edition") else ""
    others = [b for b in books if b["slug"] != s]
    total = len(books)
    return f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0">
    <script>document.documentElement.classList.remove("no-js");</script>
    <title>MASU PHOTO | {name} — Photo Book {n} ({y}), {cnt} pages free to read</title>
    <meta name="description" content="MASU PHOTO {name} is book {n} in the series. Photographed in {name} in {y}, all {cnt} pages are free to read online. By MaSU (KEI), founder of FOMUS.">
    <meta name="keywords" content="MASU PHOTO {name}, masu photo, masu photo books, {name} photo book, 枡フォト {name}, FOMUS, MaSU KEI">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="en" href="{url}">
    <link rel="alternate" hreflang="ja" href="{SITE}/ja/books/{s}/">
    <link rel="alternate" hreflang="x-default" href="{url}">
    <meta property="og:type" content="book">
    <meta property="og:site_name" content="MASU PHOTO">
    <meta property="og:locale" content="en_US">
    <meta property="og:title" content="MASU PHOTO | {name} — Photo Book {n} ({y})">
    <meta property="og:description" content="Photographed in {name} in {y}. All {cnt} pages free to read.">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{SITE}/og/{s}.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="MASU PHOTO | {name}">
    <meta name="twitter:description" content="{y} · {name}. All {cnt} pages free to read.">
    <meta name="twitter:image" content="{SITE}/og/{s}.jpg">
    <meta name="theme-color" content="#0d0d0d">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Book",
        "name": "MASU PHOTO | {name}",
        "alternateName": "枡フォト写真集｜{name}",
        "description": "Book {n} of the MASU PHOTO series. Photographed in {name} in {y}, {cnt} pages.",
        "abstract": {json.dumps(book.get("story_en", ""), ensure_ascii=False)},
        "datePublished": "{book['date_published']}",
        "numberOfPages": {cnt},
        "url": "{url}",
        "image": "{SITE}/covers-lg/{s}.webp",
        "inLanguage": "en",
        "isAccessibleForFree": true,
        "author": {{
            "@type": "Person",
            "@id": "{SITE}/#person-masu",
            "name": "MaSU (KEI)",
            "sameAs": ["https://www.instagram.com/masumasumasuo7/"]
        }},
        "publisher": {{ "@type": "Organization", "@id": "https://www.fomus.jp/#organization", "name": "FOMUS", "url": "https://www.fomus.jp/" }},
        "isPartOf": {{
            "@type": "BookSeries",
            "name": "MASU PHOTO Book Series",
            "url": "{SITE}/#photo-books"
        }}
    }}
    </script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{ "@type": "ListItem", "position": 1, "name": "MASU PHOTO", "item": "{SITE}/" }},
            {{ "@type": "ListItem", "position": 2, "name": "Photo Books", "item": "{SITE}/#photo-books" }},
            {{ "@type": "ListItem", "position": 3, "name": "{name}", "item": "{url}" }}
        ]
    }}
    </script>
    <style>.no-js [data-animate]{{opacity:1;transform:none;}}</style>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&family=Noto+Sans+JP:wght@200;300;400&family=Shippori+Mincho:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../styles.css?v={ver("styles.css")}">
    <link rel="stylesheet" href="../../book.css?v={ver("book.css")}">
    <link rel="stylesheet" href="../../info.css?v={ver("info.css")}">
</head>
<body>
    <div class="noise"></div>

    <header class="site-header">
        <a class="brand" href="../../">MASU PHOTO</a>
        <div class="header-right">
            <a class="lang-toggle" href="../../ja/books/{s}/" hreflang="ja" lang="ja">EN / 日本語</a>
        </div>
        <nav id="site-menu">
            <a href="../../">Home</a>
            <a href="../../#photo-books">Photo Books</a>
            <a href="../../about/">About</a>
            <a href="../../masu/">Why Masu</a>
            <a href="../../commission/">Commission</a>
        </nav>
    </header>

    <main>
        <nav class="crumb" aria-label="Breadcrumb">
            <a href="../../">MASU PHOTO</a>
            <span>›</span>
            <a href="../../#photo-books">Photo Books</a>
            <span>›</span>
            <span aria-current="page">{name}</span>
        </nav>

        <section class="book-detail" data-animate>
            <div class="book-detail-cover">
                <a href="#read">
                    <img src="../../covers-lg/{s}.webp" width="640" height="880"
                         alt="MASU PHOTO {name} — Photo Book {n} cover" fetchpriority="high">
                </a>
            </div>
            <div class="book-detail-body">
                <p class="label">MASU PHOTO　Photo Book {n}</p>
                <h1>MASU PHOTO｜{name}</h1>
                <dl class="book-facts">
                    <dt>Location</dt><dd>{name}</dd>
                    <dt>Year</dt><dd>{y}</dd>{edition}
                    <dt>Pages</dt><dd>{cnt} pages</dd>
                    <dt>Photographed by</dt><dd>MaSU (KEI), founder of FOMUS</dd>
                    <dt>Access</dt><dd>Free, no sign-up</dd>
                </dl>
                {f'<p class="book-story">{esc(book["story_en"])}</p>' if book.get("story_en") else ""}
                <p class="book-note">Book {n} of the MASU PHOTO series. Photographed in {name} in {y}, all {cnt} pages are free to read online.</p>
                <a class="btn" href="#read">Read the photo book　↓</a>
            </div>
        </section>

{reader_html(book, pages, "../../", "en")}

        <section class="book-cta" data-animate>
            <p class="label">COMMISSION</p>
            <h2>Make the next volume, of your place</h2>
            <p>MASU PHOTO makes one photo book per country or region — the people of your place, photographed with the masu and published as the next volume. For city and destination promotion.</p>
            <a class="btn" href="../../commission/">Start a photo book project</a>
        </section>

        <section class="section-bookshelf" id="other-books">
            <div class="bookshelf-header" data-animate>
                <h2>Other photo books</h2>
                <p>MASU PHOTO is {NUM_WORDS[total]} books across {NUM_WORDS[countries]} countries.</p>
            </div>
            <div class="bookshelf-scroll" data-animate>
{shelf_cards(others, "en", "../", "../../", "year", "book")}            </div>
        </section>
    </main>

    <footer class="site-footer">
        <p>&copy; MASU PHOTO ONLINE ARCHIVE</p>
    </footer>

    <script src="../../script.js?v={ver("script.js")}"></script>
    <script src="../../vendor/page-flip.browser.js?v={ver("vendor/page-flip.browser.js")}"></script>
    <script src="../../reader.js?v={ver("reader.js")}"></script>
</body>
</html>
'''


def book_page_ja(book, pages, books, countries):
    s, n, y, name, en = book["slug"], book["number"], book["year"], book["name_ja"], book["name_en"]
    cnt = len(pages)
    url = f"{SITE}/ja/books/{s}/"
    others = [b for b in books if b["slug"] != s]
    total = len(books)
    return f'''<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0">
    <script>document.documentElement.classList.remove("no-js");</script>
    <title>枡フォト写真集｜{name}（第{n}巻・{y}）— 全{cnt}ページを無料公開</title>
    <meta name="description" content="枡フォト写真集シリーズ第{n}巻。{y}年に{name}で撮影した全{cnt}ページを、オンラインで無料公開しています。撮影はFOMUS代表のMaSU（KEI）。">
    <meta name="keywords" content="枡フォト,枡フォト写真集,枡フォト {name},MASU PHOTO {en},masu photo,{name} 写真集,FOMUS">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="ja" href="{url}">
    <link rel="alternate" hreflang="en" href="{SITE}/books/{s}/">
    <link rel="alternate" hreflang="x-default" href="{SITE}/books/{s}/">
    <meta property="og:type" content="book">
    <meta property="og:site_name" content="枡フォト｜MASU PHOTO">
    <meta property="og:locale" content="ja_JP">
    <meta property="og:title" content="枡フォト写真集｜{name}（第{n}巻・{y}）">
    <meta property="og:description" content="{y}年に{name}で撮影した枡フォト写真集 第{n}巻。全{cnt}ページを無料公開。">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{SITE}/og/{s}.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="枡フォト写真集｜{name}">
    <meta name="twitter:description" content="{y}年・{name}。全{cnt}ページを無料で読めます。">
    <meta name="twitter:image" content="{SITE}/og/{s}.jpg">
    <meta name="theme-color" content="#0d0d0d">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Book",
        "name": "枡フォト写真集｜{name}",
        "alternateName": "MASU PHOTO | {en}",
        "description": "枡フォト写真集シリーズ第{n}巻。{y}年に{name}で撮影した全{cnt}ページの写真集。",
        "abstract": {json.dumps(book.get("story_ja", ""), ensure_ascii=False)},
        "datePublished": "{book['date_published']}",
        "numberOfPages": {cnt},
        "url": "{url}",
        "image": "{SITE}/covers-lg/{s}.webp",
        "inLanguage": "ja",
        "isAccessibleForFree": true,
        "author": {{
            "@type": "Person",
            "@id": "{SITE}/#person-masu",
            "name": "MaSU（KEI）",
            "alternateName": ["まっすー", "増尾圭亮"],
            "sameAs": ["https://www.instagram.com/masumasumasuo7/"]
        }},
        "publisher": {{ "@type": "Organization", "@id": "https://www.fomus.jp/#organization", "name": "FOMUS", "url": "https://www.fomus.jp/" }},
        "isPartOf": {{
            "@type": "BookSeries",
            "name": "枡フォト写真集シリーズ",
            "url": "{SITE}/ja/"
        }}
    }}
    </script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{ "@type": "ListItem", "position": 1, "name": "枡フォト", "item": "{SITE}/ja/" }},
            {{ "@type": "ListItem", "position": 2, "name": "写真集シリーズ", "item": "{SITE}/ja/#photo-books" }},
            {{ "@type": "ListItem", "position": 3, "name": "{name}", "item": "{url}" }}
        ]
    }}
    </script>
    <style>
      .no-js [data-animate]{{opacity:1;transform:none;}}
      h1, h2, h3, p {{ line-break: strict; }}
    </style>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&family=Noto+Sans+JP:wght@200;300;400&family=Shippori+Mincho:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../../styles.css?v={ver("styles.css")}">
    <link rel="stylesheet" href="../../../book.css?v={ver("book.css")}">
    <link rel="stylesheet" href="../../../info.css?v={ver("info.css")}">
</head>
<body>
    <div class="noise"></div>

    <header class="site-header">
        <a class="brand" href="../../">枡フォト</a>
        <div class="header-right">
            <a class="lang-toggle" href="../../../books/{s}/" hreflang="en" lang="en">JA / EN</a>
        </div>
        <nav id="site-menu">
            <a href="../../">ホーム</a>
            <a href="../../#photo-books">写真集</a>
            <a href="../../about/">作者について</a>
            <a href="../../masu/">枡について</a>
            <a href="../../commission/">写真集プロジェクト</a>
        </nav>
    </header>

    <main>
        <nav class="crumb" aria-label="パンくずリスト">
            <a href="../../">枡フォト</a>
            <span>›</span>
            <a href="../../#photo-books">写真集シリーズ</a>
            <span>›</span>
            <span aria-current="page">{name}</span>
        </nav>

        <section class="book-detail" data-animate>
            <div class="book-detail-cover">
                <a href="#read">
                    <img src="../../../covers-lg/{s}.webp" width="640" height="880"
                         alt="枡フォト写真集｜{name}（第{n}巻）の表紙" fetchpriority="high">
                </a>
            </div>
            <div class="book-detail-body">
                <p class="label">枡フォト写真集　第{n}巻</p>
                <h1>枡フォト写真集｜{name}</h1>
                <dl class="book-facts">
                    <dt>撮影地</dt><dd>{name}</dd>
                    <dt>年</dt><dd>{y}</dd>
                    <dt>収録ページ数</dt><dd>全{cnt}ページ</dd>
                    <dt>撮影</dt><dd>MaSU（KEI）／FOMUS 代表</dd>
                    <dt>閲覧</dt><dd>無料・登録不要</dd>
                </dl>
                {f'<p class="book-story">{esc(book["story_ja"])}</p>' if book.get("story_ja") else ""}
                <p class="book-note">枡フォト写真集シリーズの第{n}巻です。{y}年に{name}で撮影した全{cnt}ページを、オンラインで無料公開しています。</p>
                <a class="btn" href="#read">写真集を読む　↓</a>
            </div>
        </section>

{reader_html(book, pages, "../../../", "ja")}

        <section class="book-cta" data-animate>
            <p class="label">写真集プロジェクト</p>
            <h2>次の1冊を、あなたの国・地域で</h2>
            <p>枡フォトは、国や地域ごとに1冊の写真集をつくるプロジェクトです。その土地の人々を枡と一緒に撮影し、シリーズの新しい1冊として公開します。シティプロモーションや観光PRにご活用ください。</p>
            <a class="btn" href="../../commission/">写真集プロジェクトを相談する</a>
        </section>

        <section class="section-bookshelf" id="other-books">
            <div class="bookshelf-header" data-animate>
                <h2>他の枡フォト写真集</h2>
                <p>枡フォトは全{total}冊、{countries}カ国を旅した記録です。</p>
            </div>
            <div class="bookshelf-scroll" data-animate>
{shelf_cards(others, "ja", "../", "../../../", "year", "book")}            </div>
        </section>
    </main>

    <footer class="site-footer">
        <p>&copy; 枡フォト｜MASU PHOTO ONLINE ARCHIVE</p>
    </footer>

    <script src="../../../script.js?v={ver("script.js")}"></script>
    <script src="../../../vendor/page-flip.browser.js?v={ver("vendor/page-flip.browser.js")}"></script>
    <script src="../../../reader.js?v={ver("reader.js")}"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- トップ等の差し込み

def replace_block(text, name, content, p):
    pat = re.compile(r"(<!-- BUILD:%s -->).*?(<!-- /BUILD:%s -->)" % (name, name), re.S)
    if not pat.search(text):
        sys.exit(f"{p} に <!-- BUILD:{name} --> が見つかりません")
    return pat.sub(lambda m: m.group(1) + "\n" + content + m.group(2), text)


def series_jsonld_en(books, countries):
    parts = [b["name_en"] for b in books if b["slug"] != "world"]
    listed = ", ".join(parts) + (" and a World edition" if any(b["slug"] == "world" for b in books) else "")
    items = ",\n".join(
        f'            {{"@type": "Book", "name": "MASU PHOTO | {b["name_en"]}", "datePublished": "{b["date_published"]}", "url": "{SITE}/books/{b["slug"]}/"}}'
        for b in books)
    return f'''    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "MASU PHOTO Book Series",
        "description": "{len(books)} photo books documenting a wooden MASU vessel's journey across {countries} countries, including {listed}.",
        "url": "{SITE}/#photo-books",
        "numberOfItems": {len(books)},
        "hasPart": [
{items}
        ]
    }}
    </script>
'''


def series_jsonld_ja(books, countries):
    items = ",\n".join(f'''            {{
                "@type": "ListItem",
                "position": {i},
                "url": "{SITE}/ja/books/{b["slug"]}/",
                "name": "枡フォト写真集｜{b["name_ja"]}"
            }}''' for i, b in enumerate(books, 1))
    return f'''    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "枡フォト写真集シリーズ",
        "description": "枡とともに世界{countries}カ国を旅した写真集シリーズ 全{len(books)}冊。",
        "numberOfItems": {len(books)},
        "itemListElement": [
{items}
        ]
    }}
    </script>
'''


def update_counts(text, total, countries):
    """トップ・partnership の本文に散らばる冊数・国数をそろえる。"""
    rules = [
        (r"\b\d+ (free )?photo books\b", lambda m: f"{total} {m.group(1) or ''}photo books"),
        (r"\b\d+ MASU PHOTO books\b", lambda m: f"{total} MASU PHOTO books"),
        (r"\b\d+ countries\b", lambda m: f"{countries} countries"),
        (r"全\d+冊", lambda m: f"全{total}冊"),
        (r"(?<![\d全])\d+冊", lambda m: f"{total}冊"),
        (r"\d+カ国", lambda m: f"{countries}カ国"),
        (r'<span class="p-stat-number">\d+</span>(\s*<span class="p-stat-label" data-i18n="p_stat1")',
         lambda m: f'<span class="p-stat-number">{countries}</span>{m.group(1)}'),
        (r'<span class="p-stat-number">\d+</span>(\s*<span class="p-stat-label" data-i18n="p_stat2")',
         lambda m: f'<span class="p-stat-number">{total}</span>{m.group(1)}'),
    ]
    for pat, rep in rules:
        text = re.sub(pat, rep, text)
    return text


def faq_count_en(text, books):
    def yr(b):
        return b["year_shelf"].replace(" / ", "/")
    parts = [f'{b["name_en"]} ({yr(b)})' for b in books if b["slug"] != "world"]
    world = [b for b in books if b["slug"] == "world"]
    listed = ", ".join(parts) + (f', and a World edition ({yr(world[0])})' if world else "")
    return re.sub(r"There are currently \d+ MASU PHOTO books covering [^\"]*?\. ",
                  f"There are currently {len(books)} MASU PHOTO books covering {listed}. ", text)


def sitemap(books):
    urls = [(f"{SITE}/", "1.0", "weekly"), (f"{SITE}/ja/", "1.0", "weekly"),
            (f"{SITE}/partnership/", "0.6", "monthly")]
    for slug in ("commission", "about", "masu"):
        urls.append((f"{SITE}/{slug}/", "0.9" if slug == "commission" else "0.7", "monthly"))
        urls.append((f"{SITE}/ja/{slug}/", "0.9" if slug == "commission" else "0.7", "monthly"))
    for b in books:
        urls.append((f"{SITE}/books/{b['slug']}/", "0.8", "monthly"))
        urls.append((f"{SITE}/ja/books/{b['slug']}/", "0.8", "monthly"))
    # 写真集ページには、そのページに載っている写真を画像サイトマップとして添える（画像検索からの入口）
    images = {}
    for b in books:
        folder = path("photobooks", b["slug"])
        files = sorted((f for f in os.listdir(folder) if f.lower().endswith(SRC_EXT)), key=natural_key)
        locs = [f"{SITE}/photobooks/{b['slug']}/{f}" for f in files]
        images[f"{SITE}/books/{b['slug']}/"] = locs
        images[f"{SITE}/ja/books/{b['slug']}/"] = locs

    def entry(u, pr, f):
        imgs = "".join(f"\n    <image:image><image:loc>{i}</image:loc></image:image>" for i in images.get(u, []))
        return f"""  <url>
    <loc>{u}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{f}</changefreq>
    <priority>{pr}</priority>{imgs}
  </url>"""
    body = "\n".join(entry(u, pr, f) for u, pr, f in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + body + "\n</urlset>\n")


def llms_txt(books, countries):
    """AI 向けの案内（llmstxt.org の形式）。サイトの要点と主要ページへの入口だけを書く"""
    lines = [f"# MASU PHOTO（枡フォト）", "",
             f"> MASU PHOTO is a photography project by MaSU (KEI, Keisuke Masuo), founder of FOMUS LLC (合同会社FOMUS). "
             f"Carrying a masu — a traditional Japanese wooden vessel and good-luck charm whose name echoes 'to increase' — "
             f"MaSU photographs people around the world. {len(books)} photo books from {countries} countries, all free to read on this site. "
             f"MASU PHOTO takes photo book projects: one book per country or region, for city and destination promotion, commissioned by national tourism boards, municipalities, DMOs and regional companies, with embassies and consulates welcome as non-paying partners (quoted individually; no individual portrait sessions). Optional promotion after publication: social media, social media advertising, video production, exhibitions and events, with a results report.", "",
             "## Photo book projects / 写真集プロジェクトのご依頼",
             f"- [Commission (EN)]({SITE}/commission/): one MASU PHOTO book per country or region, for city and destination promotion",
             f"- [写真集プロジェクトのご依頼 (JA)]({SITE}/ja/commission/): 国・地域ごとに1冊の写真集をつくるプロジェクト（シティプロモーション・観光PR）", "",
             "## About",
             f"- [About MaSU (KEI) and FOMUS]({SITE}/about/)", f"- [作者について]({SITE}/ja/about/)",
             f"- [Why the masu]({SITE}/masu/)", f"- [枡について]({SITE}/ja/masu/)", "",
             "## Photo books / 写真集"]
    for b in books:
        lines.append(f"- [Book {b['number']}: {b['name_en']} ({b['year']})]({SITE}/books/{b['slug']}/) / "
                     f"[第{b['number']}巻 {b['name_ja']}]({SITE}/ja/books/{b['slug']}/)")
    lines += ["", "## Company", "- [FOMUS (fomus.jp)](https://www.fomus.jp/)", "- [MASU-STORE — buy a masu](https://masu.fomus.jp/)", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- main

def build():
    data = json.load(open(path("books.json"), encoding="utf-8"))
    books = sorted(data["books"], key=lambda b: b["number"])
    countries = data["countries"]
    total = len(books)

    for b in books:
        print(f"[{b['number']:>2}] {b['name_en']}")
        pages = prepare_pages(b)
        prepare_covers(b, pages)
        og_book(b, pages)
        write_if_changed(path("books", b["slug"], "index.html"), book_page_en(b, pages, books, countries))
        write_if_changed(path("ja", "books", b["slug"], "index.html"), book_page_ja(b, pages, books, countries))

    og_site(books)

    p = path("index.html")
    t = open(p, encoding="utf-8").read()
    t = replace_block(t, "shelf", shelf_cards(books, "en", "books/", "", "year_shelf", "home") + "            ", p)
    t = replace_block(t, "series-jsonld", series_jsonld_en(books, countries), p)
    t = faq_count_en(update_counts(t, total, countries), books)
    write_if_changed(p, t)

    p = path("ja", "index.html")
    t = open(p, encoding="utf-8").read()
    t = replace_block(t, "shelf", shelf_cards(books, "ja", "books/", "../", "year_shelf", "home") + "            ", p)
    t = replace_block(t, "series-jsonld", series_jsonld_ja(books, countries), p)
    write_if_changed(p, update_counts(t, total, countries))

    p = path("partnership", "index.html")
    t = open(p, encoding="utf-8").read()
    one = "\n".join(f'                <img src="../covers-thumb/{b["slug"]}.webp" width="440" height="605" loading="lazy" alt="{esc(b["name_en"])}" >' for b in books)
    t = replace_block(t, "marquee", one + "\n                <!-- duplicate for seamless loop -->\n" + one + "\n            ", p)
    write_if_changed(p, update_counts(t, total, countries))

    import site_pages
    for lang, base in (("en", ""), ("ja", "ja")):
        write_if_changed(path(base, "commission", "index.html"), site_pages.commission_page(lang, books, countries, total, ver))
        write_if_changed(path(base, "about", "index.html"), site_pages.about_page(lang, books, countries, ver))
        write_if_changed(path(base, "masu", "index.html"), site_pages.masu_page(lang, countries, total, ver))
    write_if_changed(path("llms.txt"), llms_txt(books, countries))

    write_if_changed(path("sitemap.xml"), sitemap(books))
    print(f"done: {total} books, {countries} countries")


INDEXNOW_KEY = "489c3bec7c9aceadf1a612aac5a4527f"  # ルートの <key>.txt と対で置く。消すと Bing 等への通知が認証されない


def indexnow():
    """sitemap.xml の全URLを IndexNow（Bing・Yandex 等が共有）に通知する。push して公開された後に実行する"""
    import urllib.request
    urls = re.findall(r"<loc>([^<]+)</loc>", open(path("sitemap.xml"), encoding="utf-8").read())
    body = json.dumps({"host": "masuphoto.fomus.jp", "key": INDEXNOW_KEY,
                       "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req) as res:
        print(f"IndexNow: {len(urls)} URLs -> HTTP {res.status}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "indexnow":
        indexnow()
    elif len(sys.argv) >= 2 and sys.argv[1] == "import":
        if len(sys.argv) != 4:
            sys.exit("usage: python3 build.py import <slug> <folder>")
        import_pages(sys.argv[2], sys.argv[3])
    else:
        build()
