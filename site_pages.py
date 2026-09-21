"""撮影依頼・作者・枡の3ページ（英語と日本語）。build.py から呼ばれる。

事実として書いてよいのは、このサイトと fomus.jp で公開済みのことだけ。
料金はすべて要見積もり（2026-09 増尾さん決定）。大使館での展示は載せない。
"""
import html
import json


def esc(v):
    return html.escape(str(v), quote=True)

SITE = "https://masuphoto.fomus.jp"
ORG_ID = "https://www.fomus.jp/#organization"
PERSON_ID = f"{SITE}/#person-masu"
FORM_KEY = "c72fa767-1677-4c8c-b48c-407ec1f79896"  # Web3Forms（fomus.jp と共通。届け先 contact@fomus.jp）
CONTACT_EMAIL = "contact@fomus.jp"
PRIVACY_URL = "https://www.fomus.jp/privacy.html"

ORGANIZATION = {
    "@type": "Organization",
    "@id": ORG_ID,
    "name": "FOMUS",
    "legalName": "合同会社FOMUS",
    "url": "https://www.fomus.jp/",
    "foundingDate": "2022-10",
    "founder": {"@id": PERSON_ID},
    "sameAs": ["https://fomusglobal.com/", "https://www.instagram.com/masumasumasuo7/"],
}
PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": "MaSU (KEI)",
    "alternateName": ["増尾圭亮", "まっすー", "Keisuke Masuo"],
    "jobTitle": "Photographer, Founder of FOMUS",
    "worksFor": {"@id": ORG_ID},
    "sameAs": ["https://www.instagram.com/masumasumasuo7/"],
}


def jsonld(obj):
    return ('    <script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=4).replace("\n", "\n    ")
            + "\n    </script>")


def shell(lang, slug, title, desc, body, ld, ver, books_nav=True):
    """slug: 'commission' など。EN は /<slug>/、JA は /ja/<slug>/"""
    en_url, ja_url = f"{SITE}/{slug}/", f"{SITE}/ja/{slug}/"
    url = en_url if lang == "en" else ja_url
    root = "../" if lang == "en" else "../../"
    home = root if lang == "en" else "../"
    if lang == "en":
        brand, toggle = "MASU PHOTO", f'<a class="lang-toggle" href="../ja/{slug}/" hreflang="ja" lang="ja">EN / 日本語</a>'
        nav = [("Home", home), ("Photo Books", home + "#photo-books"), ("About", root + "about/"),
               ("Why Masu", root + "masu/"), ("Commission", root + "commission/"),
               ("Sponsor", root + "sponsor/")]
        site_name, locale, footer = "MASU PHOTO", "en_US", "&copy; MASU PHOTO ONLINE ARCHIVE — masuphoto.fomus.jp"
    else:
        brand, toggle = "枡フォト", f'<a class="lang-toggle" href="../../{slug}/" hreflang="en" lang="en">JA / EN</a>'
        nav = [("ホーム", home), ("写真集", home + "#photo-books"), ("作者について", "../about/"),
               ("枡について", "../masu/"), ("写真集プロジェクト", "../commission/"),
               ("スポンサー", "../sponsor/")]
        site_name, locale, footer = "枡フォト｜MASU PHOTO", "ja_JP", "&copy; 枡フォト｜MASU PHOTO ONLINE ARCHIVE — masuphoto.fomus.jp"
    nav_html = "\n".join(f'            <a href="{h}">{t}</a>' for t, h in nav)
    ld_html = "\n".join(jsonld(o) for o in ld)
    return f'''<!DOCTYPE html>
<html lang="{lang}" class="no-js">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0">
    <script>document.documentElement.classList.remove("no-js");</script>
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="en" href="{en_url}">
    <link rel="alternate" hreflang="ja" href="{ja_url}">
    <link rel="alternate" hreflang="x-default" href="{en_url}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{site_name}">
    <meta property="og:locale" content="{locale}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{SITE}/og/site.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:image" content="{SITE}/og/site.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="theme-color" content="#0d0d0d">
{ld_html}
    <style>.no-js [data-animate]{{opacity:1;transform:none;}}{" h1,h2,h3,p{line-break:strict;}" if lang == "ja" else ""}</style>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&family=Noto+Sans+JP:wght@200;300;400&family=Shippori+Mincho:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{root}styles.css?v={ver("styles.css")}">
    <link rel="stylesheet" href="{root}book.css?v={ver("book.css")}">
    <link rel="stylesheet" href="{root}info.css?v={ver("info.css")}">
</head>
<body>
    <div class="noise"></div>

    <header class="site-header">
        <a class="brand" href="{home}">{brand}</a>
        <div class="header-right">
            {toggle}
            <button class="menu-toggle" aria-label="{"Menu" if lang == "en" else "メニュー"}" aria-expanded="false" aria-controls="site-menu">
                <span></span>
                <span></span>
            </button>
        </div>
        <nav id="site-menu">
{nav_html}
        </nav>
    </header>

    <main class="info">
{body}
    </main>

    <footer class="site-footer">
        <p>{footer}</p>
    </footer>

    <script src="{root}script.js?v={ver("script.js")}"></script>
    <script src="{root}form.js?v={ver("form.js")}"></script>
</body>
</html>
'''


def breadcrumb(lang, slug, name):
    home = f"{SITE}/" if lang == "en" else f"{SITE}/ja/"
    url = f"{SITE}/{slug}/" if lang == "en" else f"{SITE}/ja/{slug}/"
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "MASU PHOTO" if lang == "en" else "枡フォト", "item": home},
        {"@type": "ListItem", "position": 2, "name": name, "item": url}]}


def crumb_html(lang, name):
    home = "../" if lang == "en" else "../"
    label = "Breadcrumb" if lang == "en" else "パンくずリスト"
    top = "MASU PHOTO" if lang == "en" else "枡フォト"
    return f'''        <nav class="crumb" aria-label="{label}">
            <a href="{home}">{top}</a>
            <span>›</span>
            <span aria-current="page">{name}</span>
        </nav>'''


def faq_html(items):
    return "\n".join(f'''                <details class="faq-item">
                    <summary>{q}</summary>
                    <p>{a}</p>
                </details>''' for q, a in items)


def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


# ------------------------------------------------------------------ 写真集プロジェクトのご依頼

COMMISSION = {
    "en": {
        "name": "Commission",
        "title": "A MASU PHOTO Book for Your Country or City — Photo Book Projects for City & Destination Promotion",
        "desc": "MASU PHOTO creates one photo book per country or region: the people of the place, photographed with the masu, Japan's traditional good-luck vessel, and published worldwide as a volume of the series. For national tourism boards, municipalities, DMOs and regional companies, with embassies welcome as partners. Quoted individually.",
        "label": "COMMISSION",
        "h1": "Make a MASU PHOTO book of your country or city",
        "lead": "MASU PHOTO makes one photo book per country or region. We photograph the people of your place holding the masu — a traditional Japanese vessel whose name echoes “to increase” — and publish the result as a new volume of a series that already spans {countries} countries and {total} books. A project for destination and city promotion, cultural exchange and exhibitions.",
        "why_title": "Why a MASU PHOTO book",
        "why": [
            ("A volume in a world series", "Your book is published free to read alongside {total} volumes from {countries} countries, in English and Japanese — a place in a growing international archive, not a one-off campaign."),
            ("Portraits of your people", "Each book is built from the people who live there — faces, streets and light — which is what makes a place feel worth visiting."),
            ("A link to Japan", "The masu is a Japanese good-luck vessel. For places abroad it becomes a story about Japan; for places in Japan, a way to show local people to the world."),
        ],
        "menus_title": "Who we work with",
        "menus": [
            ("01", "National tourism boards", "A national volume for destination promotion abroad, or for a cultural exchange programme with Japan."),
            ("02", "Municipalities, tourism associations & DMOs", "A volume of your city or region for city promotion, tourism and relations with sister cities."),
            ("03", "Regional companies & organisations", "Sponsor or co-produce the volume of the region you belong to, credited in the book."),
            ("04", "Series sponsorship", "Support the MASU PHOTO series as a whole, credited across the online archive and future volumes."),
        ],
        "partners_note": "Embassies and consulates are welcome as partners — through endorsement, local introductions or an exhibition venue — without a fee.",
        "uses_title": "How the book can be used",
        "uses": ["City and destination promotion", "Tourism websites and social media", "Cultural exchange and sister-city programmes",
                 "Exhibitions and events", "Gifts and presentations for guests"],
        "mkt_title": "Promotion after publication",
        "mkt_label": "OPTION",
        "mkt_lead": "We can also take on promotion once the book is finished. Choose what you need; it is quoted together with the book.",
        "mkt": [
            ("Social media", "We share the book and the story of the shoot on social media."),
            ("Social media advertising", "We plan and run ads that reach the countries and audiences you want."),
            ("Video", "We produce videos of the shoot, including short-form video."),
            ("Exhibitions & events", "We plan and run exhibitions of the book and events to launch it."),
            ("Results report", "We report on the results of the promotion — views, reactions and more — for your own reporting and next steps."),
        ],
        "flow_title": "How it works",
        "flow": [("Inquiry", "Tell us the country or region and what you want the book to do."),
                 ("Consultation & quote", "We shape the plan together — places, people, schedule — and send a proposal and quote."),
                 ("Shoot on location", "MaSU photographs the people of your place with the masu."),
                 ("Publication & promotion", "The book is published as a new volume of MASU PHOTO. If you wish, we also take on its promotion.")],
        "price_title": "Pricing",
        "price": "Each project, including any promotion options, is quoted individually according to the region, the scale of the shoot and how the book will be used. Consultations and quotes are free. MASU PHOTO does not take individual portrait sessions.",
        "faq_title": "Questions",
        "faq": [
            ("How much does a project cost?", "Each project is quoted individually according to the region, the scale of the shoot and how the book will be used. Consultations and quotes are free."),
            ("Do you take individual or family portrait sessions?", "No. MASU PHOTO works on photo book projects for countries, regions and the organisations that represent them."),
            ("Can you photograph outside Japan?", "Yes. MASU PHOTO has been photographed in {countries} countries, in Japan and abroad."),
            ("Will the book be published?", "Yes. The finished book is published on this site as a volume of the MASU PHOTO series. The timing and details of publication are agreed with you."),
            ("Can you also handle the promotion?", "Yes. Social media, social media advertising, video production, and exhibitions and events are available as options, and we report on the results."),
            ("Can we use the photographs for our own promotion?", "Yes, how the photographs are used is agreed in the proposal for each project."),
            ("Who is the photographer?", "MaSU (KEI), founder of FOMUS and the photographer of MASU PHOTO."),
        ],
        "form_title": "Inquiry",
        "form_lead": "We will reply by email. Your details are used only to respond to your inquiry.",
        "form": {
            "name": "Name", "org": "Organisation", "email": "Email",
            "type": "Type of organisation", "types": ["National tourism board", "Municipality / tourism association / DMO",
                                                      "Regional company / organisation", "Series sponsorship", "Embassy / consulate (partnership)", "Other"],
            "choose": "Please choose", "where": "Country / region", "where_ph": "e.g. Kyoto, Japan / Lisbon, Portugal",
            "when": "Preferred timing", "when_ph": "e.g. spring 2027", "msg": "Message",
            "msg_ph": "What would you like the book to achieve, and how do you plan to use it?",
            "consent": 'I agree to the <a href="' + PRIVACY_URL + '" target="_blank" rel="noopener">privacy policy</a>.',
            "submit": "Send inquiry", "optional": "optional", "subject": "MASU PHOTO photo book project inquiry",
        },
    },
    "ja": {
        "name": "写真集プロジェクトのご依頼",
        "title": "あなたの国・地域の枡フォト写真集をつくる｜シティプロモーション・観光PRの写真集プロジェクト",
        "desc": "枡フォトは、国や地域ごとに1冊の写真集をつくるプロジェクトです。その土地の人々を、日本の縁起物「枡」と一緒に撮影し、シリーズの1冊として世界に公開します。政府観光局・自治体・観光協会・DMO・地域企業からのご依頼と、大使館・領事館とのご協力を受け付けています。料金はお見積りです。",
        "label": "写真集プロジェクト",
        "h1": "あなたの国・地域の枡フォト写真集をつくる",
        "lead": "枡フォトは、国や地域ごとに1冊の写真集をつくるプロジェクトです。その土地に暮らす人々を、「増す・益す」に通じる日本の縁起物「枡」と一緒に撮影し、{countries}カ国・{total}冊を数えるシリーズの新しい1冊として公開します。シティプロモーションや観光PR、国際交流、展示にご活用いただけます。",
        "why_title": "枡フォトの写真集が、地域の発信に向く理由",
        "why": [
            ("世界シリーズの1冊になる", "{countries}カ国・{total}冊と並んで、日英両方で世界に無料公開されます。一度きりのキャンペーンではなく、広がり続ける国際アーカイブの中に、あなたの地域の1冊が残ります。"),
            ("その土地の「人」が主役", "写真集は、そこに暮らす人の表情と、街並みと、光でできています。訪れたくなる理由は、景色だけでなく人にあります。"),
            ("日本とのつながりが生まれる", "枡は日本の縁起物です。海外の地域にとっては日本との物語に、日本の地域にとっては地元の人を世界へ届ける手段になります。"),
        ],
        "menus_title": "ご依頼いただける団体",
        "menus": [
            ("01", "政府観光局", "海外に向けた国の観光PRや、日本との文化交流事業としての1冊。"),
            ("02", "自治体・観光協会・DMO", "シティプロモーション、観光誘客、姉妹都市との交流に向けた、市や地域の1冊。"),
            ("03", "地域の企業・団体", "自社が根ざす地域の1冊への協賛・共同制作。写真集にお名前を掲載します。"),
            ("04", "シリーズのスポンサー", "枡フォトシリーズ全体を支援いただき、オンラインアーカイブと今後の写真集にお名前を掲載します。"),
        ],
        "partners_note": "大使館・領事館とは、後援や現地のご紹介、展示会場のご提供など、費用をともなわない形でのご協力も歓迎しています。",
        "uses_title": "写真集の活用例",
        "uses": ["シティプロモーション・観光PR", "観光サイト・SNSでの発信", "国際交流・姉妹都市との交流", "展示・イベント", "来賓・視察団への贈呈"],
        "mkt_title": "完成後の発信・マーケティングもお任せください",
        "mkt_label": "オプション",
        "mkt_lead": "写真集が完成したあとの発信まで、まとめてお受けできます。必要なものを選んでいただき、写真集の制作とあわせてお見積りします。",
        "mkt": [
            ("SNSでの発信", "写真集や撮影の様子を、SNSで発信します。"),
            ("SNS広告の運用", "届けたい国や層に向けて、広告を設計・運用します。"),
            ("動画の制作", "撮影の記録やショート動画を制作します。"),
            ("展示・イベントの企画", "写真集の展示や、完成を伝えるイベントを企画・運営します。"),
            ("効果測定レポート", "発信の結果（閲覧数や反応など）をまとめてご報告します。報告書や次の施策の検討にお使いいただけます。"),
        ],
        "flow_title": "ご依頼の流れ",
        "flow": [("お問い合わせ", "対象の国・地域と、写真集で実現したいことをお知らせください。"),
                 ("ヒアリング・お見積り", "撮影する場所・人・スケジュールを一緒に考え、企画とお見積りをお送りします。"),
                 ("現地での撮影", "MaSUが現地に伺い、その土地の人々を枡と一緒に撮影します。"),
                 ("公開・発信", "枡フォトの新しい1冊として公開します。ご希望に応じて、発信・マーケティングまで行います。")],
        "price_title": "料金について",
        "price": "対象地域・撮影の規模・写真集の活用方法、発信・マーケティングのオプションに合わせて、個別にお見積りします。ご相談・お見積りは無料です。なお、個人の方の記念撮影は受け付けていません。",
        "faq_title": "よくあるご質問",
        "faq": [
            ("費用はいくらですか？", "対象地域・撮影の規模・写真集の活用方法に合わせて、個別にお見積りします。ご相談・お見積りは無料です。"),
            ("個人や家族の撮影は依頼できますか？", "受け付けていません。枡フォトは、国や地域、それを代表する団体とつくる写真集プロジェクトです。"),
            ("海外でも撮影できますか？", "はい。枡フォトはこれまで国内外の{countries}カ国で撮影してきました。"),
            ("写真集は公開されますか？", "はい。完成した写真集は、枡フォトシリーズの1冊としてこのサイトで公開します。公開の時期や内容はご相談のうえ決めます。"),
            ("発信やマーケティングもお願いできますか？", "はい。SNSでの発信、SNS広告の運用、動画の制作、展示・イベントの企画を、オプションとしてお受けしています。発信の結果は効果測定レポートでご報告します。"),
            ("写真を自分たちのPRに使えますか？", "はい。写真の使い方は、プロジェクトごとの企画の中でご相談のうえ決めます。"),
            ("誰が撮影しますか？", "枡フォトの撮影者である、FOMUS代表のMaSU（KEI）が撮影します。"),
        ],
        "form_title": "お問い合わせフォーム",
        "form_lead": "メールでご返信します。いただいた情報は、お問い合わせへの対応にのみ使います。",
        "form": {
            "name": "お名前", "org": "団体名・ご所属", "email": "メールアドレス",
            "type": "団体の種類", "types": ["政府観光局", "自治体・観光協会・DMO", "地域の企業・団体", "シリーズのスポンサー", "大使館・領事館（ご協力）", "その他"],
            "choose": "選択してください", "where": "対象の国・地域", "where_ph": "例：山梨県笛吹市／ポルトガル・リスボン",
            "when": "希望時期", "when_ph": "例：2027年春", "msg": "ご相談内容",
            "msg_ph": "写真集で実現したいこと、想定している活用方法などをお書きください",
            "consent": '<a href="' + PRIVACY_URL + '" target="_blank" rel="noopener">プライバシーポリシー</a>に同意のうえ送信します。',
            "submit": "送信する", "optional": "任意", "subject": "枡フォト 写真集プロジェクトのご相談",
        },
    },
}


# 依頼ページの作例（公開済みの写真集のページから、街並みと人が伝わるものを選んだ）
SAMPLES = [("latvia", "004"), ("estonia", "003"), ("spain", "003"),
           ("malaysia", "003"), ("bahrain", "007"), ("world", "005")]


def series_html(lang, books, root):
    covers = "\n".join(
        f'''                <a class="series-book" href="{root}books/{b["slug"]}/">
                    <img src="{root}covers-thumb/{b["slug"]}.webp" width="440" height="605" loading="lazy" alt="{("MASU PHOTO " + b["name_en"]) if lang == "en" else ("枡フォト " + b["name_ja"])}">
                    <span>{b["name_en"] if lang == "en" else b["name_ja"]}</span>
                </a>''' for b in books)
    nxt = len(books) + 1
    slot = (f"Book {nxt}<br>Your country<br>or city" if lang == "en" else f"第{nxt}巻<br>あなたの<br>国・地域")
    return f'''            <div class="series-shelf">
{covers}
                <a class="series-book series-next" href="#inquiry">
                    <div class="series-slot">{slot}</div>
                    <span>{"Next" if lang == "en" else "次の1冊"}</span>
                </a>
            </div>'''


def samples_html(lang, books, root):
    """作例を1枚の枠で切り替えるスライドショー（切り替えは form.js）"""
    names = {b["slug"]: (b["name_en"] if lang == "en" else b["name_ja"]) for b in books}
    slides = "\n".join(
        f'''                    <figure class="slide{" is-active" if i == 0 else ""}">
                        <img src="{root}photobooks/{slug}/sm/{page}.webp" width="800" height="1118" {"" if i == 0 else 'loading="lazy" '}alt="{("MASU PHOTO " + names[slug]) if lang == "en" else ("枡フォト写真集 " + names[slug])}">
                        <figcaption>{names[slug]}</figcaption>
                    </figure>''' for i, (slug, page) in enumerate(SAMPLES))
    dots = "\n".join(f'                    <button type="button" aria-label="{i + 1}"{" aria-current=\"true\"" if i == 0 else ""}></button>' for i in range(len(SAMPLES)))
    return f'''            <div class="slideshow" data-slideshow>
                <div class="slides">
{slides}
                </div>
                <div class="slide-dots">
{dots}
                </div>
            </div>'''


def commission_page(lang, books, countries, total, ver):
    fill = lambda t: t.replace("{countries}", str(countries)).replace("{total}", str(total))
    c = json.loads(fill(json.dumps(COMMISSION[lang], ensure_ascii=False)))
    f = c["form"]
    req = '<span class="req">*</span>'
    opt = f'<span class="opt">{f["optional"]}</span>'
    menus = "\n".join(f'''                <article class="info-card">
                    <p class="info-card-num">{n}</p>
                    <h3>{t}</h3>
                    <p>{d}</p>
                </article>''' for n, t, d in c["menus"])
    flow = "\n".join(f'''                <li><h3>{t}</h3><p>{d}</p></li>''' for t, d in c["flow"])
    why = "\n".join(f'''                <article class="info-point">
                    <h3>{t}</h3>
                    <p>{d}</p>
                </article>''' for t, d in c["why"])
    uses = "\n".join(f'                <li>{u}</li>' for u in c["uses"])
    mkt = "\n".join(f'''                <article class="info-card">
                    <h3>{t}</h3>
                    <p>{d}</p>
                </article>''' for t, d in c["mkt"])
    options = "\n".join(f'                            <option value="{t}">{t}</option>' for t in f["types"])
    ok_msg = ("Thank you. Your inquiry has been sent — we will reply by email."
              if lang == "en" else "送信しました。ありがとうございます。メールでご返信します。")
    ng_msg = (f"Sending failed. Please email us directly at {CONTACT_EMAIL}."
              if lang == "en" else f"送信に失敗しました。お手数ですが {CONTACT_EMAIL} まで直接ご連絡ください。")
    body = f'''{crumb_html(lang, c["name"])}

        <section class="info-hero" data-animate>
            <p class="label">{c["label"]}</p>
            <h1>{c["h1"]}</h1>
            <p class="info-lead">{c["lead"]}</p>
            <a class="btn" href="#inquiry">{"Start a project" if lang == "en" else "相談する"}　↓</a>
        </section>

        <section class="info-series" data-animate>
            <p class="info-series-caption">{("The " + str(total) + " volumes so far — and the next one") if lang == "en" else ("これまでの" + str(total) + "冊と、次の1冊")}</p>
{series_html(lang, books, "../" if lang == "en" else "../../")}
        </section>

        <section class="info-section info-split" data-animate>
            <div class="info-split-text">
                <h2>{"The people of the place, with the masu" if lang == "en" else "その土地の人を、枡と一緒に"}</h2>
                <p>{"Every volume is made of portraits like these — people photographed where they live, each holding the same masu." if lang == "en" else "どの写真集も、こうした一枚一枚でできています。その土地で暮らす人を、その土地の風景の中で、同じ枡と一緒に撮影します。"}</p>
            </div>
{samples_html(lang, books, "../" if lang == "en" else "../../")}
        </section>

        <section class="info-section" data-animate>
            <h2>{c["why_title"]}</h2>
            <div class="info-points">
{why}
            </div>
        </section>

        <section class="info-section" data-animate>
            <h2>{c["menus_title"]}</h2>
            <div class="info-cards">
{menus}
            </div>
            <p class="info-note info-partners">{c["partners_note"]}</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>{c["uses_title"]}</h2>
            <ul class="info-uses">
{uses}
            </ul>
        </section>

        <section class="info-section" data-animate>
            <p class="label">{c["mkt_label"]}</p>
            <h2>{c["mkt_title"]}</h2>
            <p>{c["mkt_lead"]}</p>
            <div class="info-cards info-cards-3">
{mkt}
            </div>
        </section>

        <section class="info-section" data-animate>
            <h2>{c["flow_title"]}</h2>
            <ol class="info-flow">
{flow}
            </ol>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>{c["price_title"]}</h2>
            <p>{c["price"]}</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>{c["faq_title"]}</h2>
            <div class="faq">
{faq_html(c["faq"])}
            </div>
        </section>

        <section class="info-section info-narrow" id="inquiry">
            <h2>{c["form_title"]}</h2>
            <p class="info-note">{c["form_lead"]}</p>
            <form class="inquiry-form" action="https://api.web3forms.com/submit" method="POST"
                  data-ok="{ok_msg}" data-ng="{ng_msg}">
                <input type="hidden" name="access_key" value="{FORM_KEY}">
                <input type="hidden" name="subject" value="{f["subject"]}">
                <input type="hidden" name="from_name" value="MASU PHOTO">
                <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
                <div class="fg-row">
                    <label class="fg"><span class="fg-label">{f["name"]} {req}</span><input type="text" name="name" autocomplete="name" required></label>
                    <label class="fg"><span class="fg-label">{f["org"]} {opt}</span><input type="text" name="organization" autocomplete="organization"></label>
                </div>
                <label class="fg"><span class="fg-label">{f["email"]} {req}</span><input type="email" name="email" autocomplete="email" required></label>
                <label class="fg"><span class="fg-label">{f["type"]} {req}</span>
                    <select name="request_type" required>
                        <option value="">{f["choose"]}</option>
{options}
                    </select>
                </label>
                <div class="fg-row">
                    <label class="fg"><span class="fg-label">{f["where"]} {req}</span><input type="text" name="location" placeholder="{f["where_ph"]}" required></label>
                    <label class="fg"><span class="fg-label">{f["when"]} {opt}</span><input type="text" name="timing" placeholder="{f["when_ph"]}"></label>
                </div>
                <label class="fg"><span class="fg-label">{f["msg"]} {req}</span><textarea name="message" rows="6" placeholder="{f["msg_ph"]}" required></textarea></label>
                <label class="fg-check"><input type="checkbox" name="consent" required><span>{f["consent"]}</span></label>
                <button class="btn" type="submit">{f["submit"]}</button>
                <p class="form-status" role="status" hidden></p>
            </form>
        </section>'''
    url = f"{SITE}/commission/" if lang == "en" else f"{SITE}/ja/commission/"
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": c["h1"],
        "serviceType": "Photo book production for city and destination promotion" if lang == "en" else "シティプロモーション・観光PRのための写真集制作",
        "description": c["desc"],
        "url": url,
        "provider": ORGANIZATION,
        "areaServed": "Worldwide",
        "availableLanguage": ["ja", "en"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": c["menus_title"],
            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t, "description": d},
                                 "priceSpecification": {"@type": "PriceSpecification", "description":
                                                        "Quoted individually" if lang == "en" else "お見積り"}}
                                for _, t, d in c["menus"]]
                               + [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t, "description": d}}
                                  for t, d in c["mkt"]],
        },
    }
    return shell(lang, "commission", c["title"], c["desc"], body,
                 [service, faq_ld(c["faq"]), breadcrumb(lang, "commission", c["name"])], ver)


# ------------------------------------------------------------------ 作者について

def about_page(lang, books, countries, ver):
    total = len(books)
    rows = "\n".join(
        f'                <li><a href="{"../books/" if lang == "en" else "../books/"}{b["slug"]}/">'
        f'<span class="tl-year">{b["year"]}</span>'
        f'<span>{("Book " + str(b["number"]) + " — " + b["name_en"]) if lang == "en" else ("第" + str(b["number"]) + "巻　" + b["name_ja"])}</span></a></li>'
        for b in books)
    if lang == "en":
        name, title = "About", "About MASU PHOTO — MaSU (KEI) and FOMUS"
        desc = f"MASU PHOTO is a photography project by MaSU (KEI), founder of FOMUS, who travels with the masu — Japan's traditional wooden vessel — and has published {total} photo books from {countries} countries."
        body = f'''{crumb_html(lang, name)}

        <section class="info-hero" data-animate>
            <p class="label">ABOUT</p>
            <h1>MaSU (KEI) and FOMUS</h1>
            <p class="info-lead">MASU PHOTO is a photography project by MaSU (KEI), founder of FOMUS. Carrying a masu — a traditional Japanese wooden vessel — MaSU photographs the people and places met along the way. The project has been photographed in {countries} countries and published as {total} photo books, all free to read on this site.</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>The photographer</h2>
            <p>MaSU (KEI) — Keisuke Masuo — is the founder and representative of FOMUS. MaSU is the photographer of MASU PHOTO, from the first volume in Japan in 2022 to the Bahrain volume in 2026.</p>
            <a class="text-link" href="https://www.instagram.com/masumasumasuo7/" target="_blank" rel="noopener">Instagram @masumasumasuo7 →</a>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>FOMUS and the masu</h2>
            <p>FOMUS LLC (合同会社FOMUS, founded October 2022) designs masu made from Japanese hinoki cypress for gifts, businesses and international presentation. Its own processing options include a waterproof coating for professional use, gold leaf, laser printing and branding-iron marks, and masu can be personalised from a single piece.</p>
            <p><a class="text-link" href="https://www.fomus.jp/masu.html" target="_blank" rel="noopener">FOMUS masu →</a>　<a class="text-link" href="https://masu.fomus.jp/" target="_blank" rel="noopener">MASU-STORE →</a></p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>The photo books</h2>
            <ol class="timeline">
{rows}
            </ol>
        </section>

        <section class="info-section info-narrow info-cta" data-animate>
            <h2>A MASU PHOTO book of your place</h2>
            <p>MASU PHOTO makes one photo book per country or region, with countries, municipalities and regional organisations.</p>
            <a class="btn" href="../commission/">Start a photo book project</a>
        </section>'''
    else:
        name, title = "作者について", "作者について｜枡フォト（MASU PHOTO）— MaSU（KEI）とFOMUS"
        desc = f"枡フォト（MASU PHOTO）は、FOMUS代表のMaSU（KEI・増尾圭亮）が、日本の伝統工芸「枡」を手に世界を旅して撮影する写真プロジェクトです。{countries}カ国で撮影し、{total}冊の写真集を公開しています。"
        body = f'''{crumb_html(lang, name)}

        <section class="info-hero" data-animate>
            <p class="label">作者について</p>
            <h1>MaSU（KEI）とFOMUS</h1>
            <p class="info-lead">枡フォト（MASU PHOTO）は、FOMUS代表のMaSU（KEI）による写真プロジェクトです。日本の伝統工芸「枡」を手に旅をし、出会った人と場所を撮影しています。これまでに{countries}カ国で撮影し、{total}冊の写真集として、このサイトですべて無料公開しています。</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>撮影者</h2>
            <p>MaSU（KEI）＝増尾圭亮（まっすー）。合同会社FOMUSの代表です。2022年の日本での第1巻から、2026年のバーレーンの巻まで、枡フォトの撮影者です。</p>
            <a class="text-link" href="https://www.instagram.com/masumasumasuo7/" target="_blank" rel="noopener">Instagram @masumasumasuo7 →</a>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>FOMUSと枡</h2>
            <p>合同会社FOMUS（2022年10月設立）は、国産ヒノキの枡を、ギフト・業務用・海外贈答に向けて設計しています。業務用に耐える防水コーティング、金箔加工、レーザープリント、焼印といった独自の加工に対応し、1個からの名入れもできます。</p>
            <p><a class="text-link" href="https://www.fomus.jp/masu.html" target="_blank" rel="noopener">FOMUSの枡 →</a>　<a class="text-link" href="https://masu.fomus.jp/" target="_blank" rel="noopener">枡の専門店 MASU-STORE →</a></p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>写真集の歩み</h2>
            <ol class="timeline">
{rows}
            </ol>
        </section>

        <section class="info-section info-narrow info-cta" data-animate>
            <h2>あなたの地域の1冊をつくりませんか</h2>
            <p>国・自治体・地域の団体と一緒に、国や地域ごとに1冊の写真集をつくっています。</p>
            <a class="btn" href="../commission/">写真集プロジェクトを相談する</a>
        </section>'''
    url = f"{SITE}/about/" if lang == "en" else f"{SITE}/ja/about/"
    page = {"@context": "https://schema.org", "@type": "AboutPage", "name": title, "url": url,
            "mainEntity": PERSON}
    org = dict(ORGANIZATION, **{"@context": "https://schema.org"})
    return shell(lang, "about", title, desc, body, [page, org, breadcrumb(lang, "about", name)], ver)


# ------------------------------------------------------------------ 枡について

MASU_FAQ = {
    "en": [
        ("What is a masu?", "A masu is a traditional Japanese wooden box that has been used since the Nara period to measure rice and sake."),
        ("Why is the masu a symbol of good luck?", "In Japanese, masu sounds like the verbs 'to increase' and 'to prosper', so the vessel came to stand for growing happiness and prosperity. It is used for weddings and for celebrating the opening of a business."),
        ("Why does MASU PHOTO photograph people with a masu?", "Holding the same masu, people in every country become part of one continuing story. The masu connects portraits taken years and continents apart."),
        ("Where can I buy a masu?", "FOMUS masu, including personalised ones, are available at MASU-STORE (masu.fomus.jp)."),
    ],
    "ja": [
        ("枡とは何ですか？", "枡は、奈良時代から日本で使われてきた木製の計量器です。米や酒を量るための器として使われてきました。"),
        ("枡はなぜ縁起物なのですか？", "「ます」という響きが「増す・益す」に通じることから、幸せや繁栄が増えていくことを願う縁起物になりました。結婚式や開業祝いにも使われます。"),
        ("枡フォトは、なぜ枡を持って撮影するのですか？", "どの国の人も同じ枡を手にすることで、何年も離れ、何千キロも離れた一枚一枚が、ひとつの続いていく物語になるからです。"),
        ("枡はどこで買えますか？", "FOMUSの枡は、名入れのものも含めて、枡の専門店 MASU-STORE（masu.fomus.jp）で購入できます。"),
    ],
}


def masu_page(lang, countries, total, ver):
    faq = MASU_FAQ[lang]
    if lang == "en":
        name, title = "Why Masu", "Why the Masu — Japan's Good-Luck Wooden Vessel | MASU PHOTO"
        desc = "The masu is a traditional Japanese wooden vessel, used since the Nara period to measure rice and sake. Its name echoes 'to increase', making it a symbol of good fortune. Why MASU PHOTO travels the world with it."
        body = f'''{crumb_html(lang, name)}

        <section class="info-hero" data-animate>
            <p class="label">WHY MASU</p>
            <h1>A vessel that means “more”</h1>
            <p class="info-lead">The masu is a small wooden box from Japan. Since the Nara period it has been used to measure rice and sake. Because <em>masu</em> sounds like the words for “to increase” and “to prosper”, it became a symbol of growing happiness — used at weddings and to celebrate new businesses.</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>Why we photograph with it</h2>
            <p>MASU PHOTO asks people in every country to hold the same kind of vessel. In Japan, in Taiwan, in Spain or in Qatar, the same vessel in different hands turns separate portraits into one continuing story. Across {countries} countries and {total} photo books, the masu is the thread.</p>
            <p>The masu used in the photographs are made by FOMUS from Japanese hinoki cypress.</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>Questions about the masu</h2>
            <div class="faq">
{faq_html(faq)}
            </div>
        </section>

        <section class="info-section info-narrow info-cta" data-animate>
            <h2>A MASU PHOTO book of your place</h2>
            <p>MASU PHOTO makes one photo book per country or region, for city and destination promotion.</p>
            <a class="btn" href="../commission/">Start a photo book project</a>
            <p class="info-note"><a class="text-link" href="https://masu.fomus.jp/" target="_blank" rel="noopener">Buy a masu at MASU-STORE →</a></p>
        </section>'''
    else:
        name, title = "枡について", "枡とは｜縁起物「枡」と枡フォト（MASU PHOTO）"
        desc = "枡は奈良時代から米や酒を量ってきた日本の木の器。「増す・益す」に通じる縁起物です。枡フォトが、なぜ枡を手に世界を旅して撮影するのかを紹介します。"
        body = f'''{crumb_html(lang, name)}

        <section class="info-hero" data-animate>
            <p class="label">枡について</p>
            <h1>「増す」を宿す器</h1>
            <p class="info-lead">枡（ます）は、日本の小さな木の器です。奈良時代から、米や酒を量るために使われてきました。「ます」という響きが「増す・益す」に通じることから、幸せや繁栄が増えていくことを願う縁起物となり、結婚式や開業祝いにも使われています。</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>枡フォトが、枡と撮る理由</h2>
            <p>枡フォトは、どの国の人にも同じ枡を手にしてもらって撮影します。日本でも、台湾でも、スペインでも、カタールでも、同じ枡を手にすることで、離れた場所の一枚一枚がひとつの物語としてつながっていきます。{countries}カ国・{total}冊の写真集を貫いているのが、この枡です。</p>
            <p>撮影に使っている枡は、FOMUSが国産ヒノキでつくっています。</p>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>枡についてのよくあるご質問</h2>
            <div class="faq">
{faq_html(faq)}
            </div>
        </section>

        <section class="info-section info-narrow info-cta" data-animate>
            <h2>あなたの地域の1冊をつくりませんか</h2>
            <p>枡フォトは、国や地域ごとに1冊の写真集をつくります。シティプロモーションや観光PRにご活用ください。</p>
            <a class="btn" href="../commission/">写真集プロジェクトを相談する</a>
            <p class="info-note"><a class="text-link" href="https://masu.fomus.jp/" target="_blank" rel="noopener">枡の専門店 MASU-STORE で枡を見る →</a></p>
        </section>'''
    url = f"{SITE}/masu/" if lang == "en" else f"{SITE}/ja/masu/"
    article = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
               "url": url, "inLanguage": lang, "author": {"@id": PERSON_ID}, "publisher": {"@id": ORG_ID},
               "about": {"@type": "Thing", "name": "Masu" if lang == "en" else "枡",
                         "sameAs": "https://en.wikipedia.org/wiki/Masu_(measurement)" if lang == "en" else "https://ja.wikipedia.org/wiki/枡"}}
    return shell(lang, "masu", title, desc, body, [article, faq_ld(faq), breadcrumb(lang, "masu", name)], ver)


# ------------------------------------------------------------------ スポンサー

# 掲載中のスポンサー（ロゴは partnership/1..7.webp。リンクは 2026-09 に確認したもの）
SPONSORS = [
    ("KUKU", "https://www.fomus.jp/kuku/", "partnership/1.webp"),
    ("CARDANO", None, "partnership/2.webp"),
    ("大橋量器", "https://www.masukoubou.jp/", "partnership/3.webp"),
    ("ADDress", "https://address.love/", "partnership/4.webp"),
    ("Rickshaw Inn", "https://www.rickshawinn.com/", "partnership/5.webp"),
    ("KOTO BUS", "https://www.kotobus.com/", "partnership/6.webp"),
    ("PON FES", None, "partnership/7.webp"),
]

SPONSOR = {
    "en": {
        "name": "Sponsor",
        "title": "Sponsor MASU PHOTO — Your Name in the Next Photo Book",
        "desc": "Support MASU PHOTO and have your company credited in the next photo book, on every page of this archive and in our posts. Three plans from 100,000 yen a year. Already supported by seven companies.",
        "label": "SPONSOR",
        "h1": "Your name in the next book.",
        "lead": "MASU PHOTO has been photographed in {countries} countries and published as {total} photo books, free to read. The next volume is made with the companies and people who support it — and their names stay in it.",
        "why_title": "Why sponsor a photo book",
        "why": [
            ("It stays", "A campaign ends. A book does not. Your name stays in the volume and in this archive, read in English and Japanese, for as long as the project exists."),
            ("It is culture, not advertising", "Your company appears as a supporter of Japanese culture — the masu, a craft of more than 1,300 years — rather than as an ad beside it."),
            ("It travels", "The books are photographed abroad and published in two languages, so your name is seen outside Japan as well as in it."),
        ],
        "credit_title": "Where your name appears",
        "credit_caption": "Example of the credit page. The design is finalised with you.",
        "proof_title": "What you are supporting",
        "proof": [
            ("{total} photo books", "Photographed in {countries} countries since 2022, over 400 pages, all free to read."),
            ("Shown at Japanese embassies", "FOMUS has exhibited the masu at receptions hosted by the Embassies of Japan in Ireland, Bahrain and Saudi Arabia."),
            ("Seven supporters so far", "Companies from crafts, travel, transport and culture already support the series."),
        ],
        "sponsors_title": "Current supporters",
        "plans_title": "Plans",
        "plans_note": "Prices are per year, including tax. The credit starts with the next volume published after your support begins.",
        "plans": [
            ("SUPPORTER", "¥100,000", "/ year", ["Logo and link in the supporters section, reachable from every page"]),
            ("PARTNER", "¥300,000", "/ year", ["Everything above",
                                                "Your name and logo credited in the photo books published that year",
                                                "Introduced in our social media posts"]),
            ("MAIN PARTNER", "¥1,000,000", "/ one volume", ["Everything above",
                                                            "Named partner of one volume, credited at its opening",
                                                            "Placed at the top of the supporters section"]),
        ],
        "flow_title": "How it works",
        "flow": [("Inquiry", "Tell us which plan interests you using the form below."),
                 ("Talk it through", "We agree on the plan, the timing and how your name appears."),
                 ("Support", "We send an invoice; you send your logo."),
                 ("Published", "Your name goes live in the archive and is credited in the next volume.")],
        "faq_title": "Questions",
        "faq": [
            ("Can an individual sponsor a book?", "Yes. Individuals are welcome, and a name can be listed instead of a company."),
            ("When does the credit start?", "In the archive as soon as the support begins, and in the photo books published after that."),
            ("How long does it last?", "One year for SUPPORTER and PARTNER. A MAIN PARTNER credit stays in that volume permanently."),
            ("Can a company outside Japan sponsor?", "Yes. The books and this site are published in English and Japanese."),
            ("Can we choose which country's volume we support?", "For MAIN PARTNER, yes — we decide the volume together."),
        ],
        "form_title": "Sponsorship inquiry",
        "form_lead": "We will reply by email. Your details are used only to respond to your inquiry.",
        "form": {
            "name": "Name", "org": "Company / organisation", "email": "Email",
            "type": "Plan", "types": ["SUPPORTER (¥100,000 / year)", "PARTNER (¥300,000 / year)",
                                      "MAIN PARTNER (¥1,000,000 / volume)", "Not decided yet"],
            "choose": "Please choose", "msg": "Message",
            "msg_ph": "Anything you would like to ask or tell us.",
            "submit": "Send inquiry", "optional": "optional", "subject": "MASU PHOTO sponsorship inquiry",
        },
    },
    "ja": {
        "name": "スポンサー",
        "title": "枡フォトのスポンサー｜次の1冊に、あなたの名前を残す",
        "desc": "枡フォト写真集のスポンサーを募集しています。写真集のクレジット、サイトのスポンサー欄、SNSでの紹介に社名・ロゴを掲載します。年10万円・30万円・100万円の3プラン。すでに7社が支援しています。",
        "label": "スポンサー",
        "h1": "次の1冊に、名前を残す。",
        "lead": "枡フォトは、{countries}カ国で撮影し、{total}冊の写真集として無料公開しているプロジェクトです。次の1冊は、支えてくださる企業や個人と一緒につくります。その名前は、写真集の中に残ります。",
        "why_title": "広告ではなく、残るものに名前を",
        "why": [
            ("消えない", "広告は期間が終われば消えます。写真集は残ります。日英で公開しているこのアーカイブの中に、プロジェクトが続くかぎり名前が残ります。"),
            ("文化の文脈で紹介される", "1300年以上の歴史をもつ日本の伝統工芸「枡」を支える企業として紹介されます。広告枠の中ではなく、作品の中に名前が入ります。"),
            ("海外にも届く", "撮影の中心は海外で、写真集もサイトも日英で公開しています。国内だけでなく、海外の人の目にも触れます。"),
        ],
        "credit_title": "名前が載る場所",
        "credit_caption": "クレジットページの掲載イメージです。実際のデザインはご相談のうえ決めます。",
        "proof_title": "支援していただくもの",
        "proof": [
            ("{total}冊の写真集", "2022年から{countries}カ国で撮影し、400ページを超える写真を、すべて無料で公開しています。"),
            ("日本国大使館での展示", "FOMUSは、在アイルランド・在バーレーン・在サウジアラビア日本国大使館の行事で、枡を展示してきました。"),
            ("すでに7社が支援", "工芸・宿・交通・文化など、さまざまな企業がこのシリーズを支えています。"),
        ],
        "sponsors_title": "現在のスポンサー",
        "plans_title": "スポンサープラン",
        "plans_note": "金額は年間・税込です。写真集への掲載は、ご支援後に出す巻からとなります。",
        "plans": [
            ("SUPPORTER", "10万円", "／年", ["全ページから辿れるスポンサー欄に、ロゴとリンクを掲載"]),
            ("PARTNER", "30万円", "／年", ["上記すべて",
                                          "その年に出す写真集に、社名・ロゴを掲載",
                                          "SNSでの紹介"]),
            ("MAIN PARTNER", "100万円", "／1冊", ["上記すべて",
                                                "1冊の冠スポンサーとして、巻頭に掲載",
                                                "スポンサー欄の最上段に掲載"]),
        ],
        "flow_title": "ご支援までの流れ",
        "flow": [("お問い合わせ", "下のフォームから、ご関心のあるプランをお知らせください。"),
                 ("ご相談", "プラン・時期・掲載の形を一緒に決めます。"),
                 ("ご支援", "請求書をお送りします。ロゴデータをお預かりします。"),
                 ("掲載", "サイトのスポンサー欄に掲載し、次の写真集にクレジットを入れます。")],
        "faq_title": "よくあるご質問",
        "faq": [
            ("個人でも支援できますか？", "できます。社名ではなく、お名前での掲載も承ります。"),
            ("いつから掲載されますか？", "サイトはご支援後すぐ、写真集はその後に出す巻から掲載します。"),
            ("掲載の期間は？", "SUPPORTERとPARTNERは1年間です。MAIN PARTNERの写真集への掲載は、その巻に残り続けます。"),
            ("海外の企業でも支援できますか？", "できます。写真集もサイトも、日本語と英語で公開しています。"),
            ("支援する国の巻を選べますか？", "MAIN PARTNERの場合は、どの巻にするかを一緒に決めます。"),
        ],
        "form_title": "スポンサーのお問い合わせ",
        "form_lead": "メールでご返信します。いただいた情報は、お問い合わせへの対応にのみ使います。",
        "form": {
            "name": "お名前", "org": "会社名・団体名", "email": "メールアドレス",
            "type": "ご関心のあるプラン", "types": ["SUPPORTER（10万円／年）", "PARTNER（30万円／年）",
                                                "MAIN PARTNER（100万円／1冊）", "まだ決めていない"],
            "choose": "選択してください", "msg": "ご質問・ご要望",
            "msg_ph": "ご質問やご要望があればお書きください。",
            "submit": "送信する", "optional": "任意", "subject": "枡フォト スポンサーのお問い合わせ",
        },
    },
}


def sponsor_page(lang, countries, total, ver):
    fill = lambda t: t.replace("{countries}", str(countries)).replace("{total}", str(total))
    c = json.loads(fill(json.dumps(SPONSOR[lang], ensure_ascii=False)))
    f = c["form"]
    req = '<span class="req">*</span>'
    opt = f'<span class="opt">{f["optional"]}</span>'
    root = "../" if lang == "en" else "../../"
    why = "\n".join(f'''                <article class="info-point">
                    <h3>{t}</h3>
                    <p>{d}</p>
                </article>''' for t, d in c["why"])
    proof = "\n".join(f'''                <article class="info-card">
                    <h3>{t}</h3>
                    <p>{d}</p>
                </article>''' for t, d in c["proof"])
    sponsors = "\n".join(
        (f'                <a class="sponsor-logo" href="{url}" target="_blank" rel="noopener">'
         if url else '                <div class="sponsor-logo">')
        + f'<img src="{root}{logo}" width="240" height="240" loading="lazy" alt="{esc(nm)}"><span>{esc(nm)}</span>'
        + ("</a>" if url else "</div>")
        for nm, url, logo in SPONSORS)
    plans = "\n".join(f'''                <article class="plan{' is-main' if i == 1 else ''}">
                    <p class="plan-name">{nm}</p>
                    <p class="plan-price">{price}<span>{unit}</span></p>
                    <ul>{"".join(f"<li>{b}</li>" for b in items)}</ul>
                    <a class="btn" href="#inquiry">{f["submit"] if lang == "en" else "このプランで相談する"}</a>
                </article>''' for i, (nm, price, unit, items) in enumerate(c["plans"]))
    flow = "\n".join(f'''                <li><h3>{t}</h3><p>{d}</p></li>''' for t, d in c["flow"])
    options = "\n".join(f'                            <option value="{t}">{t}</option>' for t in f["types"])
    ok_msg = ("Thank you. Your inquiry has been sent — we will reply by email."
              if lang == "en" else "送信しました。ありがとうございます。メールでご返信します。")
    ng_msg = (f"Sending failed. Please email us directly at {CONTACT_EMAIL}."
              if lang == "en" else f"送信に失敗しました。お手数ですが {CONTACT_EMAIL} まで直接ご連絡ください。")
    body = f'''{crumb_html(lang, c["name"])}

        <section class="info-hero" data-animate>
            <p class="label">{c["label"]}</p>
            <h1>{c["h1"]}</h1>
            <p class="info-lead">{c["lead"]}</p>
            <a class="btn" href="#plans">{"See the plans" if lang == "en" else "プランを見る"}　↓</a>
        </section>

        <section class="info-section" data-animate>
            <h2>{c["why_title"]}</h2>
            <div class="info-points">
{why}
            </div>
        </section>

        <section class="info-section info-split" data-animate>
            <div class="info-split-text">
                <h2>{c["credit_title"]}</h2>
                <p>{"Your name and logo appear in three places: the credit page of the photo books, the supporters section of this site, and our social media posts." if lang == "en" else "写真集のクレジットページ、サイトのスポンサー欄、SNSでの紹介。この3か所に、社名とロゴを掲載します。"}</p>
                <p class="info-note">{c["credit_caption"]}</p>
            </div>
            <figure class="credit-mock">
                <img src="{root}sponsor-credit-sm.webp" width="644" height="900" loading="lazy"
                     alt="{"MASU PHOTO credit page example" if lang == "en" else "枡フォト写真集のクレジットページ掲載イメージ"}">
            </figure>
        </section>

        <section class="info-section" data-animate>
            <h2>{c["proof_title"]}</h2>
            <div class="info-cards info-cards-3">
{proof}
            </div>
        </section>

        <section class="info-section" data-animate>
            <h2>{c["sponsors_title"]}</h2>
            <div class="sponsor-logos">
{sponsors}
            </div>
        </section>

        <section class="info-section" id="plans" data-animate>
            <h2>{c["plans_title"]}</h2>
            <div class="plans">
{plans}
            </div>
            <p class="info-note">{c["plans_note"]}</p>
        </section>

        <section class="info-section" data-animate>
            <h2>{c["flow_title"]}</h2>
            <ol class="info-flow">
{flow}
            </ol>
        </section>

        <section class="info-section info-narrow" data-animate>
            <h2>{c["faq_title"]}</h2>
            <div class="faq">
{faq_html(c["faq"])}
            </div>
        </section>

        <section class="info-section info-narrow" id="inquiry">
            <h2>{c["form_title"]}</h2>
            <p class="info-note">{c["form_lead"]}</p>
            <form class="inquiry-form" action="https://api.web3forms.com/submit" method="POST"
                  data-ok="{ok_msg}" data-ng="{ng_msg}">
                <input type="hidden" name="access_key" value="{FORM_KEY}">
                <input type="hidden" name="subject" value="{f["subject"]}">
                <input type="hidden" name="from_name" value="MASU PHOTO">
                <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
                <div class="fg-row">
                    <label class="fg"><span class="fg-label">{f["name"]} {req}</span><input type="text" name="name" autocomplete="name" required></label>
                    <label class="fg"><span class="fg-label">{f["org"]} {opt}</span><input type="text" name="organization" autocomplete="organization"></label>
                </div>
                <label class="fg"><span class="fg-label">{f["email"]} {req}</span><input type="email" name="email" autocomplete="email" required></label>
                <label class="fg"><span class="fg-label">{f["type"]} {req}</span>
                    <select name="plan" required>
                        <option value="">{f["choose"]}</option>
{options}
                    </select>
                </label>
                <label class="fg"><span class="fg-label">{f["msg"]} {opt}</span><textarea name="message" rows="5" placeholder="{f["msg_ph"]}"></textarea></label>
                <label class="fg-check"><input type="checkbox" name="consent" required><span>{COMMISSION[lang]["form"]["consent"]}</span></label>
                <button class="btn" type="submit">{f["submit"]}</button>
                <p class="form-status" role="status" hidden></p>
            </form>
        </section>'''
    url = f"{SITE}/sponsor/" if lang == "en" else f"{SITE}/ja/sponsor/"
    offers = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": c["h1"],
        "serviceType": "Sponsorship" if lang == "en" else "スポンサーシップ",
        "description": c["desc"],
        "url": url,
        "provider": ORGANIZATION,
        "areaServed": "Worldwide",
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": c["plans_title"],
            "itemListElement": [
                {"@type": "Offer", "name": nm, "price": price.replace("¥", "").replace(",", "").replace("万円", "0000"),
                 "priceCurrency": "JPY", "description": " / ".join(items)}
                for nm, price, unit, items in c["plans"]],
        },
    }
    return shell(lang, "sponsor", c["title"], c["desc"], body,
                 [offers, faq_ld(c["faq"]), breadcrumb(lang, "sponsor", c["name"])], ver)
