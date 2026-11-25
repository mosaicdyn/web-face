#!/usr/bin/env python3
"""Builds the static inner pages of therushb.com.

Usage (from the repo root):  python3 _build/build.py

Page content lives in _build/pages.py. Each page is written to <slug>/index.html.
The homepage (index.html) and the legal pages are edited by hand and are not touched.
Folders starting with "_" are ignored by GitHub Pages (Jekyll), so this script is not published.
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pages import PAGES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://therushb.com"
APP_STORE = "https://apps.apple.com/app/id6738445061"
GOOGLE_PLAY = "https://play.google.com/store/apps/details?id=guide.pro.rush.b"
SOCIAL = [
    ("TikTok", "https://www.tiktok.com/@rushb.guide",
     '<path transform="translate(11.25 11.25) scale(.5625)" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>'),
    ("YouTube", "https://www.youtube.com/@rushb_guide",
     '<path d="M25.98 13.96a2.1 2.1 0 00-1.47-1.48C23.21 12.13 18 12.13 18 12.13s-5.21 0-6.51.35a2.1 2.1 0 00-1.47 1.48c-.35 1.31-.35 4.04-.35 4.04s0 2.73.35 4.04c.19.72.76 1.29 1.47 1.48 1.3.35 6.51.35 6.51.35s5.21 0 6.51-.35a2.1 2.1 0 001.47-1.48c.35-1.31.35-4.04.35-4.04s0-2.73-.35-4.04zM16.3 20.48v-4.96l4.35 2.48-4.35 2.48z"/>'),
    ("Instagram", "https://www.instagram.com/rushb.guide/",
     '<path d="M21.75 10.5h-7.5a3.75 3.75 0 00-3.75 3.75v7.5a3.75 3.75 0 003.75 3.75h7.5a3.75 3.75 0 003.75-3.75v-7.5a3.75 3.75 0 00-3.75-3.75zM18 21.75a3.75 3.75 0 110-7.5 3.75 3.75 0 010 7.5zm4.01-7.04a.75.75 0 110-1.5.75.75 0 010 1.5z"/><circle cx="18" cy="18" r="2.25"/>'),
]
NAV = [("Home", ""), ("Nades", "lineups/"), ("Tactics", "tactics/"), ("Setups", "setups/"),
       ("AI Coach", "ai-coach/"), ("Binds", "binds/"), ("Contact", "#contact")]
FOOTER_NAV = [("Nades", "lineups/"), ("Smokes", "lineups/smokes/"), ("Flashes", "lineups/flashes/"),
              ("HE grenades", "lineups/he-grenades/"), ("Molotovs", "lineups/molotovs/"),
              ("Tactics", "tactics/"), ("Setups", "setups/"), ("AI Coach", "ai-coach/"),
              ("Binds", "binds/"), ("FAQ", "faq/"), ("About", "about/"), ("Download", "download/")]

e = html.escape


def store_buttons(r, extra_class=""):
    return f'''<div class="store-buttons{extra_class}">
        <a class="store-btn" href="{APP_STORE}" rel="noopener">
          <img src="{r}assets/img/icon-apple.svg" alt="" width="32" height="32" />
          <span class="store-btn__text"><span class="store-btn__small">Download on the</span><span class="store-btn__big">App Store</span></span>
        </a>
        <a class="store-btn" href="{GOOGLE_PLAY}" rel="noopener">
          <img src="{r}assets/img/icon-google-play.svg" alt="" width="32" height="32" />
          <span class="store-btn__text"><span class="store-btn__small">Get it on</span><span class="store-btn__big">Google Play</span></span>
        </a>
      </div>'''


def social_links():
    return "\n".join(
        f'        <a class="social__link" href="{url}" target="_blank" rel="noopener" aria-label="RushB on {name}"><svg viewBox="0 0 36 36" aria-hidden="true">{svg}</svg></a>'
        for name, url, svg in SOCIAL)


def header(r, active):
    links = []
    for label, href in NAV:
        if href.startswith("#"):
            url = f"{r}{href}" if r else href
        else:
            url = f"{r}{href}" if (r or href) else "./"
        cls = "site-nav__link is-active" if label == active else "site-nav__link"
        cur = ' aria-current="page"' if label == active else ""
        links.append(f'<a class="{cls}" href="{url}"{cur}>{label}</a>')
    return f'''  <header class="site-header" id="top">
    <a class="site-header__logo" href="{r or './'}" aria-label="RushB home">
      <img src="{r}assets/img/logo.webp" alt="RushB" width="139" height="60" />
    </a>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      {"\n      ".join(links)}
    </nav>
    <a class="btn btn--soft site-header__cta" href="{r}download/">Download App</a>
    <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span>
    </button>
  </header>'''


def footer(r):
    nav = "\n      ".join(f'<a href="{r}{href}">{label}</a>' for label, href in FOOTER_NAV)
    return f'''  <footer class="site-footer">
    <div class="footer-scene" id="footer-scene">
      <img class="footer-scene__img footer-scene__img--1" src="{r}assets/img/footer-1.webp" alt="" width="1440" height="1049" loading="lazy" aria-hidden="true" />
      <img class="footer-scene__img footer-scene__img--2" src="{r}assets/img/footer-2.webp" alt="" width="1440" height="1049" loading="lazy" aria-hidden="true" />
      <img class="footer-scene__img footer-scene__img--3" src="{r}assets/img/footer-3.webp" alt="RushB graffiti logo on a wall lit by a lamp" width="1440" height="1049" loading="lazy" />
      <nav class="social social--scene" aria-label="RushB on social media">
{social_links()}
      </nav>
    </div>

    <div class="footer-mobile">
      <p class="footer-mobile__text">Our platform combines data, visuals, and experience from the competitive scene to help you truly understand CS2. Train smarter, master every map, and bring pro-level thinking into your daily matches.</p>
      <nav class="social social--mobile" aria-label="RushB on social media">
{social_links()}
      </nav>
      {store_buttons(r, " store-buttons--footer")}
    </div>

    <nav class="footer-nav" aria-label="Site">
      {nav}
    </nav>
    <div class="footer-bar">
      <p>© 2026 Mosaic Dynamics LTD. All rights reserved.</p>
      <nav class="footer-bar__links" aria-label="Legal">
        <a href="{r}privacy.html">Privacy Policy</a>
        <a href="{r}terms.html">Terms of Use</a>
        <a href="{r}contact-us.html">Contact</a>
      </nav>
    </div>
  </footer>'''



def phones(screens, r):
    """screens: [(file, alt)] - first is the front phone, then back-left and back-right."""
    roles = ["front", "left", "right"]
    items = [(roles[i], f, alt) for i, (f, alt) in enumerate(screens[:3])]
    items = items[1:] + items[:1]          # back phones first, front last (paint order)
    imgs = "\n".join(
        f'          <div class="phone phones__item phones__item--{role}"><img src="{r}assets/img/{f}" alt="{e(alt)}" '
        f'width="600" height="1299" /></div>' for role, f, alt in items)
    mod = " phones--single" if len(screens) == 1 else ""
    return f'''<div class="phones{mod}">
{imgs}
        </div>'''

def hero(p, r):
    crumbs = [f'<a href="{r or "./"}">Home</a>']
    for label, href in p.get("crumbs", []):
        crumbs.append('<span aria-hidden="true">/</span>')
        crumbs.append(f'<a href="{r}{href}">{e(label)}</a>')
    crumbs.append('<span aria-hidden="true">/</span>')
    crumbs.append(f'<span aria-current="page">{e(p["crumb"])}</span>')
    stats = ""
    if p.get("stats"):
        stats = '<div class="stat-line">' + "".join(
            f'<div><strong>{v}</strong>{e(l)}</div>' for v, l in p["stats"]) + "</div>"
    device = ""
    if p.get("screens"):
        device = phones(p["screens"], r)
    return f'''    <section class="page-hero" aria-labelledby="page-title">
      <div class="hero__bg" aria-hidden="true"><img src="{r}assets/img/hero-wall.webp" alt="" width="1440" height="1682" /></div>
      <div class="container page-hero__grid">
        <div>
          <nav class="breadcrumbs" aria-label="Breadcrumb">{"".join(crumbs)}</nav>
          <h1 class="page-title" id="page-title">{p["h1"]}</h1>
          <p class="page-lead">{p["lead"]}</p>
          <div class="page-cta">
            {store_buttons(r)}
            <div class="qr-mini"><img src="{r}assets/img/qr-download.svg" alt="QR code to download RushB" width="72" height="72" /><span>Scan to get<br />RushB on your phone</span></div>
          </div>
          {stats}
        </div>
        {device}
      </div>
    </section>'''


def faq_section(p):
    if not p.get("faq"):
        return ""
    items = "\n".join(
        f'''        <details class="faq-item"{' open' if i == 0 else ''}>
          <summary>{e(q)}</summary>
          <div class="faq-item__body">{a}</div>
        </details>''' for i, (q, a) in enumerate(p["faq"]))
    return f'''    <section class="page-section" aria-labelledby="faq-title">
      <div class="container">
        <div class="section-head section-head--left">
          <h2 class="section-title" id="faq-title">{p.get("faq_title", "Questions")}</h2>
        </div>
        <div class="faq-list">
{items}
        </div>
      </div>
    </section>'''


def cta_band(r, p):
    title = p.get("cta_title", 'Get <span class="accent">RushB</span> on your phone')
    text = p.get("cta_text", "Lineups, tactics, setups, binds and an AI coach — free to download on iPhone and Android.")
    return f'''    <section class="cta-band">
      <div class="container">
        <div class="cta-band__box">
          <div>
            <h2 class="cta-band__title">{title}</h2>
            <p class="cta-band__text">{text}</p>
            {store_buttons(r)}
          </div>
          <img class="cta-band__qr" src="{r}assets/img/qr-download.svg" alt="QR code to download RushB" width="132" height="132" />
        </div>
      </div>
    </section>'''


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def schema(p):
    url = f"{SITE}/{p['slug']}"
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"}]
    for i, (label, href) in enumerate(p.get("crumbs", []), start=2):
        crumbs.append({"@type": "ListItem", "position": i, "name": label, "item": f"{SITE}/{href}"})
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": p["crumb"], "item": url})
    graph = [
        {"@type": "WebPage", "@id": url, "url": url, "name": p["title"], "description": p["description"],
         "isPartOf": {"@id": f"{SITE}/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": crumbs},
    ]
    if p.get("faq"):
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in p["faq"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def render(p):
    depth = p["slug"].strip("/").count("/") + 1
    r = "../" * depth
    canonical = f"{SITE}/{p['slug']}"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{e(p["title"])}</title>
  <meta name="description" content="{e(p["description"])}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="theme-color" content="#0e0f13" />
  <meta name="apple-itunes-app" content="app-id=6738445061" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="RushB" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{e(p["title"])}" />
  <meta property="og:description" content="{e(p["description"])}" />
  <meta property="og:image" content="{SITE}/assets/img/og-image.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" type="image/png" href="{r}assets/img/favicon.png" />
  <link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{r}assets/css/main.css" />
  <script>document.documentElement.classList.add("js")</script>
  <script type="application/ld+json">
{schema(p)}
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
{header(r, p.get("nav", ""))}
  <main id="main">
{hero(p, r)}
{p["body"](r)}
{faq_section(p)}
{cta_band(r, p)}
  </main>
{footer(r)}
  <script src="{r}assets/js/main.js" defer></script>
</body>
</html>
'''


def main():
    written = []
    for p in PAGES:
        out_dir = os.path.join(ROOT, p["slug"])
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(p))
        written.append(p["slug"])
    print("built:", ", ".join(written))


if __name__ == "__main__":
    main()
