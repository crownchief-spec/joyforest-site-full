#!/usr/bin/env python3
"""Build nine core service pages, index, nav, CSS, redirects, and sanitization copy."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
CSS = ROOT / "assets/css/style.css"
HEADER = ROOT / "components/header.html"
FOOTER = ROOT / "components/footer.html"
INDEX = ROOT / "index.html"
REDIRECTS = ROOT / "_redirects"
APPEND_SCRIPT = ROOT / "scripts/_build_nine_append.py"

STAY = (
    "拍攝完成後，免費贈送 2 小時空間停留使用，可休息、聚餐、聊天，"
    "讓孩子或毛孩在草地活動。若希望停留更久，可另外洽詢加購夜間體驗方案或延長空間使用時間。"
)

DEFAULT_FLOW = [
    ("純場地包場", "4 小時 NT$6,800", "約 200 坪室內外森林系空間，20 人內包場；可自帶餐點、外送、烤肉。"),
    ("加購｜活動拍照", "NT$4,800", "活動紀錄拍攝，照片全給並含基本調色。"),
    ("加購｜照片＋短片", "NT$8,800", "照片搭配微電影短片，依流程安排。"),
]

CSS_MARKER = "/* --- nine-services (build-nine-services.py) --- */"
CSS_BLOCK = """
/* --- nine-services (build-nine-services.py) --- */
.service-grid-9 {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
  margin-top: 14px;
}
@media (min-width: 720px) {
  .service-grid-9 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1024px) {
  .service-grid-9 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.service-grid-9 .service-card-entry {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: var(--r2);
  background: #fff;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.service-grid-9 .service-card-entry:hover {
  border-color: var(--green);
  box-shadow: 0 4px 16px rgba(46, 75, 63, 0.08);
}
.service-grid-9 .service-card-entry h3 {
  margin: 8px 0 6px;
  font-size: 1.05rem;
}
.service-grid-9 .service-card-entry p {
  margin: 0;
  flex: 1;
}

.space-usage-gallery .image-placeholder-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
  margin-top: 14px;
}
@media (min-width: 720px) {
  .space-usage-gallery .image-placeholder-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (min-width: 1024px) {
  .space-usage-gallery .image-placeholder-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.image-placeholder-card {
  margin: 0;
  border: 1px solid var(--line);
  border-radius: var(--r2);
  overflow: hidden;
  background: #f8f9f8;
}
.image-placeholder-media {
  aspect-ratio: 3 / 2;
  background: #e8ece9;
  overflow: hidden;
}
.image-placeholder-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.image-placeholder-card figcaption { padding: 12px 14px 14px; }
.image-placeholder-caption { margin: 0 0 6px; }
/* --- end nine-services --- */
""".strip()

CHANGED: list[str] = []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def log(path: Path | str) -> None:
    s = str(path)
    if s not in CHANGED:
        CHANGED.append(s)


def write_if_changed(path: Path, text: str) -> None:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old != text:
        path.write_text(text, encoding="utf-8")
        log(rel(path))


def gi(filename: str, alt: str, caption: str, fallback: str) -> dict:
    return {"filename": filename, "alt": alt, "caption": caption, "fallback": fallback}


def gallery_html(items: list[dict]) -> str:
    cards = []
    for it in items:
        cards.append(
            f"""          <figure class="image-placeholder-card">
            <div class="image-placeholder-media">
              <img src="../assets/images/{it['fallback']}" alt="{it['alt']}" loading="lazy" width="1200" height="800" />
            </div>
            <figcaption>
              <p class="image-placeholder-caption"><strong>{it['caption']}</strong></p>
              <p class="small image-placeholder-meta">建議檔名：<code>{it['filename']}</code></p>
            </figcaption>
          </figure>"""
        )
    return (
        '    <section class="section space-usage-gallery" id="space-config-gallery">\n'
        '      <div class="container">\n'
        '        <h2>空間使用示意</h2>\n'
        '        <p class="small">以下示意圖將依方案陸續補上實際照片，協助了解不同活動如何使用雲朵帳篷、熱氣球帳篷與戶外草地。</p>\n'
        '        <div class="image-placeholder-grid">\n'
        + "\n".join(cards)
        + "\n        </div>\n      </div>\n    </section>"
    )


def append_css() -> None:
    txt = CSS.read_text(encoding="utf-8")
    if CSS_MARKER in txt:
        return
    out = txt.rstrip() + "\n\n" + CSS_BLOCK + "\n"
    write_if_changed(CSS, out)


def section_from_id(main_html: str, section_id: str, *, to_end: bool = False) -> str:
    hit = main_html.find(f'id="{section_id}"')
    if hit < 0:
        return ""
    start = main_html.rfind("<section", 0, hit)
    if start < 0:
        return ""
    if to_end:
        return main_html[start:].strip()
    tail = main_html[start:]
    m = re.search(r'\n\s*<section class="section tight"|<section class="section tight"', tail)
    if m:
        return tail[: m.start()].strip()
    return tail.strip()


def extract_main(html: str) -> str:
    m = re.search(r"<main>(.*?)</main>", html, flags=re.S)
    return m.group(1).strip() if m else ""


def build_head(cfg: dict) -> str:
    slug = cfg["slug"]
    title = cfg["title"]
    desc = cfg["desc"]
    image = cfg["og_image"]
    url = f"https://joyforest.tw/pages/{slug}"
    svc = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": title,
        "provider": {"@type": "Organization", "name": "Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地"},
        "areaServed": "Taoyuan",
        "url": url,
        "description": desc,
        "image": image,
    }
    wp = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": url,
        "description": desc,
    }
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <base href="https://joyforest.tw/pages/" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}｜Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地</title>
  <link rel="stylesheet" href="./../assets/css/style.css" />

  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{title}｜Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:locale" content="zh_TW" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}｜Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{image}" />
  <meta name="robots" content="index, follow" />
  <meta name="googlebot" content="index, follow" />
  <meta name="bingbot" content="index, follow" />
  <meta name="theme-color" content="#2e4b3f" />
  <link rel="icon" href="../favicon.ico" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="../assets/images/favicon.svg" />
  <link rel="apple-touch-icon" href="../apple-touch-icon.png" />
  <link rel="manifest" href="../manifest.webmanifest" />
  <link rel="sitemap" type="application/xml" title="Sitemap" href="https://joyforest.tw/sitemap.xml" />
  <script type="application/ld+json">{json.dumps(svc, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(wp, ensure_ascii=False)}</script>
</head>
<body data-base="../">
  <div id="site-header"></div>
  <main>"""


def build_standard_main(cfg: dict) -> str:
    slug = cfg["slug"]
    hero_extra = ""
    if cfg.get("photo_nav"):
        hero_extra = (
            '        <div class="photo-series-nav" aria-label="攝影服務系列切換">\n'
            '          <a class="series-pill active" href="../pages/portrait-photography" aria-current="page">人像寫真服務</a>\n'
            '          <a class="series-pill" href="../pages/pet-photography">寵物攝影服務</a>\n'
            "        </div>\n"
        )
    elif slug == "pet-photography":
        hero_extra = (
            '        <div class="photo-series-nav" aria-label="攝影服務系列切換">\n'
            '          <a class="series-pill" href="../pages/portrait-photography">人像寫真服務</a>\n'
            '          <a class="series-pill active" href="../pages/pet-photography" aria-current="page">寵物攝影服務</a>\n'
            "        </div>\n"
        )

    paras = "".join(f'        <p class="hero-service-desc">{p}</p>\n' for p in cfg["hero_p"])
    hero = f"""    <section class="hero" aria-label="Hero">
      <div class="media" aria-hidden="true">
        <img src="../assets/images/{cfg['hero_img']}" alt="{cfg['hero_alt']}" />
        <div class="overlay"></div>
      </div>
      <div class="container inner">
        <p class="kicker" style="color:rgba(255,255,255,.85)">{cfg['kicker']}</p>
{hero_extra}        <h1 class="title">{cfg['h1']}</h1>
{paras}        <div class="actions" style="margin-top:16px">
          <a class="btn primary" href="https://line.me/ti/p/F2MWlK47xD" target="_blank" rel="noopener">加 Line 詢問</a>
          <a class="btn ghost" href="#space-config-gallery" style="color:#fff;border-color:rgba(255,255,255,.22);background:rgba(255,255,255,.08)">查看空間配置</a>
        </div>
      </div>
    </section>"""

    audience = (
        '    <section class="section" id="audience">\n'
        '      <div class="container">\n'
        '        <h2>適合對象</h2>\n'
        '        <div class="card"><ul class="small">\n'
        + "".join(f"            <li>{x}</li>\n" for x in cfg["audience"])
        + "          </ul></div>\n      </div>\n    </section>"
    )
    space = (
        f'    <section class="section" id="space-config">\n'
        f'      <div class="container">\n'
        f'        <h2>{cfg["space_title"]}</h2>\n'
        f'        <div class="card"><p class="small">{cfg["space_body"]}</p></div>\n'
        f"      </div>\n    </section>"
    )
    parts = [hero, audience, space, gallery_html(cfg["gallery"])]

    if not cfg.get("skip_flow"):
        flow_rows = cfg.get("flow_rows", DEFAULT_FLOW)
        flow_tr = "\n".join(
            f"            <tr><td><strong>{a}</strong></td><td>{b}</td><td class='small'>{c}</td></tr>"
            for a, b, c in flow_rows
        )
        parts.append(
            f"""    <section class="section" id="plans">
      <div class="container">
        <h2>{cfg.get('flow_title', '方案與流程')}</h2>
        <div class="card" style="overflow:auto">
          <table style="width:100%;border-collapse:collapse">
            <thead><tr>
              <th style="text-align:left;padding:10px;border-bottom:1px solid var(--line)">項目</th>
              <th style="text-align:left;padding:10px;border-bottom:1px solid var(--line)">費用</th>
              <th style="text-align:left;padding:10px;border-bottom:1px solid var(--line)">說明</th>
            </tr></thead>
            <tbody>
{flow_tr}
            </tbody>
          </table>
        </div>
        <p class="small" style="margin-top:12px">實際方案依日期、人數與需求確認，請加 Line 詢問最新檔期。</p>
      </div>
    </section>"""
        )

    if not cfg.get("skip_addons"):
        parts.append(
            """    <section class="section" id="add-ons">
      <div class="container">
        <h2>可加購項目</h2>
        <div class="grid-2">
          <div class="card"><h3>活動拍攝</h3><p class="small">活動紀錄拍攝，適合聚會、儀式與品牌活動。</p></div>
          <div class="card"><h3>照片＋短片</h3><p class="small">照片搭配微電影短片，依流程安排。</p></div>
          <div class="card"><h3>夜間體驗</h3><p class="small">活動後延長使用，安排燈光、投影與夜間氛圍。<a href="../pages/forest-night-experience">了解夜間體驗</a></p></div>
          <div class="card"><h3>延長空間使用</h3><p class="small">可另外洽詢延長空間方案與時段。</p></div>
          <div class="card"><h3>佈置討論</h3><p class="small">可依活動討論簡單佈置與動線，請預約時告知。</p></div>
        </div>
      </div>
    </section>"""
        )

    if not cfg.get("skip_faq"):
        faq_cards = "".join(
            f'          <div class="card"><h3>{q}</h3><p class="small">{a}</p></div>\n' for q, a in cfg["faq"]
        )
        parts.append(
            f"""    <section class="section" id="faq">
      <div class="container">
        <h2>常見問題</h2>
        <div class="grid-2">
{faq_cards}        </div>
      </div>
    </section>"""
        )

    if not cfg.get("skip_footer_blocks"):
        rel_links = "\n".join(
            f'          <a class="card-link" href="../pages/{s}">{l}</a>' for s, l in cfg["related"]
        )
        parts.extend(
            [
                """    <section class="section tight" id="booking-cta">
      <div class="container">
        <h2>預約與詢問</h2>
        <div class="card">
          <p><strong>全採預約制</strong>｜請加 Line 詢問／預約（Line ID：<strong>0911252302</strong>）。</p>
          <div class="actions" style="margin-top:10px">
            <a class="btn primary" href="https://line.me/ti/p/F2MWlK47xD" target="_blank" rel="noopener">加 Line 詢問</a>
            <a class="btn ghost" href="../pages/book">前往預約頁</a>
          </div>
        </div>
      </div>
    </section>""",
                f"""    <section class="section tight" id="related-services">
      <div class="container">
        <h2>相關服務</h2>
        <div class="card-links" style="margin-top:10px">
{rel_links}
        </div>
      </div>
    </section>""",
                f"""    <section class="section tight" id="seo-keywords">
      <div class="container">
        <h2>相關關鍵字</h2>
        <div class="card"><p class="small">{cfg['tags']}</p></div>
      </div>
    </section>""",
            ]
        )
    return "\n".join(parts)


def build_page(cfg: dict, main_html: str) -> str:
    return (
        build_head(cfg)
        + "\n"
        + main_html.strip()
        + """
  </main>
  <div id="site-footer"></div>
  <div id="cta-global"></div>
  <script src="./../assets/js/main.js" defer></script>
</body>
</html>
"""
    )


def nine_cfg() -> dict[str, dict]:
    return {
        "birthday-party": {
            "slug": "birthday-party",
            "title": "生日與小型派對包場",
            "desc": "桃園派對場地推薦：Joyforest 揪好森森林系私密包場，桃園中壢適合 20 人內生日與小型聚會。可加購活動拍照或照片＋短片。",
            "og_image": "https://joyforest.tw/assets/images/party/outdoor-party-table-01.jpg",
            "kicker": "活動包場｜預約制",
            "h1": "生日與小型派對包場",
            "hero_img": "party/outdoor-party-table-01.jpg",
            "hero_alt": "生日與小型派對包場 主視覺",
            "hero_p": [
                "適合 20 人內的生日派對、朋友小聚與家庭慶祝，室內外可自由切換。",
                "可自帶餐點、烤肉、唱歌、拍照，活動流程可完全客製化。",
            ],
            "audience": ["生日派對與朋友聚會", "希望隱私包場的家庭活動", "想加購拍攝留下紀錄的客人"],
            "space_title": "空間配置建議",
            "space_body": "室內可作為用餐與休息區，戶外草地可作為互動與拍照區，活動動線彈性。",
            "gallery": [
                gi("birthday-party-hero.jpg", "生日派對戶外桌面", "戶外派對桌面", "party/outdoor-party-table-01.jpg"),
                gi("birthday-party-food.jpg", "派對餐食與點心", "派對餐桌與點心", "party/party-food-table-01.jpg"),
                gi("birthday-party-kid.jpg", "兒童生日派對", "兒童生日活動", "party/birthday-party-kid-01.jpg"),
            ],
            "faq": [("可以自備餐點嗎？", "可以，自備餐點、外送與簡單烤肉皆可。"), ("是否可加購拍攝？", "可加購活動拍照或照片＋短片，請預約時提出。")],
            "related": [("family-party", "家庭聚餐"), ("pet-party", "寵物聚會"), ("forest-night-experience", "夜間體驗")],
            "tags": "#生日派對 #生日包場 #朋友聚會 #聚會場地 #桃園聚會場地 #中壢聚會 #楊梅聚會",
        },
        "baby-grab": {
            "slug": "baby-grab",
            "title": "抓周・週歲派對",
            "desc": "桃園楊梅森林系抓周場地，適合抓周、週歲派對、寶寶生日與家庭聚會。約 200 坪室內外空間。",
            "og_image": "https://joyforest.tw/assets/images/party/baby-grab-ceremony-01.jpg",
            "kicker": "活動包場｜預約制",
            "h1": "抓周・週歲派對",
            "hero_img": "party/baby-grab-ceremony-01.jpg",
            "hero_alt": "抓周・週歲派對 主視覺",
            "hero_p": [
                "把抓周從單一儀式延伸成一場完整家庭活動，包含拍照、聚餐與陪伴時光。",
                "室內可安排儀式流程，戶外草地可拍家庭互動與孩子自然活動。",
            ],
            "audience": ["抓周、週歲與寶寶生日", "三代同堂家庭聚會", "重視儀式與自然互動畫面的家庭"],
            "space_title": "抓周活動空間",
            "space_body": "可在室內安排抓周主儀式，戶外安排拍照、遊戲與親友合照，流程更彈性。",
            "gallery": [
                gi("baby-grab-hero.jpg", "抓周儀式場景", "抓周主儀式", "party/baby-grab-ceremony-01.jpg"),
                gi("baby-grab-family.jpg", "家庭互動場景", "家庭合照區", "party/joyforest-family-party-01.jpg"),
                gi("baby-grab-outdoor.jpg", "戶外草地活動", "戶外草地互動", "hero/forest-party-table-setup.jpg"),
            ],
            "faq": [("是否可加購拍攝？", "可加購活動拍照或照片＋短片，協助保留抓周流程。"), ("是否可攜帶長輩同行？", "可，空間可安排室內休息與戶外活動分區。")],
            "related": [("portrait-photography", "親子寫真"), ("family-party", "家庭聚餐"), ("birthday-party", "生日派對")],
            "tags": "#抓周 #抓周場地 #週歲派對 #寶寶生日 #桃園抓周 #中壢抓周 #楊梅抓周",
        },
        "pet-party": {
            "slug": "pet-party",
            "title": "寵物聚會｜毛孩生日派對、草地包場、寵物友善場地",
            "desc": "Joyforest 揪好森提供桃園楊梅森林系寵物友善場地，適合毛孩生日派對、狗狗同好聚會、親子與寵物家庭日。",
            "og_image": "https://joyforest.tw/assets/images/pet-party/og-pet-party-joyforest.jpg",
            "kicker": "活動包場｜寵物友善",
            "h1": "寵物聚會｜毛孩生日派對、草地包場、寵物友善場地",
            "hero_img": "pet-party/hero-pet-party-grass-picnic-joyforest.webp",
            "hero_alt": "寵物聚會 主視覺",
            "hero_p": [
                "森林草地與帳篷空間可包場使用，毛孩能活動、主人也能聚餐聊天。",
                "不綁定攝影，可純場地聚會，也可另外加購拍攝或夜間延長體驗。",
            ],
            "audience": ["毛孩生日派對", "寵物同好聚會", "親子＋寵物家庭日"],
            "space_title": "寵物友善場地配置",
            "space_body": "戶外草地可活動與拍照，室內帳篷可休息與用餐，適合毛孩與主人一同放鬆。",
            "gallery": [
                gi("pet-party-grass.jpg", "狗狗草地聚會", "草地聚會動線", "pet-party/pet-party-dogs-grass-picnic-joyforest-thumb.webp"),
                gi("pet-party-dome.jpg", "草地與帳篷", "帳篷休息區", "pet-party/pet-party-husky-bernese-grass-dome-joyforest-thumb.webp"),
                gi("pet-party-owner.jpg", "主人與毛孩互動", "人寵互動區", "pet-party/pet-photography-outdoor-golden-owner-grass-dome-joyforest-thumb.webp"),
            ],
            "skip_flow": True,
            "skip_addons": True,
            "skip_faq": True,
            "skip_footer_blocks": True,
            "related": [],
            "faq": [],
            "tags": "#寵物聚會 #毛孩生日 #寵物友善場地",
        },
        "family-party": {
            "slug": "family-party",
            "title": "家庭聚餐・家族聚會",
            "desc": "桃園楊梅約 200 坪森林系家庭聚會場地，適合家庭聚餐、親友聚會、長輩慶生。",
            "og_image": "https://joyforest.tw/assets/images/party/joyforest-family-party-01.jpg",
            "kicker": "活動包場｜預約制",
            "h1": "家庭聚餐・家族聚會",
            "hero_img": "party/joyforest-family-party-01.jpg",
            "hero_alt": "家庭聚餐 主視覺",
            "hero_p": ["比餐廳更自由的家庭聚會場景，室內休息與戶外活動可同時安排。", "適合長輩、小孩與毛孩同行的家庭日。"],
            "audience": ["家庭聚餐與家族聚會", "長輩慶生", "親友交流與輕活動"],
            "space_title": "家庭聚會空間",
            "space_body": "室內可吹冷氣休息用餐，戶外可散步與拍照，動線簡單好安排。",
            "gallery": [
                gi("family-party-main.jpg", "家庭聚會戶外", "家庭聚餐氛圍", "party/joyforest-family-party-01.jpg"),
                gi("family-party-table.jpg", "戶外桌面佈置", "聚餐桌面配置", "party/outdoor-party-table-01.jpg"),
                gi("family-party-grass.jpg", "草地互動場景", "草地活動區", "hero/joyforest-forest-venue-aerial.jpg"),
            ],
            "faq": [("可攜帶孩子與毛孩嗎？", "可以，空間可安排不同區域讓全家一起參與。"), ("是否可加購拍攝？", "可加購活動拍照或照片＋短片。")],
            "related": [("birthday-party", "生日派對"), ("baby-grab", "抓周派對"), ("portrait-photography", "親子寫真")],
            "tags": "#家庭聚餐 #家族聚會 #桃園家庭聚會 #楊梅家庭聚會 #包場聚餐",
        },
        "proposal": {
            "slug": "proposal",
            "title": "森林系求婚場地・驚喜求婚",
            "desc": "桃園楊梅森林系求婚包場，戶外草地儀式、雲朵帳篷準備區、熱氣球帳篷慶祝聚餐。適合約 20 人內驚喜求婚。",
            "og_image": "https://joyforest.tw/assets/images/night/forest-night-sparkler-couple.jpg",
            "kicker": "活動包場｜預約制",
            "h1": "森林系求婚場地・驚喜求婚・小型慶祝",
            "hero_img": "night/forest-night-sparkler-couple.jpg",
            "hero_alt": "森林系求婚場地 主視覺",
            "hero_p": [
                "Joyforest 適合想要有隱私、有場景、有儀式感的森林系求婚。戶外草地可安排紅毯、花束、燈光、投影與求婚儀式；雲朵帳篷可作為主角休息、換裝、物品放置與準備空間；熱氣球帳篷則適合求婚後的冷氣聚餐與朋友慶祝。",
                "適合約 20 人內的驚喜求婚、紀念日、親友見證與小型慶祝活動。可依需求加購求婚紀錄拍攝、照片＋短片、夜間燈光體驗或延長空間使用。",
            ],
            "audience": ["驚喜求婚與紀念日", "約 10–20 人親友見證", "希望草地儀式＋室內慶祝分區的客人"],
            "space_title": "求婚不是只有佈置，而是完整流程",
            "space_body": "一場求婚通常會需要等待、準備、儀式、拍照、慶祝與收尾。Joyforest 的空間可以分區使用：戶外草地負責求婚主場景與儀式動線，雲朵帳篷負責主角休息、換裝與物品放置，熱氣球帳篷負責朋友等待、求婚後聚餐、播放影片、吹冷氣與聊天。求婚成功後，不需要立刻離開，可以繼續留下慶祝與拍照。",
            "gallery": [
                gi("proposal-grass-red-carpet-setup.jpg", "戶外草地作為森林系求婚紅毯與佈置空間", "戶外草地｜求婚儀式、紅毯、花束、燈光與投影佈置。", "party/outdoor-party-table-01.jpg"),
                gi("proposal-cloud-tent-rest-room.jpg", "雲朵帳篷作為求婚主角休息與準備空間", "雲朵帳篷｜主角休息、換裝、放置物品與求婚準備區。", "photography/joyforest-indoor-dome-natural-light-studio-scene-01.jpg"),
                gi("proposal-balloon-tent-dining-celebration.jpg", "熱氣球帳篷作為求婚後冷氣用餐與朋友慶祝空間", "熱氣球帳篷｜求婚後聚餐、朋友慶祝、播放影片與冷氣休息。", "party/joyforest-family-party-01.jpg"),
                gi("proposal-night-lights-atmosphere.jpg", "夜間燈光作為森林求婚後延長體驗", "夜間體驗｜燈光、投影與求婚後浪漫氣氛延伸。", "night/forest-night-fire-lights.jpg"),
            ],
            "faq": [
                ("可以安排朋友躲起來驚喜嗎？", "可以依現場動線討論，室內帳篷可作為朋友等待與準備空間。"),
                ("可以播放影片嗎？", "可依設備與當日時段安排投影或螢幕播放，請預約時先告知。"),
                ("適合多少人？", "約 20 人內最適合，10 到 15 人會更舒適。"),
            ],
            "related": [("forest-wedding", "戶外婚禮"), ("forest-night-experience", "夜間體驗"), ("birthday-party", "生日派對")],
            "tags": "#求婚場地 #求婚包場 #桃園求婚場地 #戶外求婚 #森林求婚 #草地求婚 #求婚佈置 #求婚攝影 #驚喜求婚 #浪漫求婚 #求婚派對",
        },
        "forest-wedding": {
            "slug": "forest-wedding",
            "title": "森林系戶外婚禮・草地證婚",
            "desc": "桃園楊梅小型森林婚禮，戶外草地證婚、雲朵帳篷新人休息室、熱氣球帳篷室內冷氣宴客。約 20 位賓客內。",
            "og_image": "https://joyforest.tw/assets/images/wedding/outdoor-wedding-ceremony-01.jpg",
            "kicker": "活動包場｜預約制",
            "h1": "森林系戶外婚禮・草地證婚・小型婚禮",
            "hero_img": "wedding/outdoor-wedding-ceremony-01.jpg",
            "hero_alt": "森林系戶外婚禮 主視覺",
            "hero_p": [
                "Joyforest 適合約 20 位賓客內的小型森林系婚禮與戶外證婚。戶外草地可作為證婚儀式、紅毯、親友見證與拍照區；雲朵帳篷可作為新人休息室、化妝換裝與物品放置區；熱氣球帳篷可作為儀式後的室內冷氣宴客與用餐空間。",
                "適合想要簡單、溫暖、不制式的小型婚禮、證婚儀式、家人好友見證與精緻宴客。",
            ],
            "audience": ["約 20 人內小型證婚與婚禮", "重視戶外儀式感與室內舒適宴客", "家人好友見證的精緻婚禮"],
            "space_title": "戶外儀式＋室內冷氣宴客",
            "space_body": "很多戶外婚禮最大的問題，是賓客沒有舒適的休息與用餐空間。Joyforest 的特色是儀式可以在戶外草地完成，儀式後可以回到室內冷氣帳篷用餐、聊天與休息。雲朵帳篷可作為新人休息室與化妝換裝空間，熱氣球帳篷可作為約 20 人內的室內冷氣宴客空間。這樣能同時保留戶外儀式感與室內舒適度。",
            "gallery": [
                gi("wedding-grass-ceremony-red-carpet.jpg", "戶外草地作為森林系婚禮證婚與紅毯儀式空間", "戶外草地｜證婚儀式、紅毯、親友見證與拍照區。", "wedding/outdoor-wedding-ceremony-01.jpg"),
                gi("wedding-cloud-tent-bridal-room.jpg", "雲朵帳篷作為森林婚禮新人休息與化妝空間", "雲朵帳篷｜新人休息室、化妝換裝與物品放置。", "photography/joyforest-indoor-dome-natural-light-studio-scene-01.jpg"),
                gi("wedding-balloon-tent-indoor-banquet.jpg", "熱氣球帳篷作為小型婚禮室內冷氣宴客空間", "熱氣球帳篷｜儀式後室內冷氣用餐與親友宴客。", "party/joyforest-family-party-01.jpg"),
                gi("wedding-family-photo-grass.jpg", "戶外草地作為小型婚禮親友合照空間", "戶外草地｜婚禮後親友合照與自然光紀錄。", "wedding/outdoor-wedding-guests-01.jpg"),
            ],
            "faq": [
                ("適合大型婚禮嗎？", "不適合大型婚禮，建議約 20 位賓客內的小型證婚或精緻婚禮。"),
                ("可以在室內用餐嗎？", "可以，熱氣球帳篷可作為儀式後的室內冷氣用餐空間。"),
                ("有新人休息室嗎？", "雲朵帳篷可作為新人休息、化妝換裝與物品放置空間。"),
            ],
            "related": [("proposal", "求婚"), ("family-party", "家庭聚餐"), ("portrait-photography", "親子寫真")],
            "tags": "#戶外婚禮 #森林系婚禮 #戶外證婚 #證婚場地 #草地婚禮 #桃園婚禮場地 #小型婚禮 #小型婚宴 #婚禮包場 #森林婚禮",
        },
        "workshop-event": {
            "slug": "workshop-event",
            "title": "品牌活動・工作坊",
            "desc": "桃園楊梅約 200 坪森林系活動場地，適合品牌聚會、課程、工作坊與小型企業活動。",
            "og_image": "https://joyforest.tw/assets/images/hero/joyforest-forest-venue-aerial.jpg",
            "kicker": "活動包場｜預約制",
            "h1": "品牌活動・工作坊",
            "hero_img": "hero/joyforest-forest-venue-aerial.jpg",
            "hero_alt": "品牌活動與工作坊 主視覺",
            "hero_p": ["室內可講座、交流與用餐；戶外可體驗、互動與品牌拍照。", "適合想要有自然氛圍、又能保有流程彈性的活動主辦人。"],
            "audience": ["品牌小型活動", "生活風格工作坊", "企業與社群聚會"],
            "space_title": "活動空間配置",
            "space_body": "室內可簡報與課程，戶外可互動與拍照，活動流程可依主題彈性安排。",
            "gallery": [
                gi("workshop-aerial.jpg", "活動場地空拍", "場地整體動線", "hero/joyforest-forest-venue-aerial.jpg"),
                gi("workshop-table.jpg", "戶外活動桌面", "戶外課程配置", "party/outdoor-party-table-01.jpg"),
                gi("workshop-family.jpg", "草地互動活動", "戶外互動區", "party/joyforest-family-party-01.jpg"),
            ],
            "faq": [("可安排室內講座嗎？", "可以，室內可用於講座、交流與休息。"), ("可加購活動紀錄嗎？", "可加購拍照或照片＋短片。")],
            "related": [("birthday-party", "生日派對"), ("family-party", "家庭聚餐"), ("portrait-photography", "攝影服務")],
            "tags": "#品牌活動 #工作坊場地 #桃園活動場地 #森林活動場地 #企業小聚",
        },
        "portrait-photography": {
            "slug": "portrait-photography",
            "title": "寫真攝影｜親子家庭照・閨蜜寫真・個人形象照",
            "desc": "桃園攝影棚一頁式寫真服務：家庭照、親子寫真、閨蜜寫真、個人形象照。統一 NT$5,800／1.5 小時。",
            "og_image": "https://joyforest.tw/assets/images/photography/outdoor-family-photography-balloon-01.jpg",
            "kicker": "攝影服務｜預約制",
            "h1": "森林系親子寫真・家庭照・人像寫真",
            "hero_img": "photography/outdoor-family-photography-balloon-01.jpg",
            "hero_alt": "森林系親子寫真 主視覺",
            "hero_p": [
                "這裡不是一般小型攝影棚，而是約 200 坪的森林系攝影基地。拍攝空間包含雲朵帳篷正式棚拍區、熱氣球帳篷化妝休息與選片空間，以及戶外草地森林自然互動場景。",
                "適合家庭照、親子寫真、閨蜜照、情侶寫真、個人形象照與生活感人像拍攝。可以拍白背景棚拍，也可以拍自然光、草地、森林與生活感互動畫面。",
                STAY,
            ],
            "audience": ["家庭照與親子寫真", "閨蜜照、情侶寫真與個人形象照", "想同時拍棚拍與草地外景的客人"],
            "space_title": "三個空間，完成一場完整寫真拍攝",
            "space_body": "雲朵帳篷作為正式攝影棚，可設背景紙、棚拍燈光、自然光拍攝，適合家庭合照、人像棚拍與白背景簡約作品。熱氣球帳篷作為化妝、換裝、休息、家人等待與現場選片空間，家人不用全部擠在拍攝區等待。戶外草地與森林則適合拍孩子奔跑、親子互動、家庭散步、野餐感與生活感照片。",
            "gallery": [
                gi("portrait-cloud-tent-studio.jpg", "雲朵帳篷作為親子寫真正式棚拍攝影棚", "雲朵帳篷｜正式棚拍區，可設背景紙與棚拍燈光。", "photography/joyforest-indoor-dome-natural-light-studio-scene-01.jpg"),
                gi("portrait-balloon-tent-makeup-selection.jpg", "熱氣球帳篷作為家庭寫真化妝休息與選片空間", "熱氣球帳篷｜化妝、換裝、家人休息與現場選片空間。", "photography/outdoor-family-photography-balloon-01.jpg"),
                gi("portrait-grass-family-photo.jpg", "戶外草地作為親子寫真自然互動拍攝場景", "戶外草地｜親子奔跑、家庭互動與自然光生活感照片。", "photography/family-photography-child-grass-01.jpg"),
            ],
            "skip_flow": True,
            "skip_addons": True,
            "faq": [
                ("拍攝後的 2 小時可以做什麼？", "可以休息、聚餐、聊天、讓孩子在草地活動，也可以安排簡單慶生或家庭聚會。若希望停留更久，可另外洽詢夜間體驗或延長空間使用。"),
                ("可以只拍棚拍嗎？", "可以。也可以同時安排棚拍與草地外景，依當天家庭狀態與拍攝需求調整。"),
                ("有化妝或換衣服的空間嗎？", "有，熱氣球帳篷可作為化妝、換裝、休息與選片空間。"),
            ],
            "photo_nav": True,
            "related": [("pet-photography", "寵物攝影"), ("baby-grab", "抓周派對"), ("family-party", "家庭聚餐")],
            "faq": [],
            "tags": "#家庭照 #親子寫真 #家庭攝影 #人像寫真 #桃園家庭寫真 #自然風寫真 #生活感寫真 #白背景棚拍 #森林系寫真 #閨蜜寫真 #個人形象照",
        },
        "pet-photography": {
            "slug": "pet-photography",
            "title": "寵物攝影｜毛孩寫真・人寵合照・寵物家庭照",
            "desc": "桃園寵物攝影服務：毛孩寫真、人寵合照、寵物家庭照。統一 NT$5,800／1.5 小時。",
            "og_image": "https://joyforest.tw/assets/images/pet-photography/pet-photography-studio-surf-shiba-dogs.jpg",
            "kicker": "攝影服務｜預約制",
            "h1": "森林系寵物寫真・毛孩攝影・人寵合照",
            "hero_img": "pet-photography/pet-photography-studio-surf-shiba-dogs.jpg",
            "hero_alt": "森林系寵物寫真 主視覺",
            "hero_p": [
                "Joyforest 是適合毛孩真正放鬆活動的森林系寵物攝影空間。約 200 坪室內外場地包含正式棚拍空間、主人休息與選片空間，以及戶外草地森林互動場景。",
                "毛孩可以拍白背景棚拍，也可以在草地奔跑、探索環境、與主人互動，拍出比一般小型攝影棚更自然的表情與畫面。",
                STAY,
            ],
            "audience": ["毛孩寫真與寵物生日照", "人寵合照與寵物家庭照", "容易緊張、需要草地先放鬆的毛孩"],
            "space_title": "棚拍、草地、主人休息空間一次完成",
            "space_body": "雲朵帳篷可作為正式寵物攝影棚，適合毛孩生日照、白背景棚拍、人寵合照與寵物家庭照。熱氣球帳篷可作為主人休息、毛孩整理、等待與選片空間。戶外草地森林適合拍狗狗奔跑、毛孩互動、主人陪伴與自然生活感畫面。對容易緊張的毛孩來說，這樣的空間比一般小型攝影棚更容易放鬆。",
            "gallery": [
                gi("pet-cloud-tent-studio.jpg", "雲朵帳篷作為寵物寫真正式棚拍攝影棚", "雲朵帳篷｜寵物棚拍、人寵合照與毛孩生日照。", "pet-photography/pet-photography-studio-surf-shiba-dogs.jpg"),
                gi("pet-balloon-tent-owner-rest-selection.jpg", "熱氣球帳篷作為主人休息與寵物攝影選片空間", "熱氣球帳篷｜主人休息、毛孩整理與現場選片。", "pet-photography/outdoor-pet-photography-couple-with-dogs.jpg"),
                gi("pet-grass-running-photo.jpg", "戶外草地作為狗狗奔跑與寵物自然互動攝影場景", "戶外草地｜狗狗奔跑、毛孩互動與生活感攝影。", "pet-photography/outdoor-pet-photography-husky-grassland.jpg"),
            ],
            "skip_flow": True,
            "skip_addons": True,
            "faq": [
                ("毛孩緊張怎麼辦？", "可以先在戶外草地放鬆，再進行棚拍，或依毛孩狀況改以草地互動為主。"),
                ("可以拍主人跟毛孩一起嗎？", "可以，適合人寵合照、寵物家庭照、情侶與毛孩合照。"),
                ("拍完可以留下來聚會嗎？", "拍攝完成後免費贈送 2 小時空間停留使用，可聊天、聚餐或讓毛孩繼續活動。"),
            ],
            "related": [("pet-party", "寵物聚會"), ("portrait-photography", "親子寫真"), ("birthday-party", "生日派對")],
            "faq": [],
            "tags": "#寵物攝影 #寵物寫真 #毛孩攝影 #狗狗攝影 #貓咪攝影 #人寵合照 #寵物家庭照 #桃園寵物攝影 #草地寵物攝影 #寵物友善攝影棚 #毛孩生日",
        },
        "forest-night-experience": {
            "slug": "forest-night-experience",
            "title": "夜間森林體驗・活動後延長空間使用",
            "desc": "活動後的夜間延時使用時段，享受燈光、柴火、投影影音與森林夜晚氛圍。",
            "og_image": "https://joyforest.tw/assets/images/night/forest-night-fire-lights.jpg",
            "kicker": "夜間體驗｜預約制",
            "h1": "夜間森林體驗・活動後延長空間使用",
            "hero_img": "night/forest-night-fire-lights.jpg",
            "hero_alt": "夜間森林體驗 主視覺",
            "hero_p": [
                "夜間體驗是活動後的延長使用方案，適合想把聚會延伸到晚上、安排燈光、投影、聊天、用餐與夜間氣氛拍攝的客人。",
                "此方案不是住宿方案，而是依活動性質、人數與時段討論的夜間延長空間使用。",
            ],
            "audience": ["活動後想延長聚會的客人", "想安排夜間氣氛與投影的活動", "想保留夜間互動畫面的客人"],
            "space_title": "夜間體驗配置",
            "space_body": "可依活動安排夜間燈光與投影體驗，讓活動在更放鬆的節奏中收尾。",
            "gallery": [
                gi("night-lights-grass-area.jpg", "戶外草地夜間燈光體驗", "夜間燈光｜活動後延長使用與夜間氣氛。", "night/forest-night-fire-lights.jpg"),
                gi("night-projector-movie.jpg", "森林場地夜間投影戶外電影體驗", "投影體驗｜戶外電影、聊天與夜間聚會。", "night/forest-night-light-relax.jpg"),
                gi("night-balloon-tent-dining.jpg", "熱氣球帳篷夜間聚餐與室內休息空間", "室內夜間聚會｜用餐、休息與聊天。", "party/joyforest-family-party-01.jpg"),
            ],
            "faq": [("是住宿服務嗎？", "不是，為活動後的夜間延時使用時段。"), ("可以加購拍攝嗎？", "可以，可與活動拍攝一起安排。")],
            "related": [("birthday-party", "生日派對"), ("pet-party", "寵物聚會"), ("proposal", "求婚場地")],
            "tags": "#夜間體驗 #森林夜間活動 #活動延長方案 #燈光投影 #桃園夜間聚會",
        },
    }


def build_pages(cfg_map: dict[str, dict]) -> None:
    full_rebuild = {
        "birthday-party",
        "baby-grab",
        "family-party",
        "proposal",
        "forest-wedding",
        "workshop-event",
        "forest-night-experience",
    }
    for slug in full_rebuild:
        cfg = cfg_map[slug]
        write_if_changed(PAGES / f"{slug}.html", build_page(cfg, build_standard_main(cfg)))

    # Canonical page and redirect page for baby-grab / baby-party
    baby_party_redirect = """<!doctype html><html lang="zh-Hant"><head>
<meta charset="utf-8"/><meta http-equiv="refresh" content="0;url=https://joyforest.tw/pages/baby-grab"/>
<link rel="canonical" href="https://joyforest.tw/pages/baby-grab"/>
<title>重新導向</title><script>location.replace("https://joyforest.tw/pages/baby-grab");</script>
</head><body><p><a href="https://joyforest.tw/pages/baby-grab">前往抓周・週歲派對</a></p></body></html>
"""
    write_if_changed(PAGES / "baby-party.html", baby_party_redirect)

    # Portrait / Pet photography: prepend standard top, keep legacy from pricing to portfolio, then standard footer blocks.
    for slug in ("portrait-photography", "pet-photography"):
        cfg = cfg_map[slug].copy()
        html = (PAGES / f"{slug}.html").read_text(encoding="utf-8")
        main = extract_main(html)
        legacy = section_from_id(main, "pricing")
        cfg["skip_footer_blocks"] = False
        top_cfg = cfg.copy()
        top_cfg["skip_footer_blocks"] = True
        body = build_standard_main(top_cfg)
        if legacy:
            body += "\n" + legacy + "\n"
        body += "\n".join(
            [
                """    <section class="section tight" id="booking-cta">
      <div class="container">
        <h2>預約與詢問</h2>
        <div class="card">
          <p><strong>全採預約制</strong>｜請加 Line 詢問／預約（Line ID：<strong>0911252302</strong>）。</p>
          <div class="actions" style="margin-top:10px">
            <a class="btn primary" href="https://line.me/ti/p/F2MWlK47xD" target="_blank" rel="noopener">加 Line 詢問</a>
            <a class="btn ghost" href="../pages/book">前往預約頁</a>
          </div>
        </div>
      </div>
    </section>""",
                "    <section class=\"section tight\" id=\"related-services\">\n      <div class=\"container\">\n        <h2>相關服務</h2>\n        <div class=\"card-links\" style=\"margin-top:10px\">\n"
                + "\n".join(f'          <a class="card-link" href="../pages/{s}">{l}</a>' for s, l in cfg["related"])
                + "\n        </div>\n      </div>\n    </section>",
                f"""    <section class="section tight" id="seo-keywords">
      <div class="container">
        <h2>相關關鍵字</h2>
        <div class="card"><p class="small">{cfg['tags']}</p></div>
      </div>
    </section>""",
            ]
        )
        write_if_changed(PAGES / f"{slug}.html", build_page(cfg, body))

    # Pet party: prepend standard top and keep legacy from #party-pricing to end of main.
    pet_cfg = cfg_map["pet-party"]
    pet_html = (PAGES / "pet-party.html").read_text(encoding="utf-8")
    pet_main = extract_main(pet_html)
    pet_legacy = section_from_id(pet_main, "party-pricing", to_end=True)
    pet_top = build_standard_main(pet_cfg)
    pet_body = pet_top + ("\n" + pet_legacy if pet_legacy else "")
    write_if_changed(PAGES / "pet-party.html", build_page(pet_cfg, pet_body))


def update_index() -> None:
    txt = INDEX.read_text(encoding="utf-8")
    hero = """    <section class="hero" aria-label="Hero">
  <div class="media" aria-hidden="true">
    <video autoplay muted loop playsinline preload="metadata" poster="assets/images/hero/joyforest-forest-venue-aerial.jpg">
      <source src="assets/video/hero/hero-forest-aerial.mp4" type="video/mp4" />
    </video>
    <div class="overlay"></div>
  </div>
  <div class="container inner">
    <p class="kicker" style="color:rgba(255,255,255,.85)">Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地｜預約制</p>
    <h1 class="title">森林系活動包場空間 × 攝影服務基地</h1>
    <p class="subtitle hero-service-desc" style="margin-top:1em; max-width:42em; line-height:1.65">Joyforest 揪好森位於桃園楊梅，是一處約 200 坪的森林系活動包場空間，適合生日派對、抓周、寵物聚會、求婚、小型婚禮、家庭聚餐、品牌活動，也提供親子寫真、家庭照、人像寫真與寵物攝影服務。</p>
    <p class="subtitle hero-service-desc" style="max-width:42em; line-height:1.65">場地包含室內冷氣帳篷、戶外草地、森林場景、戶外廚房、攝影棚空間、休息與選片空間。活動可以依需求安排聚餐、拍照、儀式、烤肉、野餐、戶外電影、唱歌、遊戲與夜間燈光體驗。</p>
    <p class="subtitle hero-service-desc" style="max-width:42em; line-height:1.65">全場採預約制，適合約 20 人內，希望有隱私、不被打擾，又想留下照片與活動回憶的小型聚會。</p>
    <div class="actions" style="margin-top:16px">
      <a class="btn primary" href="pages/book">加入 Line 詢問／預約</a>
    </div>
  </div>
</section>"""
    txt = re.sub(r'<section class="hero" aria-label="Hero">.*?</section>', hero, txt, count=1, flags=re.S)

    nine_cards = [
        ("portrait-photography", "親子寫真 / 家庭照", "約 200 坪森林系攝影基地，包含正式棚拍、休息化妝選片空間與戶外草地場景，適合家庭照、親子寫真、閨蜜照與個人形象照。"),
        ("pet-photography", "寵物寫真 / 毛孩攝影", "毛孩可拍白背景棚拍，也能在草地奔跑與主人互動。適合寵物寫真、人寵合照、毛孩生日照與寵物家庭照。"),
        ("birthday-party", "生日派對 / 朋友聚會", "適合 20 人內生日派對、朋友聚餐與小型慶祝。室內可吹冷氣唱歌，戶外可烤肉、野餐、拍照與看戶外電影。"),
        ("baby-grab", "抓周 / 寶寶生日", "適合抓周、週歲派對、寶寶生日與家庭聚會。室內可安排儀式與用餐，戶外可拍家庭合照與親子互動。"),
        ("pet-party", "毛孩聚會 / 狗狗生日", "寵物友善草地與室內冷氣空間，適合毛孩生日、狗狗聚會、寵物家庭日與主人朋友聚餐。"),
        ("proposal", "求婚 / 驚喜活動", "戶外草地可安排紅毯、花束、燈光、投影與求婚儀式；室內帳篷可作為求婚後聚餐與朋友慶祝空間。"),
        ("forest-wedding", "戶外婚禮 / 森林證婚", "適合約 20 位賓客內的小型森林婚禮。戶外草地證婚，雲朵帳篷作新人休息室，熱氣球帳篷作室內冷氣宴客空間。"),
        ("family-party", "家庭聚餐 / 家族聚會", "適合家庭聚餐、長輩慶生、親友聚會與孩子毛孩同行。室內可用餐休息，戶外可野餐、拍照與草地活動。"),
        ("workshop-event", "品牌活動 / 工作坊", "適合品牌聚會、課程活動、親子工作坊、生活風格活動與小型企業聚會。室內可講座簡報，戶外可體驗活動與拍照。"),
    ]
    cards_html = "\n".join(
        f"""          <a class="service-card-entry" href="pages/{slug}">
            <h3>{title}</h3>
            <p class="small">{body}</p>
          </a>"""
        for slug, title, body in nine_cards
    )
    middle = f"""    <section class="section tight"><div class="container"><h2>三大主軸，一次到位</h2>
<div id="services" class="grid-3">
  <div class="card">
    <div class="badge">活動包場</div>
    <h3 style="margin-top:10px">生日、抓周、求婚、寵物聚會、小型婚禮</h3>
    <p class="small">適合 20 人內的小型森林系包場活動。室內可吹冷氣、用餐、唱歌、玩遊戲與休息；戶外可烤肉、野餐、拍照、辦儀式與看戶外電影。比一般餐廳更自由，也比一般包廂更有自然氛圍。</p>
  </div>
  <div class="card">
    <div class="badge">攝影服務</div>
    <h3 style="margin-top:10px">親子寫真、家庭照、人像寫真、寵物攝影</h3>
    <p class="small">結合正式棚拍空間、休息化妝選片空間與戶外草地森林場景。拍攝完成後，免費贈送 2 小時空間停留使用，可休息、聚餐、聊天，讓拍攝不只是拍照，而是一段完整的相聚時光。</p>
  </div>
  <div class="card">
    <div class="badge">夜間體驗</div>
    <h3 style="margin-top:10px">活動後延長使用、燈光、投影、夜間聚會氛圍</h3>
    <p class="small">適合活動後加購延長，安排夜間燈光、投影、聊天、聚餐與氣氛體驗。僅作為活動後延長空間使用與夜間氛圍方案，非住宿產品。</p>
  </div>
</div>
</div></section>
    <section class="section tight" id="nine-services">
      <div class="container">
        <h2>九大服務</h2>
        <p class="small">依活動目的快速挑選最適合的服務頁，全部方案皆可先加 Line 討論檔期與需求。</p>
        <div class="service-grid-9">
{cards_html}
        </div>
      </div>
    </section>"""
    txt = re.sub(
        r'<section class="section tight"><div class="container"><h2>三大主軸，一次到位</h2>.*?<section class="section tight"><div class="container"><h2>服務與費用摘要</h2>',
        middle + '\n    <section class="section tight"><div class="container"><h2>服務與費用摘要</h2>',
        txt,
        flags=re.S,
    )
    write_if_changed(INDEX, txt)


def update_header() -> None:
    header = """<header class="site-header">
  <div class="container">
    <nav class="nav" aria-label="Primary">
      <a class="brand" href="{{base}}">
        <img src="{{base}}assets/images/favicon.svg" alt="Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地" />
        <span>Joyforest 揪好森｜森林系活動包場空間＋攝影服務基地</span>
      </a>

      <button class="mobile-toggle" data-nav-toggle aria-expanded="false" aria-label="Open menu">☰</button>

      <div class="menu" data-nav-menu>
        <a href="{{base}}">首頁</a>

        <div class="dropdown menu-group">
          <button type="button" aria-expanded="false" class="menu-group-title">活動包場 ▾</button>
          <div class="dropdown-panel">
            <a href="{{base}}pages/birthday-party">生日派對</a>
            <a href="{{base}}pages/baby-grab">抓周派對</a>
            <a href="{{base}}pages/pet-party">毛孩聚會</a>
            <a href="{{base}}pages/proposal">求婚</a>
            <a href="{{base}}pages/forest-wedding">戶外婚禮</a>
            <a href="{{base}}pages/family-party">家庭聚餐</a>
            <a href="{{base}}pages/workshop-event">品牌活動</a>
          </div>
        </div>

        <div class="dropdown menu-group">
          <button type="button" aria-expanded="false" class="menu-group-title">攝影服務 ▾</button>
          <div class="dropdown-panel">
            <a href="{{base}}pages/portrait-photography">親子寫真 / 家庭照</a>
            <a href="{{base}}pages/pet-photography">寵物寫真</a>
            <a href="{{base}}pages/photography-studio">森林攝影場地出租</a>
          </div>
        </div>

        <a href="{{base}}#nine-services" class="menu-group menu-group-title">九大服務</a>
        <a href="{{base}}pages/forest-night-experience" class="menu-group menu-group-title">夜間體驗</a>
        <a href="{{base}}pages/faq" class="menu-group menu-group-title">常見問題</a>
        <a class="btn primary nav-cta" href="{{base}}pages/book">預約</a>
      </div>
    </nav>
  </div>
</header>
"""
    write_if_changed(HEADER, header)


def update_footer() -> None:
    txt = FOOTER.read_text(encoding="utf-8")
    txt = txt.replace("{{base}}pages/baby-party", "{{base}}pages/baby-grab")
    write_if_changed(FOOTER, txt)


def update_redirects() -> None:
    txt = REDIRECTS.read_text(encoding="utf-8")
    txt = re.sub(r"^/pages/baby-grab\.html\s+/pages/\S+\s+301$", "/pages/baby-grab.html             /pages/baby-grab            301", txt, flags=re.M)
    txt = re.sub(r"^/pages/baby-grab\s+/pages/\S+\s+301$", "/pages/baby-party                /pages/baby-grab            301", txt, flags=re.M)
    txt = re.sub(r"^/pages/baby-party\.html\s+/pages/\S+\s+301$", "/pages/baby-party.html            /pages/baby-grab            301", txt, flags=re.M)
    txt = re.sub(r"^/pages/baby-grab/\s+/pages/\S+\s+301$", "/pages/baby-grab/                /pages/baby-grab            301", txt, flags=re.M)
    txt = re.sub(r"^/pages/baby-party/\s+/pages/\S+\s+301$", "/pages/baby-party/               /pages/baby-grab            301", txt, flags=re.M)
    if "/pages/baby-party                /pages/baby-grab            301" not in txt:
        txt += "\n/pages/baby-party                /pages/baby-grab            301\n"
    write_if_changed(REDIRECTS, txt)


def sanitize_pages_wording() -> None:
    replacements = [
        ("空房狀況", "檔期狀況"),
        ("空房", "檔期"),
        ("入住當天或隔天安排拍攝", "活動當天或隔天安排拍攝"),
        ("入住", "到場"),
        ("住宿產品", "旅宿型產品"),
        ("住宿", "旅宿"),
    ]

    for path in sorted(PAGES.glob("*.html")):
        txt = path.read_text(encoding="utf-8")
        old = txt
        for a, b in replacements:
            txt = txt.replace(a, b)

        lines = []
        for line in txt.splitlines():
            if "過夜" in line and "<h3>" in line and "Q" in line:
                lines.append(line)
                continue
            lines.append(line.replace("過夜", "夜間延時使用"))
        txt = "\n".join(lines) + ("\n" if old.endswith("\n") else "")

        if txt != old:
            write_if_changed(path, txt)


def cleanup_append_script() -> None:
    if APPEND_SCRIPT.exists():
        APPEND_SCRIPT.unlink()
        log(rel(APPEND_SCRIPT))


def main() -> None:
    append_css()
    cfg_map = nine_cfg()
    build_pages(cfg_map)
    update_index()
    update_header()
    update_footer()
    update_redirects()
    sanitize_pages_wording()
    cleanup_append_script()
    print("CHANGED files:")
    for p in sorted(CHANGED):
        print(f"- {p}")


if __name__ == "__main__":
    main()
