"""Content of therushb.com inner pages. Edit text here, then run: python3 _build/build.py

Each page:
  slug         URL path ("tactics/")
  nav          which header link is highlighted
  title        <title>, under 60 characters
  description  meta description, 140–160 characters
  crumb/crumbs breadcrumb label and parent pages
  h1, lead     hero heading (may contain <span class="accent">) and intro
  stats        optional [(value_html, label)]
  screens      optional [(image in assets/img, alt text)] - front phone first, up to 3
  aside(r)     optional HTML for the right side of the hero instead of the phones (tools)
  body(r)      HTML sections; r is the relative path to the site root
  faq          [(question, answer_html)] -> also output as FAQPage schema
  updated      optional ISO date, shown under the lead
  article      optional True -> Article schema (guides)
"""

import html as _html
import json as _json
import os as _os
from collections import Counter as _Counter
from urllib.parse import quote as _quote

ACTIVE_DUTY = ["Ancient", "Anubis", "Cache", "Dust II", "Inferno", "Mirage", "Nuke"]

# Free lineups of the Active Duty maps, exported from the app (see _build/data/README.md).
LINEUPS = _json.load(open(_os.path.join(_os.path.dirname(__file__), "data", "lineups_free.json"), encoding="utf-8"))
MAP_ORDER = ["mirage", "inferno", "dust2", "ancient", "anubis", "nuke", "cache"]


def section(inner, extra=""):
    return f'''    <section class="page-section{extra}">
      <div class="container">
{inner}
      </div>
    </section>'''


def head(title, lead=None, left=True):
    cls = "section-head section-head--left" if left else "section-head"
    lead_html = f'\n          <p class="section-lead">{lead}</p>' if lead else ""
    return f'''        <div class="{cls}">
          <h2 class="section-title">{title}</h2>{lead_html}
        </div>'''


def tiles(items, cols=3, numbered=False):
    grid = {2: " tile-grid--2", 3: "", 4: " tile-grid--4"}[cols]
    out = []
    for i, it in enumerate(items, start=1):
        tag = "a" if it.get("href") else "article"
        href = f' href="{it["href"]}"' if it.get("href") else ""
        num = f'<span class="tile__num">{i}</span>' if numbered else ""
        kicker = f'<span class="tile__kicker">{it["kicker"]}</span>' if it.get("kicker") else ""
        more = f'<span class="tile__more">{it["more"]} →</span>' if it.get("more") else ""
        out.append(f'''          <{tag} class="tile reveal"{href}>{num}{kicker}
            <h3 class="tile__title">{it["title"]}</h3>
            <p class="tile__text">{it["text"]}</p>{more}
          </{tag}>''')
    return f'        <div class="tile-grid{grid}">\n' + "\n".join(out) + "\n        </div>"



def mode_cards(r, items):
    """Cards with an app screenshot next to the text (used for Single vs Combo nades)."""
    out = []
    for it in items:
        src, alt = it["img"]
        out.append(f'''          <article class="mode-card reveal">
            <div class="phone mode-card__phone"><img src="{r}assets/img/{src}" alt="{alt}" width="600" height="1299" loading="lazy" /></div>
            <div class="mode-card__body">
              <span class="tile__kicker">{it["kicker"]}</span>
              <h3 class="tile__title">{it["title"]}</h3>
              <p class="tile__text">{it["text"]}</p>
            </div>
          </article>''')
    return '        <div class="mode-grid">\n' + "\n".join(out) + "\n        </div>"

def chips(items):
    return '        <ul class="chips">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def map_links(r):
    links = []
    for slug in sorted(MAP_ORDER, key=lambda s: LINEUPS["maps"][s]["label"]):
        m = LINEUPS["maps"][slug]
        links.append(f'<li><a href="{r}lineups/{slug}/">{m["label"]} <span>{m["free"]}</span></a></li>')
    return '        <ul class="chips chips--links">' + "".join(links) + "</ul>"


def code(text):
    return f'''<div class="code-block"><button class="code-block__copy" type="button">Copy</button><pre>{text}</pre></div>'''


def prose(inner):
    return f'        <div class="prose">\n{inner}\n        </div>'


def grenade_types(r, exclude=None):
    items = [
        {"slug": "smokes", "kicker": "Smoke", "title": "Smoke lineups",
         "text": "Block vision on chokepoints, cut rotations and take sites with one-ways, execute smokes and retake smokes."},
        {"slug": "flashes", "kicker": "Flashbang", "title": "Flash lineups",
         "text": "Pop flashes for entries, flashes for your teammates and safe flashes you can throw without blinding yourself."},
        {"slug": "he-grenades", "kicker": "HE grenade", "title": "HE grenade lineups",
         "text": "Damage stacked defenders, finish low players and open a smoke for a moment with a well-timed HE."},
        {"slug": "molotovs", "kicker": "Molotov / Incendiary", "title": "Molotov lineups",
         "text": "Clear close corners, stop pushes and delay a defuse with molotovs and incendiaries thrown from safe spots."},
    ]
    items = [dict(it, href=f"{r}lineups/{it['slug']}/", more="Open") for it in items if it["slug"] != exclude]
    return tiles(items, cols=4 if len(items) == 4 else 3)


PRACTICE_CONFIG = """sv_cheats 1
sv_infinite_ammo 1
ammo_grenade_limit_total 5
sv_grenade_trajectory_prac_pipreview 1
sv_grenade_trajectory_prac_trailtime 8
mp_buy_anywhere 1
mp_buytime 9999
mp_freezetime 0
mp_roundtime_defuse 60
mp_warmup_end
bind n sv_rethrow_last_grenade"""

PRACTICE_BINDS = '''bind n "sv_rethrow_last_grenade"
bind m "ent_fire smokegrenade_projectile kill; stopsound"
bind k "noclip"'''

GRENADE_BINDS = '''bind z "slot7"
bind x "slot8"
bind c "slot6"
bind v "slot10"'''

JUMP_THROW_NOTE = (
    '<p class="note"><strong>About jump-throw binds.</strong> Since the August 2024 update, binds that combine '
    'more than one movement or attack action (for example a jump-throw or null bind) no longer work on Valve '
    'servers. Valve made the jump-throw reliable without a bind: jump and release the grenade at the same time. '
    'A single-action bind such as <code>bind mwheelup +jump</code> is still fine.</p>'
)


# ---------------------------------------------------------------- lineups hub
def lineups_body(r):
    return "\n".join([
        section(head("Pick a grenade type",
                     "Every lineup in RushB is sorted by map, grenade type and side, so you find the throw you need in a few taps.") +
                "\n" + grenade_types(r)),
        section(head("Single and combo nades",
                     "Every map in RushB has two modes. Switch between them at the top of the map screen.") + "\n" + mode_cards(r, [
            {"kicker": "Single", "title": "One grenade, one lineup",
             "img": ("screen-nades-single.webp", "RushB app: Single mode on the Mirage radar with lineups from one spot"),
             "text": "Tap a grenade on the radar to see its throw: where to stand, where to aim and how to throw it — for example running with a left click. A screenshot breakdown starts from the start position, and a video shows the full throw."},
            {"kicker": "Combo", "title": "A set of grenades that work together",
             "img": ("screen-nades-combo.webp", "RushB app: Combo mode on the Mirage radar with grenade and player icons"),
             "text": "A combo groups the nades for one play — for example two smokes, a flash and an HE for a B site take. Tap any grenade or player on the radar to open the combo and see every nade in it."},
        ]), " page-section--tight"),
        section(head("How a lineup works in RushB") + "\n" + tiles([
            {"title": "Choose the map", "text": "Open a map and pick Single for one throw or Combo for a set of nades."},
            {"title": "Filter the nades", "text": "Show the grenade type you need, or filter by retakes, insta smokes and one-way smokes."},
            {"title": "Tap the landing spot", "text": "The radar shows where each grenade lands. Tap a spot to see every way to get there."},
            {"title": "Copy the throw", "text": "Follow the position, aim point and throw type, check the screenshot breakdown and watch the video."},
        ], cols=4, numbered=True), " page-section--tight"),
        section(prose(f'''          <h2 id="maps">Lineups for the competitive map pool</h2>
          <p>Valve’s Active Duty pool is the set of maps used in Premier and at Majors. Since July 2026 it is these seven maps — open one to see its free lineups with video:</p>
''') + "\n" + map_links(r) + "\n" + prose(f'''          <p style="margin-top:20px">RushB has a database of 2000+ lineups across the competitive maps — from the standard smokes every team uses to pro-level utility. Single nades, combos and several throws from the same spot are all filtered by map and situation.</p>
          <h2>How to practise nades faster</h2>
          <p>Learn a lineup in a private match before you use it in Premier or on FACEIT. Start an offline game, open the console and paste this practice config:</p>
          {code(PRACTICE_CONFIG)}
          <p>Now you have unlimited grenades, a camera that shows where each throw will land, and <code>N</code> repeats your last grenade without walking back to the spot. Every command, the binds and a practice routine are in our guide <a href="{r}guides/cs2-practice-commands/">how to practice nades in CS2</a>.</p>
          {JUMP_THROW_NOTE}''')),
    ])


LINEUPS_FAQ = [
    ("What is a lineup in CS2?",
     "<p>A lineup is a fixed position and aim point that lands a grenade on the same spot every time. Learning a few lineups per map lets you smoke, flash or molotov a position without guessing.</p>"),
    ("How many lineups are in RushB?",
     "<p>More than 2000 smoke, flash, HE and molotov lineups for the competitive maps — single nades, combos and multi-throw variations from one spot.</p>"),
    ("What is the difference between single and combo nades?",
     "<p>A single nade is one lineup: one grenade with its position, aim point, throw type, screenshots and video. A combo is a set of grenades that work together for one play — for example two smokes, a flash and an HE for a site take — so you see every nade of the play in one place.</p>"),
    ("Do I need a jump-throw bind?",
     "<p>No. Since August 2024 Valve blocks binds that combine several movement or attack actions on its servers, and the jump-throw is reliable without a bind. Jump and release the grenade at the same moment.</p>"),
    ("Is RushB free?",
     "<p>RushB is free to download on the <a href=\"https://apps.apple.com/app/id6738445061\">App Store</a> and <a href=\"https://play.google.com/store/apps/details?id=guide.pro.rush.b\">Google Play</a>. Some lineups and features are part of the RushB Pro subscription.</p>"),
]


# ---------------------------------------------------------------- grenade pages
# ---------------------------------------------------------------- map pages
TYPE_LABEL = {"smoke": ("Smoke", "Smokes"), "flash": ("Flash", "Flashes"),
              "molotov": ("Molotov", "Molotovs"), "he": ("HE grenade", "HE grenades")}
TYPE_ORDER = ["smoke", "flash", "molotov", "he"]


def _plural(t):
    return "HE grenades" if t == "he" else TYPE_LABEL[t][1].lower()


def _nade_word(it):
    if it["type"] == "molotov" and it["side"] == "CT":
        return "incendiary"
    return {"smoke": "smoke", "flash": "flash", "molotov": "molotov", "he": "HE"}[it["type"]]


def _cards(items, cdn):
    """Groups throws with the same start and landing spot into one card."""
    groups = {}
    for it in items:
        groups.setdefault((it["from"], it["to"]), []).append(it)
    out = []
    for (frm, to), throws in groups.items():
        word = _nade_word(throws[0])
        title = f"{to} {word} from {frm}" if frm != to else f"{to} {word}"
        tags = sorted({t["tag"] for t in throws if t["tag"]})
        tag_html = "".join(f'<span class="lineup__tag">{_html.escape(t)}</span>' for t in tags)
        rows = []
        for n, t in enumerate(throws, start=1):
            label = "Watch the throw" if len(throws) == 1 else f"Watch throw {n}"
            url = cdn + _quote(t["video"])
            rows.append(f'<li><span>{_html.escape(t["throw"])}</span>'
                        f'<a class="lineup__play" href="{url}" data-video="{url}" data-title="{_html.escape(title)}">'
                        f'<span aria-hidden="true">▶</span> {label}</a></li>')
        out.append(f'''          <article class="lineup">
            <div class="lineup__head"><span class="lineup__kicker">{TYPE_LABEL[throws[0]["type"]][0]}</span>{tag_html}</div>
            <h4 class="lineup__title">{_html.escape(title)}</h4>
            <ul class="lineup__throws">{"".join(rows)}</ul>
          </article>''')
    return '        <div class="lineup-grid">\n' + "\n".join(out) + "\n        </div>"


VIDEO_DIALOG = '''    <dialog class="video-dialog" id="lineup-video" aria-label="Lineup video">
      <div class="video-dialog__bar">
        <p class="video-dialog__title"></p>
        <button class="video-dialog__close" type="button" data-close aria-label="Close video">×</button>
      </div>
      <video controls playsinline preload="none"></video>
    </dialog>'''


def map_body(slug):
    m = LINEUPS["maps"][slug]
    cdn = LINEUPS["cdn"]
    label = m["label"]

    def body(r):
        items = m["lineups"]
        top = [n for n, _ in _Counter(i["to"] for i in items).most_common(3)]
        sides = {s: [i for i in items if i["side"] == s] for s in ("T", "CT")}
        nav = []
        blocks = []
        for side in ("T", "CT"):
            parts = []
            for t in TYPE_ORDER:
                group = [i for i in sides[side] if i["type"] == t]
                if not group:
                    continue
                anchor = f"{side.lower()}-{t}"
                plural = _plural(t)
                nav.append(f'<a href="#{anchor}">{side} {plural} <span>{len(group)}</span></a>')
                parts.append(f'        <h3 class="lineup-group__title" id="{anchor}">{side} side {plural} <span>{len(group)}</span></h3>\n' + _cards(group, cdn))
            if parts:
                side_name = "Terrorist" if side == "T" else "Counter-Terrorist"
                blocks.append(section(head(f"{label} {side} side lineups",
                                           f"{len(sides[side])} free {side_name} lineups. Press Watch to see the full throw.") +
                                      "\n" + "\n".join(parts), " page-section--tight"))
        intro = prose(f'''          <p>These are the free {label} lineups from RushB: {m["free"]} throws with video — {len(sides["T"])} for the T side and {len(sides["CT"])} for CT. Most of them land on {", ".join(top[:-1])} and {top[-1]}. Every card shows where to stand, where the nade lands and how to throw it.</p>''')
        jump = '        <nav class="lineup-nav" aria-label="Jump to a group">' + "".join(nav) + "</nav>"
        more = m["total"] - m["free"]
        return "\n".join([
            section(intro + "\n" + jump, " page-section--tight"),
            *blocks,
            section(head(f"{more} more {label} lineups in RushB",
                         f"The app has {m['total']} {label} lineups, plus combos — sets of nades for one play — and filters for one-ways, insta smokes and retakes.") +
                    "\n" + tiles([
                        {"title": "Practise faster", "text": "Unlimited nades, the grenade camera and a rethrow key: set up in two minutes.",
                         "href": f"{r}guides/cs2-practice-commands/", "more": "Practice guide"},
                        {"title": "Other maps", "text": "Free lineups with video for the rest of the competitive map pool.",
                         "href": f"{r}lineups/#maps", "more": "All maps"},
                        {"title": "Get RushB", "text": f"All {m['total']} {label} lineups, combos and filters on iPhone and Android.",
                         "href": f"{r}download/", "more": "Download"},
                    ]), " page-section--tight"),
            VIDEO_DIALOG,
        ])
    return body


def map_faq(slug):
    m = LINEUPS["maps"][slug]
    label = m["label"]
    pool = ("<p>Yes. Cache came back to the Active Duty pool on July 8, 2026, in place of Overpass. It is one of the seven maps of Premier and the pro scene.</p>"
            if slug == "cache" else
            f"<p>Yes. {label} is one of the seven maps of the Active Duty pool, which is used in Premier and at Majors.</p>")
    return [
        (f"Are these {label} lineups free?",
         f"<p>Yes. The {m['free']} lineups on this page are free to watch. RushB has {m['total']} {label} lineups in total — the rest, and the combos, are in the app with RushB Pro.</p>"),
        (f"How do I practise {label} smokes?",
         f"<p>Start an offline match on {label} with unlimited nades and the grenade camera, then repeat each throw with <code>sv_rethrow_last_grenade</code>. The full setup is in our guide <a href=\"../../guides/cs2-practice-commands/\">how to practice nades in CS2</a>.</p>"),
        (f"Is {label} in the CS2 map pool?", pool),
    ]


def map_pages():
    pages = []
    for slug in MAP_ORDER:
        m = LINEUPS["maps"][slug]
        label = m["label"]
        types = [_plural(t) for t in TYPE_ORDER if any(i["type"] == t for i in m["lineups"])]
        types_text = ", ".join(types[:-1]) + " and " + types[-1]
        pages.append({
            "slug": f"lineups/{slug}/", "nav": "Nades",
            "title": f"{label} Smokes & Nades for CS2 – Free Lineups | RushB",
            "description": f"{m['free']} free {label} lineups with video: {types_text} for T and CT, with where to stand, where the nade lands and how to throw it.",
            "crumb": label, "crumbs": [("Nades", "lineups/")],
            "h1": f'{label} <span class="accent">smokes &amp; nades</span>',
            "lead": f"Free {label} lineups for T and CT: {types_text}. Pick a spot, watch the throw and land it in your next match.",
            "stats": [(str(m["free"]), "free lineups with video"), (f'{m["total"]}', "in the app"), ("T&nbsp;/&nbsp;CT", "both sides")],
            "screens": [("screen-nades-single.webp", f"RushB app: single grenade lineups on the radar"), ("screen-lineup-single.webp", "RushB app: smoke lineup with throw type and screenshot breakdown"), ("screen-nade-filters.webp", "RushB app: nade filters for retakes, insta smokes and one-way smokes")],
            "body": map_body(slug), "faq": map_faq(slug), "scripts": ["lineups.js"],
        })
    return pages


def grenade_body(kind):
    def body(r):
        g = GRENADES[kind]
        parts = [
            section(prose(g["article"](r))),
            section(head("Other grenade types") + "\n" + grenade_types(r, exclude=kind), " page-section--tight"),
        ]
        return "\n".join(parts)
    return body


def smokes_article(r):
    return f'''          <h2>What smokes do in CS2</h2>
          <p>Smokes in CS2 are volumetric: the cloud fills the space it lands in, reacts to light and can be opened for a moment by gunfire or an HE grenade. A good smoke blocks a line of sight long enough for your team to cross, plant or retake.</p>
          <h2>Types of smoke lineups</h2>
          <ul>
            <li><strong>Execute smokes</strong> cut the defenders’ angles when your team takes a bombsite.</li>
            <li><strong>Cross and mid smokes</strong> let you cross an open area or split the map.</li>
            <li><strong>One-way smokes</strong> let you see an enemy’s legs or body while they cannot see you.</li>
            <li><strong>Instant smokes</strong> are thrown from spawn or early positions to land before the enemy arrives.</li>
            <li><strong>Retake smokes</strong> isolate one angle so CTs can retake the site one fight at a time.</li>
          </ul>
          <h2>How to throw a smoke lineup</h2>
          <ol>
            <li>Stand in the exact position — corners, edges and textures are your reference points.</li>
            <li>Aim at the marked point on the wall, sky or object.</li>
            <li>Use the throw type the lineup asks for: normal throw, jump-throw, run-throw or a right-click lob.</li>
            <li>Check the landing in a practice match first, then use it in Premier or FACEIT.</li>
          </ol>
          {JUMP_THROW_NOTE}
          <h2>Smoke lineups in RushB</h2>
          <p>RushB shows every smoke on the map radar. In <strong>Single</strong> mode, tap a smoke and follow the position, aim point and throw type, with a screenshot breakdown and a video for each lineup. Filters show only retake smokes, insta smokes or one-way smokes. In <strong>Combo</strong> mode, the smokes of a full execute are grouped with the flashes and HE grenades that go with them, so you and your team know who throws what.</p>'''


def flashes_article(r):
    return f'''          <h2>Why flash lineups matter</h2>
          <p>A flashbang wins a duel before it starts. The difference between a good and a bad flash is timing and position: it should pop where the enemy is looking, not in front of your own team.</p>
          <h2>Types of flashes</h2>
          <ul>
            <li><strong>Pop flashes</strong> are thrown over or around a wall so they explode the moment they appear on the enemy’s screen.</li>
            <li><strong>Self flashes</strong> let you peek an angle on your own without blinding yourself.</li>
            <li><strong>Team flashes</strong> are thrown by a teammate for the player entering the site.</li>
            <li><strong>Retake flashes</strong> blind players who hold a planted bomb so CTs can swing together.</li>
          </ul>
          <h2>How to use flashes well</h2>
          <ol>
            <li>Call the flash before you throw it so teammates turn away or swing on time.</li>
            <li>Peek right after the pop — the blind lasts only a moment.</li>
            <li>Bounce flashes off walls and ceilings when the direct angle is visible to the enemy.</li>
            <li>Practise each lineup offline, then use it in matches.</li>
          </ol>
          <h2>Flash lineups in RushB</h2>
          <p>Flashes in RushB are filtered by map and side and come with the position, aim point and throw type. Learn a flash on its own in <strong>Single</strong> mode, or open a <strong>Combo</strong> to see which flashes go with which smokes during an execute, so a duo or a full team can use them together.</p>'''


def he_article(r):
    return f'''          <h2>What an HE grenade is for</h2>
          <p>An HE grenade deals damage in an area and briefly opens a hole in a smoke. It rarely kills on its own, but it sets up the fight: a damaged defender loses duels they would otherwise win.</p>
          <h2>Ways to use HE grenades</h2>
          <ul>
            <li><strong>Stack damage</strong> with your teammates’ grenades on common defender positions.</li>
            <li><strong>Finish low players</strong> after a trade instead of peeking them.</li>
            <li><strong>Stop a rush</strong> on a narrow chokepoint early in the round.</li>
            <li><strong>Open a smoke</strong> for a moment to catch players crossing behind it.</li>
          </ul>
          <h2>Tips for HE lineups</h2>
          <ol>
            <li>Throw at the positions defenders hold most often — the lineup tells you where.</li>
            <li>Time two HE grenades together for more damage on the same spot.</li>
            <li>Use sound and information first: an HE on an empty spot is a wasted $300.</li>
          </ol>
          <h2>HE lineups in RushB</h2>
          <p>RushB shows HE lineups on the same radar as the other grenades. In <strong>Single</strong> mode, filter by type, tap a landing spot and copy the throw, with a video for each lineup. In <strong>Combo</strong> mode, an HE is part of a full play — for example an HE on a common defender spot after the smokes and flash of a site take.</p>'''


def molotov_article(r):
    return f'''          <h2>Molotov and incendiary grenades</h2>
          <p>Terrorists buy the molotov and CTs buy the incendiary grenade; both cover an area in fire for a few seconds. Fire forces players out of close corners, delays pushes and buys time — and a smoke grenade puts the fire out.</p>
          <h2>Ways to use molotovs</h2>
          <ul>
            <li><strong>Clear close corners</strong> on a site before your team walks in.</li>
            <li><strong>Stop a push</strong> through a chokepoint and gain time for a rotation.</li>
            <li><strong>Post-plant</strong> molotovs on the bomb to delay or deny the defuse.</li>
            <li><strong>Retake molotovs</strong> to flush players out of their positions.</li>
          </ul>
          <h2>Tips for molotov lineups</h2>
          <ol>
            <li>Learn one post-plant molotov per bombsite you play on most.</li>
            <li>Throw it from a safe spot — a good lineup does not make you peek.</li>
            <li>Remember that an enemy smoke can put your fire out.</li>
          </ol>
          <h2>Molotov lineups in RushB</h2>
          <p>Molotov and incendiary lineups in RushB are filtered by map and side, with the position, aim point, throw type and a video guide for each throw. Use them one by one in <strong>Single</strong> mode, or as part of a <strong>Combo</strong> with the smokes and flashes of the same play.</p>'''


GRENADES = {
    "smokes": {"article": smokes_article},
    "flashes": {"article": flashes_article},
    "he-grenades": {"article": he_article},
    "molotovs": {"article": molotov_article},
}


# ---------------------------------------------------------------- tactics
def tactics_body(r):
    return "\n".join([
        section(head("What you get") + "\n" + tiles([
            {"title": "Site takes and fakes", "text": "Execute a bombsite with the right utility, or fake one site to pull rotations before you hit the other."},
            {"title": "Every round type", "text": "Filter tactics by buy, pistol, eco and force rounds, so you have a plan even with no money."},
            {"title": "Map-based strategies", "text": "Tactics are made for each map — Mirage, Inferno, Anubis and the rest of the competitive pool."},
            {"title": "Roles for each player", "text": "Learn who enters, who flashes and who holds the flank, so five players act as one team."},
            {"title": "Retakes", "text": "A planted bomb is not a lost round. Step-by-step retakes with video breakdowns."},
            {"title": "For FACEIT and Premier", "text": "Tactics are tagged so you see which ones work in pugs and which come from tier-1 teams."},
        ])),
        section(prose(f'''          <h2>How to use CS2 tactics in your matches</h2>
          <p>Most matches are lost before the first duel: five players peek one by one, without utility and without a plan. A tactic gives every player a job and a timing.</p>
          <ol>
            <li><strong>Pick the round type.</strong> A full-buy execute needs other tools than a pistol round or an eco.</li>
            <li><strong>Read the roles.</strong> Each tactic says who throws which grenade and who enters first.</li>
            <li><strong>Learn the utility.</strong> Open the smokes and flashes of the tactic in the <a href="{r}lineups/">lineups</a> section and practise them.</li>
            <li><strong>Call it before the round.</strong> One short call is enough when everyone knows the plan.</li>
          </ol>
          <h2>Tactics for duos and small stacks</h2>
          <p>You do not need a full five-stack. Many tactics work for two or three players who queue together; for those, see <a href="{r}setups/">solo and duo setups</a>.</p>''')),
    ])


TACTICS_FAQ = [
    ("How many tactics are in RushB?",
     "<p>More than 100 tactics for the competitive maps, from standard executes to strategies used by professional teams.</p>"),
    ("Do the tactics work in solo queue?",
     "<p>Tactics work best with players who know the plan. In solo queue, use the simpler ones or share the call in voice chat; for two or three players, use the duo and triple setups.</p>"),
    ("Are there tactics for eco and pistol rounds?",
     "<p>Yes. Tactics are filtered by buy, pistol, eco and force rounds.</p>"),
]


# ---------------------------------------------------------------- setups
def setups_body(r):
    return "\n".join([
        section(head("Three ways to play a round") + "\n" + tiles([
            {"kicker": "Solo", "title": "Solo play", "text": "Smart positions, off-angles and clutch moves for one player: where to stand, which utility to keep and when to fall back."},
            {"kicker": "Duo", "title": "Duo setups", "text": "Crossfires and coordinated utility for two players. Made for the most common FACEIT and Premier situation: you and a friend."},
            {"kicker": "Trio", "title": "Triple executes", "text": "Site defenses and executes for three players, with the role of each player and the grenades they throw."},
        ])),
        section(prose(f'''          <h2>Why setups matter</h2>
          <p>A crossfire turns a fair duel into a two-on-one. When two players hold different angles of the same entrance, the enemy can only look at one of them — and the other gets the kill.</p>
          <h2>How to use a duo setup</h2>
          <ol>
            <li>Agree on the setup before the round starts.</li>
            <li>Take your positions and check that your angles cover each other.</li>
            <li>Use the utility of the setup to slow the enemy and force them into the crossfire.</li>
            <li>Trade: if your partner dies, the setup tells you where to swing.</li>
          </ol>
          <p>In the app, solo, duo and triple setups are sorted by A site, mid and B site, and each one has a description and a video. Setups use the same grenades as the <a href="{r}lineups/">lineups</a> section, and for full-team plans see <a href="{r}tactics/">tactics</a>.</p>''')),
    ])


SETUPS_FAQ = [
    ("How many setups are in RushB?",
     "<p>More than 200 solo, duo and triple setups across the competitive maps.</p>"),
    ("What is a duo setup?",
     "<p>A plan for two players: positions that create a crossfire, the grenades each of you throws and what to do after the first kill or death.</p>"),
    ("Do setups work on FACEIT?",
     "<p>Yes. Setups are made for real matches in FACEIT and Premier, where most players queue alone or with one or two friends.</p>"),
]


# ---------------------------------------------------------------- AI coach
def ai_body(r):
    return "\n".join([
        section(head("Ask anything about CS2") + "\n" + tiles([
            {"title": "“I’m stuck at FACEIT level 4–6 — how do I reach level 10?”", "text": "Get a plan for your weak spots instead of generic advice."},
            {"title": "“How do I analyze demos like a pro player?”", "text": "Learn what to look at in your own demos and what to change."},
            {"title": "“What am I doing wrong? How do I find my mistakes?”", "text": "Describe a round and get an honest breakdown of the decisions."},
            {"title": "“How do I remove input lag and make shooting smooth?”", "text": "Settings, configs and habits that make your aim feel better."},
        ], cols=2)),
        section(prose(f'''          <h2>What the AI coach helps with</h2>
          <ul>
            <li><strong>Tactics and setups.</strong> It explains why a tactic works and when to use it.</li>
            <li><strong>Decisions.</strong> Rotate or hold, save or retake, peek or wait — talk through the situation.</li>
            <li><strong>Your playstyle.</strong> Tell it your role and level, and it adapts the advice to you.</li>
            <li><strong>Progress.</strong> Turn a goal like “reach FACEIT level 10” into steps you can practise.</li>
          </ul>
          <p>FACEIT level 10 starts at 2001 Elo. The AI coach works next to the <a href="{r}lineups/">lineups</a>, <a href="{r}tactics/">tactics</a> and <a href="{r}setups/">setups</a> in the app, so advice turns straight into something you can practise.</p>
          <p class="note">The AI coach gives advice, not guarantees. Check important settings and lineups in a practice match before you rely on them.</p>''')),
    ])


AI_FAQ = [
    ("What can I ask the RushB AI coach?",
     "<p>Anything about CS2: tactics, positions, utility, settings, demos, your mistakes and how to climb on FACEIT or in Premier.</p>"),
    ("Does the AI coach watch my matches?",
     "<p>No. You describe the situation or your problem in the chat, and the coach answers based on that.</p>"),
    ("Is the AI coach free?",
     "<p>The app is free to download. Access to some features, including parts of the AI coach, may require RushB Pro.</p>"),
]


# ---------------------------------------------------------------- binds
def binds_body(r):
    slots = "".join(
        f"<tr><td><code>{c}</code></td><td>{d}</td></tr>" for c, d in [
            ("slot6", "HE grenade"),
            ("slot7", "Flashbang"),
            ("slot8", "Smoke grenade"),
            ("slot9", "Decoy grenade"),
            ("slot10", "Molotov (T) or incendiary grenade (CT)"),
        ])
    return "\n".join([
        section(prose(f'''          <h2>What a bind is</h2>
          <p>A bind connects a key to a command. Instead of typing in the console every time, you press one key. Binds are used for jumping on the mouse wheel, practice commands, voice and volume, buying and many other things.</p>
          <h2>How to open the console in CS2</h2>
          <ol>
            <li>Go to <strong>Settings → Game</strong> and turn on <strong>Enable Developer Console (~)</strong>.</li>
            <li>Press <code>~</code> in the game to open the console.</li>
            <li>Type a command and press Enter. A bind looks like this: <code>bind "KEY" "command"</code>.</li>
          </ol>
          <h2>Binds that still work in 2026</h2>
          <p>A bind is allowed on Valve servers when one key does one action. The most popular one is jumping on the mouse wheel:</p>
          {code('bind mwheelup +jump\nbind mwheeldown +jump')}
          {JUMP_THROW_NOTE}
          <h2>Grenade binds: one key for each nade</h2>
          <p>By default <code>4</code> cycles through your grenades, so in a fight you can pull a flash when you wanted a smoke. Give each grenade its own key instead. One key selects one grenade, so these binds are allowed everywhere. Paste these lines into the console or your autoexec:</p>
          {code(GRENADE_BINDS)}
          <p>That puts the flash on <code>Z</code>, the smoke on <code>X</code>, the HE on <code>C</code> and the molotov on <code>V</code>. Use any keys you like — these are the slot commands behind them:</p>
          <table class="cmd-table"><thead><tr><th>Command</th><th>Selects</th></tr></thead><tbody>{slots}</tbody></table>
          <h2>How to throw nades faster</h2>
          <ul>
            <li><strong>Select the nade with its own key</strong> instead of cycling with <code>4</code>.</li>
            <li><strong>Pick the throw on the way:</strong> left click for a long throw, right click for a short underhand throw, both buttons for a medium one.</li>
            <li><strong>Jump-throws need no bind:</strong> jump and release the grenade at the same moment.</li>
            <li><strong>Know the lineup before the round:</strong> the position and aim point are what take time, not the throw itself.</li>
          </ul>
          <h2>Practice commands for nades</h2>
          <p>Infinite grenades, the grenade camera, rethrow and clearing smokes are commands for your own server. We put them all, with a ready config and practice binds, in a separate guide: <a href="{r}guides/cs2-practice-commands/">how to practice nades in CS2</a>.</p>
          <h2>Binds and commands in RushB</h2>
          <p>The Binds section of the app has ready-made binds and a Console tab with commands you can copy in one tap — no searching through forums and old CS:GO guides.</p>''')),
    ])


BINDS_FAQ = [
    ("Does the jump-throw bind still work in CS2?",
     "<p>Not on Valve servers. Since the August 2024 update, binds that combine more than one movement or attack action are blocked, and players who automate several actions from one key may be kicked. Valve made the jump-throw reliable without a bind.</p>"),
    ("How do I enable the console in CS2?",
     "<p>Settings → Game → Enable Developer Console (~). Then press <code>~</code> in the game.</p>"),
    ("Can I use practice commands in matchmaking?",
     "<p>No. Commands that need <code>sv_cheats 1</code>, such as <code>sv_rethrow_last_grenade</code> or <code>noclip</code>, only work on your own server or in an offline match.</p>"),
    ("How do I bind grenades to separate keys in CS2?",
     "<p>Use the slot commands: <code>slot6</code> is the HE grenade, <code>slot7</code> the flashbang, <code>slot8</code> the smoke, <code>slot9</code> the decoy and <code>slot10</code> the molotov or incendiary. For example, <code>bind x \"slot8\"</code> puts the smoke on X.</p>"),
    ("Where do I save binds so I don’t type them every time?",
     "<p>Put them in an autoexec config file in your CS2 cfg folder and add <code>+exec autoexec</code> to the game’s launch options in Steam.</p>"),
]


# ---------------------------------------------------------------- guides
def practice_body(r):
    rows = "".join(
        f"<tr><td><code>{c}</code></td><td>{d}</td></tr>" for c, d in [
            ("sv_cheats 1", "Turns on cheat commands on your own server. Most commands below need it."),
            ("sv_infinite_ammo 1", "Infinite grenades and ammo: a grenade stays in your hand after you throw it."),
            ("sv_infinite_ammo 2", "Infinite ammo that still needs reloading."),
            ("ammo_grenade_limit_total 5", "Carry all grenade types at once."),
            ("sv_grenade_trajectory_prac_pipreview 1", "The grenade camera: a small window shows where the nade will land while you aim."),
            ("sv_grenade_trajectory_prac_trailtime 8", "Keeps the flight path of a thrown grenade on screen for 8 seconds."),
            ("sv_rethrow_last_grenade", "Throws your last grenade again from the same spot, with the same angle and power."),
            ("ent_fire smokegrenade_projectile kill", "Removes every smoke on the map at once."),
            ("ent_remove_all inferno", "Removes the fire of molotovs and incendiaries on the ground."),
            ("noclip", "Fly through walls to see your smoke or flash from the enemy side."),
            ("give weapon_smokegrenade", "Gives you a smoke. Also works with weapon_flashbang, weapon_hegrenade, weapon_molotov, weapon_incgrenade and weapon_decoy."),
            ("mp_buy_anywhere 1", "Buy grenades anywhere on the map."),
            ("mp_buytime 9999", "Buy time never runs out."),
            ("mp_freezetime 0", "No freeze time at the start of a round."),
            ("mp_roundtime_defuse 60", "A 60-minute round on bomb maps."),
            ("bot_kick", "Removes all bots."),
            ("mp_restartgame 1", "Restarts the match after 1 second."),
        ])
    return "\n".join([
        section(head("Option 1: Practice mode, no console",
                     "CS2 has a practice server built in. It covers the basics in four clicks.") + "\n" + tiles([
            {"title": "Open Play → Practice", "text": "In the main menu go to Play and open the Practice tab."},
            {"title": "Turn on three options", "text": "Grenade Camera, Infinite Ammo and Infinite Warmup — the switches in the list on the left."},
            {"title": "Pick a map", "text": "Choose the map you want to learn, for example Mirage or Inferno."},
            {"title": "Press Go", "text": "You land on an empty server with unlimited nades and a camera that shows where each one lands."},
        ], cols=4, numbered=True), " page-section--tight"),
        section(prose(f'''          <h2>Option 2: the practice config</h2>
          <p>Practice mode covers the basics. For a rethrow key, clearing smokes and full control, start an offline game, open the console with <code>~</code> and paste this config. If the console does not open, turn it on in <strong>Settings → Game → Enable Developer Console</strong>.</p>
          {code(PRACTICE_CONFIG)}
          <p>To load it with one command, save the lines as <code>practice.cfg</code> in the <code>game/csgo/cfg</code> folder of your CS2 install. Then type <code>exec practice</code> in the console.</p>
          <h2>Every nade practice command</h2>
          <p>All of these work only on your own server or in an offline match. They do nothing in Premier, Competitive or on FACEIT.</p>
          <table class="cmd-table"><thead><tr><th>Command</th><th>What it does</th></tr></thead><tbody>{rows}</tbody></table>
          <h2>Binds for nade practice</h2>
          <p>Three keys save the most time: repeat the last grenade, clear the smokes and fly to the other side to check the result.</p>
          {code(PRACTICE_BINDS)}
          <p>These binds need <code>sv_cheats 1</code>, so they only work offline. Binds that pick a grenade with one key are on our <a href="{r}binds/">CS2 binds</a> page.</p>
          <h2>Commands from old guides that no longer work</h2>
          <p>Many configs online were written for CS:GO. In CS2, <code>sv_grenade_trajectory</code> and <code>sv_grenade_trajectory_time</code> are gone: the grenade camera and <code>sv_grenade_trajectory_prac_trailtime</code> replace them. Some guides also list <code>cl_grenadepreview</code> — you don’t need it, the grenade camera already shows where the nade lands.</p>
          {JUMP_THROW_NOTE}
          <h2>A practice routine that works</h2>
          <ol>
            <li><strong>Learn the lineup first.</strong> Find the position, the aim point and the throw type — in RushB each lineup has a screenshot breakdown and a video.</li>
            <li><strong>Throw it with the grenade camera on.</strong> Watch where it lands before you even release.</li>
            <li><strong>Repeat it with the rethrow key</strong> and check it from the enemy side with noclip.</li>
            <li><strong>Clear the smoke and throw it again by hand</strong> until it lands ten times in a row.</li>
            <li><strong>Use it in deathmatch or a casual match</strong> before you count on it in Premier or on FACEIT.</li>
          </ol>
          <h2>Workshop maps for nade practice</h2>
          <p>The Steam Workshop has practice maps made for utility. <strong>Yprac Hub</strong> combines a nade trainer with aim and prefire drills. In <strong>Play → Practice</strong> you can also open the Workshop with the Map Guide filter and download a guide for the map you play; then turn on <em>Use Map Guide</em> before you start.</p>
          <h2>Practise with friends</h2>
          <p>On a private server the host — or anyone with RCON access — runs the config, and everyone on the server gets unlimited nades and the grenade camera. Agree on who throws and who watches from the other side: it is the fastest way to learn smokes for a full execute.</p>''')),
        section(head("Learn the lineups in RushB",
                     "The commands make practice fast. RushB tells you what to practise: 2000+ lineups for the competitive maps with position, aim point, throw type and video.") +
                "\n" + grenade_types(r), " page-section--tight"),
    ])


PRACTICE_FAQ = [
    ("What is the command for infinite nades in CS2?",
     "<p>Type <code>sv_cheats 1</code>, then <code>sv_infinite_ammo 1</code>. Add <code>ammo_grenade_limit_total 5</code> to carry every grenade type at once. It works on your own server or in an offline match.</p>"),
    ("How do I rethrow my last grenade?",
     "<p>Use <code>sv_rethrow_last_grenade</code>. Bind it to a key — <code>bind n \"sv_rethrow_last_grenade\"</code> — and the game throws the same grenade again from the same spot, even while you watch from somewhere else.</p>"),
    ("How do I clear smokes instantly?",
     "<p>With <code>sv_cheats 1</code> on, <code>ent_fire smokegrenade_projectile kill</code> removes every smoke on the map. <code>ent_remove_all inferno</code> removes molotov fire.</p>"),
    ("How do I see where my grenade will land?",
     "<p>Turn on the grenade camera: <code>sv_grenade_trajectory_prac_pipreview 1</code>, or the Grenade Camera switch in Play → Practice. A small window shows the landing spot while you aim.</p>"),
    ("Can I use practice commands in Premier or on FACEIT?",
     "<p>No. They need <code>sv_cheats 1</code>, which only works on your own server or in an offline match.</p>"),
    ("Do I need a jump-throw bind to practise lineups?",
     "<p>No. Since August 2024 binds that combine several movement or attack actions don’t work on Valve servers, and the jump-throw is reliable without one: jump and release the grenade at the same moment.</p>"),
]


def guides_body(r):
    return "\n".join([
        section(tiles([
            {"kicker": "Practice", "title": "How to practice nades in CS2",
             "text": "Practice mode, a ready config, every command for infinite nades, rethrow and clearing smokes, and a routine that makes lineups stick.",
             "href": f"{r}guides/cs2-practice-commands/", "more": "Read"},
            {"kicker": "Binds", "title": "CS2 binds and grenade binds",
             "text": "Binds that still work on Valve servers, one key for each grenade and how to throw nades faster.",
             "href": f"{r}binds/", "more": "Read"},
            {"kicker": "FACEIT", "title": "How to get FACEIT Level 10",
             "text": "Level 10 in numbers, what Season 10 changes and the habits that raise your win rate.",
             "href": f"{r}guides/faceit-level-10/", "more": "Read"},
            {"kicker": "Tool", "title": "FACEIT Elo calculator",
             "text": "Your level, the Elo to the next one and how many matches it takes at your win rate.",
             "href": f"{r}tools/faceit-elo-calculator/", "more": "Open"},
            {"kicker": "Updates", "title": "CS2 updates & patch notes",
             "text": "The last 50 Counter-Strike 2 updates in plain words, with what each one means for your game.",
             "href": f"{r}updates/", "more": "Read"},
            {"kicker": "Smokes", "title": "CS2 smoke lineups",
             "text": "Execute smokes, one-ways, instant and retake smokes for the competitive maps.",
             "href": f"{r}lineups/smokes/", "more": "Read"},
        ]), " page-section--tight"),
    ])


# ---------------------------------------------------------------- FACEIT
# FACEIT CS2 skill levels: (level, minimum Elo). Source: FACEIT Support, "FACEIT CS2 Elo and skill levels".
FACEIT_LEVELS = [(1, 100), (2, 501), (3, 751), (4, 901), (5, 1051), (6, 1201), (7, 1351), (8, 1531), (9, 1751), (10, 2001)]


def faceit_level(elo):
    lvl = 1
    for n, lo in FACEIT_LEVELS:
        if elo >= lo:
            lvl = n
    return lvl


def elo_estimate(elo, target, wr, gain=25, loss=25, per_day=3):
    """The same maths as assets/js/elo.js, used for the page's first render."""
    import math
    diff = max(target - elo, 0)
    net = wr / 100 * gain - (1 - wr / 100) * loss
    lvl = faceit_level(elo)
    nxt = next((lo for n, lo in FACEIT_LEVELS if n == lvl + 1), None)
    out = {"level": lvl, "next": (nxt - elo) if nxt else "—", "diff": diff,
           "netwins": math.ceil(diff / gain) if diff else 0}
    if diff == 0:
        out.update(matches="0", note="You are already there.")
    elif net == 0:
        out.update(matches="—", note=f"At {wr:g}% your wins and losses cancel out, so you stay where you are. Raise your win rate first.")
    elif net < 0:
        out.update(matches="—", note=f"At {wr:g}% you lose Elo on average, so you won’t climb. Raise your win rate above 50% first.")
    else:
        m = math.ceil(diff / net)
        days = math.ceil(m / per_day)
        out.update(matches=f"{m:,}", note=f"At {wr:g}% you gain about {net:.1f} Elo per match. At {per_day} matches a day that is about {days:,} days.")
    return out


def levels_table():
    rows = []
    for i, (n, lo) in enumerate(FACEIT_LEVELS):
        nxt = FACEIT_LEVELS[i + 1][1] if i + 1 < len(FACEIT_LEVELS) else None
        rng = f"{lo:,}–{nxt - 1:,}" if nxt else f"{lo:,}+"
        width = f"{nxt - lo}" if nxt else "no limit"
        wins = f"{-(-(nxt - lo) // 25)}" if nxt else "—"
        rows.append(f"<tr><td>Level {n}</td><td>{rng}</td><td>{width}</td><td>{wins}</td></tr>")
    return ('<table class="cmd-table"><thead><tr><th>Level</th><th>Elo</th><th>Elo in the level</th>'
            '<th>Net wins to pass it at 25 Elo</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")


FACEIT_SOURCES = (
    '          <p class="sources">Sources: FACEIT Support — '
    '<a href="https://support.faceit.com/hc/en-us/articles/10525200579740-FACEIT-CS2-Elo-and-skill-level" rel="noopener">FACEIT CS2 Elo and skill levels</a>, '
    '<a href="https://support.faceit.com/hc/en-us/articles/14211743579036-Improved-Elo-Formula-FAQ" rel="noopener">Improved Elo Formula FAQ</a>, '
    '<a href="https://support.faceit.com/hc/en-us/articles/28898322786076" rel="noopener">Season 9 soft reset</a>; '
    'Season 10 dates as announced by FACEIT.</p>'
)


def calculator_form(r):
    d = elo_estimate(1300, 2001, 55)
    opts = "".join(f'<option value="{lo}"{" selected" if n == 10 else ""}>Level {n} ({lo:,} Elo)</option>'
                   for n, lo in FACEIT_LEVELS[1:])
    calc = f'''        <form class="elo-calc" id="elo-calc" novalidate>
          <div class="elo-calc__inputs">
            <label class="field"><span class="field__label">Your Elo</span><input class="field__input" type="number" name="elo" value="1300" min="100" max="6000" step="1" inputmode="numeric" /></label>
            <label class="field"><span class="field__label">Goal</span><select class="field__input" name="target">{opts}</select></label>
            <label class="field"><span class="field__label">Win rate, %</span><input class="field__input" type="number" name="wr" value="55" min="1" max="99" step="1" inputmode="numeric" /></label>
            <label class="field"><span class="field__label">Matches per day</span><input class="field__input" type="number" name="perday" value="3" min="1" max="30" step="1" inputmode="numeric" /></label>
            <details class="elo-calc__more">
              <summary>Elo per win and per loss</summary>
              <div class="elo-calc__pair">
                <label class="field"><span class="field__label">Per win</span><input class="field__input" type="number" name="gain" value="25" min="1" max="60" step="1" inputmode="numeric" /></label>
                <label class="field"><span class="field__label">Per loss</span><input class="field__input" type="number" name="loss" value="25" min="1" max="60" step="1" inputmode="numeric" /></label>
              </div>
            </details>
          </div>
          <div class="elo-calc__result" aria-live="polite">
            <div class="elo-stat"><span>Your level</span><strong data-out="level">{d["level"]}</strong></div>
            <div class="elo-stat"><span>Elo to next level</span><strong data-out="next">{d["next"]}</strong></div>
            <div class="elo-stat"><span>Elo to your goal</span><strong data-out="diff">{d["diff"]}</strong></div>
            <div class="elo-stat"><span>Net wins needed</span><strong data-out="netwins">{d["netwins"]}</strong></div>
            <div class="elo-stat elo-stat--main"><span>Matches to your goal</span><strong data-out="matches">{d["matches"]}</strong></div>
            <p class="elo-calc__note" data-out="note">{d["note"]}</p>
          </div>
        </form>'''
    return calc


def calculator_body(r):
    return "\n".join([
        section(prose(f'''          <h2>FACEIT levels and Elo</h2>
          <p>FACEIT turns your Elo into a level from 1 to 10. Level 10 has no upper limit, and the top 1,000 players at Level 10 get the Challenger rank.</p>
          {levels_table()}
          <h2>How the estimate works</h2>
          <p>FACEIT has not published its exact formula. What it does say is that the Elo you win or lose depends on how likely your team was to win: beat a stronger team and you get more, lose to a weaker one and you drop more. Between evenly matched teams a match moves you about 25 Elo, which is the default here.</p>
          <p>So the calculator works with averages: your net Elo per match is <em>win rate × Elo per win − loss rate × Elo per loss</em>, and the matches to your goal are the Elo you still need divided by that number. At 55% and 25 Elo per match that is about 2.5 Elo per match — which is why the climb feels slow, and why your win rate matters more than anything else.</p>
          <h2>What the calculator does not count</h2>
          <ul>
            <li><strong>Placement matches.</strong> The first 10 matches of a season move your Elo more than usual.</li>
            <li><strong>Your own performance.</strong> For Levels 1–9, FACEIT adds a small bonus or penalty for individual impact, on top of the result.</li>
            <li><strong>Leavers.</strong> If a teammate leaves and you still win, you get the normal Elo and the leaver only half.</li>
          </ul>
          <p>Want the plan, not just the number? Read <a href="{r}guides/faceit-level-10/">how to get FACEIT Level 10</a>.</p>
{FACEIT_SOURCES}''')),
    ])


CALCULATOR_FAQ = [
    ("What Elo is FACEIT Level 10?",
     "<p>Level 10 starts at 2,001 Elo and has no upper limit. Level 9 is 1,751–2,000 Elo.</p>"),
    ("How much Elo do you get per win on FACEIT?",
     "<p>About 25 in a match between evenly rated teams. You get more for beating a stronger team and less for beating a weaker one, and the same goes for losses in reverse.</p>"),
    ("How many matches does it take to reach Level 10?",
     "<p>It depends on your win rate. From 1,200 Elo you need 801 Elo: about 321 matches at a 55% win rate, or about 161 at 60%. Use the calculator above with your own numbers.</p>"),
    ("Does K/D affect FACEIT Elo?",
     "<p>Only a little. The match result decides most of it; for Levels 1–9 FACEIT adds a small amount for individual impact.</p>"),
    ("What Elo do new FACEIT players start with?",
     "<p>If you have Prime and enough Premier wins, FACEIT converts your latest Premier rating into Elo. Otherwise you start at 1,000 Elo.</p>"),
]


def level10_body(r):
    import math
    starts = [1000, 1200, 1350, 1530, 1750, 1900]
    rates = [52, 55, 60]
    head_cells = "".join(f"<th>{w}% win rate</th>" for w in rates)
    rows = []
    for e in starts:
        need = 2001 - e
        cells = "".join(f"<td>{math.ceil(need / (25 * (2 * w / 100 - 1))):,}</td>" for w in rates)
        rows.append(f"<tr><td>{e:,} (Level {faceit_level(e)})</td><td>{need:,}</td>{cells}</tr>")
    table = (f'<table class="cmd-table"><thead><tr><th>Your Elo</th><th>Elo to Level 10</th>{head_cells}</tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table>')
    return "\n".join([
        section(prose(f'''          <h2>Level 10 in numbers</h2>
          <p>Level 10 starts at <strong>2,001 Elo</strong>. The Elo you need is 2,001 minus your Elo, and at about 25 Elo per even match that is your gap divided by 25 in <em>net</em> wins — wins minus losses. From 1,500 Elo that is 21 more wins than losses.</p>
          <p>How many matches that takes depends on one number: your win rate. Matches to Level 10 at 25 Elo per win and per loss:</p>
          {table}
          <p>Put in your own Elo and win rate in the <a href="{r}tools/faceit-elo-calculator/">FACEIT Elo calculator</a>.</p>
          <h2>Your win rate is the whole game</h2>
          <p>The table says it plainly: going from 52% to 55% cuts the road by more than half, and 60% halves it again. Elo follows wins, not frags — for Levels 1–9 FACEIT adds only a small amount for individual impact. So the question is not “how do I get more kills” but “what makes my team win one more round in ten”. Most of that is preparation, not aim.</p>
          <h2>Season 10 starts on December 9</h2>
          <p>FACEIT Season 10 starts on December 9, 2026, and Season 9 ends the day before. The new season opens with a soft Elo reset — the higher your Elo, the more it moves — and 10 placement matches, parties included. During placements your Elo moves more than usual and your level stays hidden until you finish all ten. Staying active before the end of the season keeps the adjustment smaller, and strong placements can start you higher.</p>
          <h2>Habits that raise your win rate</h2>
          <ol>
            <li><strong>Pick two or three maps and learn them.</strong> Knowing the standard smokes, flashes and molotovs on your maps wins rounds before the first duel. Start with our free <a href="{r}lineups/mirage/">Mirage</a>, <a href="{r}lineups/inferno/">Inferno</a> and <a href="{r}lineups/dust2/">Dust 2</a> lineups.</li>
            <li><strong>Throw the utility your team needs.</strong> Five people with no nades lose to two players with a plan. Learn two executes and one retake per site.</li>
            <li><strong>Queue with a friend and set up together.</strong> A duo with fixed crossfires is the most common FACEIT situation — see our <a href="{r}setups/">solo and duo setups</a>.</li>
            <li><strong>Have a plan for every round type.</strong> Pistol, eco, force and full buy each need a default; <a href="{r}tactics/">tactics</a> by round type help here.</li>
            <li><strong>Review your losses, not your wins.</strong> One demo a day of a lost match shows the same few mistakes again and again. You can ask the <a href="{r}ai-coach/">AI coach</a> what to look for.</li>
            <li><strong>Don’t leave and don’t tilt-queue.</strong> A leaver gets only half the Elo even if the team wins. After two losses in a row, take a break before the next match.</li>
          </ol>
          <h2>How long does it really take?</h2>
          <p>At three matches a day, a 55% player starting from 1,200 Elo needs about 321 matches — roughly three and a half months. At 60% it is about 161 matches, under two months. Every point of win rate you add by preparing better is worth more than any number of matches played on autopilot.</p>
{FACEIT_SOURCES}''')),
        section(head("Tools for the climb") + "\n" + tiles([
            {"kicker": "Tool", "title": "FACEIT Elo calculator",
             "text": "Your level, the Elo to the next one and how many matches it takes at your win rate.",
             "href": f"{r}tools/faceit-elo-calculator/", "more": "Open"},
            {"kicker": "Nades", "title": "Free lineups by map",
             "text": "Smokes, flashes, molotovs and HE grenades with video for the seven competitive maps.",
             "href": f"{r}lineups/#maps", "more": "Open"},
            {"kicker": "Practice", "title": "How to practice nades",
             "text": "Unlimited grenades, the grenade camera and a rethrow key — set up in two minutes.",
             "href": f"{r}guides/cs2-practice-commands/", "more": "Read"},
        ]), " page-section--tight"),
    ])


LEVEL10_FAQ = [
    ("How long does it take to get FACEIT Level 10?",
     "<p>From 1,200 Elo at a 55% win rate, about 321 matches; at 60%, about 161. At 52% it takes about 801 matches. Your win rate decides it.</p>"),
    ("Can you get Level 10 solo?",
     "<p>Yes. Elo follows the team result, so a solo player climbs by winning more rounds with information and utility, not only by fragging. Queuing with a friend makes it easier to play set crossfires and executes.</p>"),
    ("Will Season 10 reset my FACEIT level?",
     "<p>Not fully. Season 10 starts on December 9, 2026 with a soft reset: higher Elo moves more, and 10 placement matches decide your starting point. Your level is hidden until you finish them.</p>"),
    ("Is Level 10 the highest FACEIT rank?",
     "<p>Level 10 is the highest level and starts at 2,001 Elo. The top 1,000 players at Level 10 hold the Challenger rank.</p>"),
]


# ---------------------------------------------------------------- CS2 updates
# Our own summaries of Valve's CS2 update posts (see _build/data/updates.json). Newest first.
UPDATES = _json.load(open(_os.path.join(_os.path.dirname(__file__), "data", "updates.json"), encoding="utf-8"))["updates"]
STEAM_NEWS = "https://store.steampowered.com/news/app/730/view/"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def _update_ids():
    seen, ids = {}, []
    for u in UPDATES:
        n = seen.get(u["date"], 0) + 1
        seen[u["date"]] = n
        ids.append(f"update-{u['date']}" + (f"-{n}" if n > 1 else ""))
    return ids


def _nice_date(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


def updates_body(r):
    ids = _update_ids()
    months = {}
    for u, uid in zip(UPDATES, ids):
        months.setdefault(u["date"][:7], []).append((u, uid))
    nav = "".join(f'<a href="#month-{k}">{MONTHS[int(k[5:]) - 1]} {k[:4]} <span>{len(v)}</span></a>' for k, v in months.items())
    blocks = []
    for k, items in months.items():
        cards = []
        for u, uid in items:
            tags = "".join(f'<span class="lineup__tag">{_html.escape(t)}</span>' for t in u["tags"])
            points = "".join(f"<li>{_html.escape(p)}</li>" for p in u["points"])
            matters = (f'<p class="update__matters"><strong>What it means for you:</strong> {_html.escape(u["matters"])}</p>'
                       if u.get("matters") else "")
            cards.append(f'''          <article class="update" id="{uid}">
            <div class="update__meta"><time datetime="{u["date"]}">{_nice_date(u["date"])}</time>{tags}</div>
            <h3 class="update__title">{_html.escape(u["title"])}</h3>
            <ul class="update__points">{points}</ul>
            {matters}
            <a class="update__source" href="{STEAM_NEWS}{u["gid"]}" rel="noopener">Official patch notes on Steam →</a>
          </article>''')
        blocks.append(f'''        <h2 class="update-month" id="month-{k}">{MONTHS[int(k[5:]) - 1]} {k[:4]}</h2>
        <div class="update-list">
{chr(10).join(cards)}
        </div>''')
    intro = prose('''          <p>Valve ships a Counter-Strike 2 update every week or two. Below are the last 50, newest first, in plain words: what changed, and for the updates that touch maps, grenades or gameplay, what it means for your game. Each one links to Valve’s official notes on Steam.</p>''')
    return "\n".join([
        section(intro + '\n        <nav class="lineup-nav" aria-label="Jump to a month">' + nav + "</nav>", " page-section--tight"),
        section("\n".join(blocks), " page-section--tight"),
        section(head("Keep your lineups up to date") + "\n" + tiles([
            {"kicker": "Nades", "title": "Free lineups by map",
             "text": "Smokes, flashes, molotovs and HE grenades with video for the seven competitive maps.",
             "href": f"{r}lineups/#maps", "more": "Open"},
            {"kicker": "Practice", "title": "How to practice nades",
             "text": "Re-test a lineup after an update in two minutes: unlimited nades, grenade camera, rethrow.",
             "href": f"{r}guides/cs2-practice-commands/", "more": "Read"},
            {"kicker": "Binds", "title": "CS2 binds that still work",
             "text": "Grenade binds, the mouse-wheel jump and why the jump-throw bind is gone.",
             "href": f"{r}binds/", "more": "Read"},
        ]), " page-section--tight"),
    ])


def updates_faq():
    last = UPDATES[0]
    return [
        ("When was the last CS2 update?",
         f"<p>The latest update on this page is from {_nice_date(last['date'])}: {_html.escape(last['title'][0].lower() + last['title'][1:])}. We add new updates at the top of this page.</p>"),
        ("Which maps are in the CS2 Active Duty pool?",
         "<p>Since Premier Season Five began on July 8, 2026: Ancient, Anubis, Cache, Dust II, Inferno, Mirage and Nuke. Cache came in and Overpass went out with that update.</p>"),
        ("Can a CS2 update break my grenade lineups?",
         "<p>Yes. Clipping changes, new geometry or a change in player height can move where a grenade lands. In 2026 Valve warned that lineups thrown from slopes may have changed with the new animation system, and Cache’s grenade clipping changed several times. Re-test a lineup in practice after a big map update.</p>"),
        ("Where can I read the official CS2 patch notes?",
         "<p>Valve posts every update on the Counter-Strike 2 news page on Steam. Each entry on this page links to its official post.</p>"),
    ]


# ---------------------------------------------------------------- FAQ
FAQ = [
    ("What is RushB?",
     "<p>RushB is a CS2 companion app: 2000+ single and combo grenade lineups, 100+ tactics, 200+ solo and duo setups, binds and console commands, and an AI coach — in one app for iPhone and Android.</p>"),
    ("Is RushB free?",
     "<p>Yes, RushB is free to download. Some content and features are part of the RushB Pro subscription, which you can buy in the app.</p>"),
    ("Which devices does RushB work on?",
     "<p>iPhone (<a href=\"https://apps.apple.com/app/id6738445061\">App Store</a>) and Android (<a href=\"https://play.google.com/store/apps/details?id=guide.pro.rush.b\">Google Play</a>). A web app is coming soon.</p>"),
    ("Can I buy RushB Pro on the website?",
     "<p>Not yet. Subscriptions are bought and managed inside the app through the App Store or Google Play.</p>"),
    ("How do I cancel my subscription?",
     "<p><strong>iPhone:</strong> Settings → your name → Subscriptions → RushB → Cancel Subscription.</p><p><strong>Android:</strong> Google Play → your profile → Payments &amp; subscriptions → Subscriptions → RushB → Cancel.</p><p>Deleting the app does not cancel a subscription.</p>"),
    ("Is RushB a cheat? Can I get banned for using it?",
     "<p>No. RushB is a guide: it does not run alongside the game and does not change game files. You learn the lineups and tactics in the app and use them yourself.</p>"),
    ("Is RushB affiliated with Valve or FACEIT?",
     "<p>No. RushB is an independent project and is not affiliated with Valve, FACEIT or other game publishers.</p>"),
    ("How old do I need to be to use RushB?",
     "<p>You must be at least 13 years old, as stated in our <a href=\"../terms.html\">Terms of Use</a>.</p>"),
    ("How do I contact support?",
     "<p>Email <a href=\"mailto:support@therushb.com\">support@therushb.com</a> or use the <a href=\"../#contact\">contact form</a>.</p>"),
]


def faq_body(r):
    return ""


# ---------------------------------------------------------------- About
def about_body(r):
    return "\n".join([
        section(prose(f'''          <h2>Why we made RushB</h2>
          <p>Most players don’t lose because of their aim. They lose because they don’t know the lineups, the tactics and the setups that higher-level players use every round. That knowledge is spread across hundreds of videos and old forum posts.</p>
          <p>RushB puts it in one app: grenade lineups for every competitive map, tactics for every round type, setups for solo players and duos, binds and console commands, and an AI coach that answers your questions. Our goal is simple — help players climb, from their first FACEIT matches to level 10.</p>
          <h2>Who we are</h2>
          <p>RushB is built by a small team of Counter-Strike players, developers and designers. The app is published by Mosaic Dynamics LTD.</p>
          <h2>Independent project</h2>
          <p>RushB is not affiliated with Valve, FACEIT or other game publishers. Counter-Strike and CS2 are trademarks of Valve Corporation.</p>
          <h2>Contact</h2>
          <p>Questions, partnerships or feedback: <a href="mailto:support@therushb.com">support@therushb.com</a> or the <a href="{r}#contact">contact form</a>. Follow us on <a href="https://www.tiktok.com/@rushb.guide">TikTok</a>, <a href="https://www.youtube.com/@rushb_guide">YouTube</a> and <a href="https://www.instagram.com/rushb.guide/">Instagram</a>.</p>''')),
        section(head("What’s inside the app") + "\n" + tiles([
            {"title": "Nades", "text": "2000+ single and combo lineups: smokes, flashes, HE and molotovs.", "href": f"{r}lineups/", "more": "Lineups"},
            {"title": "Tactics", "text": "100+ tactics for buy, pistol, eco and force rounds.", "href": f"{r}tactics/", "more": "Tactics"},
            {"title": "Setups", "text": "200+ solo, duo and triple setups.", "href": f"{r}setups/", "more": "Setups"},
            {"title": "AI coach", "text": "Ask anything about CS2 and your game.", "href": f"{r}ai-coach/", "more": "AI coach"},
        ], cols=4), " page-section--tight"),
    ])


# ---------------------------------------------------------------- page list
PAGES = [
    {
        "slug": "lineups/", "nav": "Nades",
        "title": "CS2 Nades: Smoke, Flash, HE & Molotov Lineups | RushB",
        "description": "2000+ CS2 nades in one app: smoke, flash, HE and molotov lineups for every competitive map, with position, aim point, throw type and video.",
        "crumb": "Nades",
        "h1": 'CS2 <span class="accent">nades</span> &amp; lineups for every map',
        "lead": "Smokes, flashes, HE grenades and molotovs — find a throw by map, grenade type and side, see exactly where to stand and aim, and land it in your next match.",
        "stats": [('2000<span class="accent">+</span>', "lineups"), ("4", "grenade types"), ("T&nbsp;/&nbsp;CT", "both sides")],
        "screens": [("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-nades-combo.webp", "RushB app: combo grenades on the Mirage radar"), ("screen-lineup-single.webp", "RushB app: B site smoke lineup with throw type and screenshot breakdown")],
        "body": lineups_body, "faq": LINEUPS_FAQ,
    },
    {
        "slug": "lineups/smokes/", "nav": "Nades",
        "title": "CS2 Smoke Lineups for Every Map | RushB",
        "description": "Learn CS2 smoke lineups: execute smokes, one-ways, instant and retake smokes for every competitive map, with position, aim point and video guide.",
        "crumb": "Smokes", "crumbs": [("Nades", "lineups/")],
        "h1": 'CS2 <span class="accent">smoke</span> lineups',
        "lead": "Execute smokes, one-ways, instant smokes and retake smokes for the competitive maps — with the exact position, aim point and throw type.",
        "screens": [("screen-nade-filters.webp", "RushB app: nade filters for retakes, insta smokes and one-way smokes"), ("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-lineup-single.webp", "RushB app: B site smoke lineup with throw type and screenshot breakdown")],
        "body": grenade_body("smokes"),
        "faq": [
            ("What is a one-way smoke?", "<p>A smoke placed so that you can see an enemy (often their legs or body) while they cannot see you through the cloud.</p>"),
            ("Why doesn’t my smoke land in the same spot?", "<p>Your position, aim point or throw type is slightly off. Practise with <code>sv_rethrow_last_grenade</code> and the trajectory preview in an offline match.</p>"),
            ("Can you shoot through smokes in CS2?", "<p>Bullets and HE grenades open a smoke for a moment, so a smoke is not a perfect wall. Combine it with flashes and timing.</p>"),
        ],
    },
    {
        "slug": "lineups/flashes/", "nav": "Nades",
        "title": "CS2 Flash Lineups & Pop Flashes | RushB",
        "description": "CS2 flash lineups for every competitive map: pop flashes, self flashes, team flashes and retake flashes, with position, aim point and video guide.",
        "crumb": "Flashes", "crumbs": [("Nades", "lineups/")],
        "h1": 'CS2 <span class="accent">flash</span> lineups',
        "lead": "Pop flashes, self flashes and team flashes that blind the enemy, not your teammates — with the position, aim point and throw type for each one.",
        "screens": [("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-lineup-combo.webp", "RushB app: combo page with the smokes and flash of a B site play"), ("screen-nades-combo.webp", "RushB app: combo grenades on the Mirage radar")],
        "body": grenade_body("flashes"),
        "faq": [
            ("What is a pop flash?", "<p>A flash thrown over or around a wall so it explodes as soon as it appears on the enemy’s screen, leaving no time to turn away.</p>"),
            ("How do I avoid flashing my teammates?", "<p>Call the flash before throwing it, use lineups that pop behind your teammates and agree on who flashes for whom.</p>"),
        ],
    },
    {
        "slug": "lineups/he-grenades/", "nav": "Nades",
        "title": "CS2 HE Grenade Lineups | RushB",
        "description": "CS2 HE grenade lineups: stack damage on defender positions, finish low players and stop rushes. Position, aim point and video for every throw.",
        "crumb": "HE grenades", "crumbs": [("Nades", "lineups/")],
        "h1": 'CS2 <span class="accent">HE grenade</span> lineups',
        "lead": "Damage stacked defenders, finish low players and open a smoke for a moment — HE lineups for the competitive maps.",
        "screens": [("screen-nades-combo.webp", "RushB app: combo grenades on the Mirage radar"), ("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-lineup-combo.webp", "RushB app: combo page with the smokes and flash of a B site play")],
        "body": grenade_body("he-grenades"),
        "faq": [
            ("Is an HE grenade worth buying?", "<p>Yes, when it has a target: common defender positions, low players after a trade or a narrow chokepoint during a rush.</p>"),
            ("Does an HE grenade clear a smoke?", "<p>The explosion opens a hole in a smoke for a short time. Use it to catch players crossing behind the smoke.</p>"),
        ],
    },
    {
        "slug": "lineups/molotovs/", "nav": "Nades",
        "title": "CS2 Molotov & Incendiary Lineups | RushB",
        "description": "CS2 molotov and incendiary lineups: clear corners, stop pushes and deny the defuse with post-plant molotovs. Position, aim point and video for each throw.",
        "crumb": "Molotovs", "crumbs": [("Nades", "lineups/")],
        "h1": 'CS2 <span class="accent">molotov</span> lineups',
        "lead": "Clear close corners, stop pushes and delay the defuse — molotov and incendiary lineups for the competitive maps.",
        "screens": [("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-lineup-single.webp", "RushB app: B site smoke lineup with throw type and screenshot breakdown"), ("screen-nades-combo.webp", "RushB app: combo grenades on the Mirage radar")],
        "body": grenade_body("molotovs"),
        "faq": [
            ("What is the difference between a molotov and an incendiary?", "<p>Terrorists buy the molotov and CTs buy the incendiary grenade. Both cover an area in fire for a few seconds.</p>"),
            ("Can a smoke put out a molotov?", "<p>Yes. A smoke grenade extinguishes the fire, so a post-plant molotov can be countered with a smoke on the bomb.</p>"),
        ],
    },
    {
        "slug": "tactics/", "nav": "Tactics",
        "title": "CS2 Tactics & Executes for Every Map | RushB",
        "description": "100+ CS2 tactics in one app: site takes, fakes, executes and retakes for buy, pistol, eco and force rounds, with roles and video breakdowns for each map.",
        "crumb": "Tactics",
        "h1": 'CS2 <span class="accent">tactics</span> for every round',
        "lead": "Site takes, fakes, executes and retakes for every competitive map — with the round type, the role of each player and the utility they throw.",
        "stats": [('100<span class="accent">+</span>', "tactics"), ("Buy · Pistol · Eco · Force", "round types")],
        "screens": [("screen-tactics-list.webp", "RushB app: tactics for Mirage filtered by buy, pistol, eco and force rounds"), ("screen-triple.webp", "RushB app: triple executes for A site, mid and B site"), ("screen-solo-page.webp", "RushB app: 200 IQ Pistol setup with description and video")],
        "body": tactics_body, "faq": TACTICS_FAQ,
    },
    {
        "slug": "setups/", "nav": "Setups",
        "title": "CS2 Solo & Duo Setups: Anchors and Crossfires | RushB",
        "description": "200+ CS2 setups for solo players, duos and trios: anchor positions, crossfires and coordinated utility for FACEIT and Premier on every competitive map.",
        "crumb": "Setups",
        "h1": 'CS2 <span class="accent">solo &amp; duo</span> setups',
        "lead": "Playing alone or with one friend? Anchor positions, crossfires and coordinated utility made for real FACEIT and Premier matches.",
        "stats": [('200<span class="accent">+</span>', "setups"), ("Solo · Duo · Trio", "for every stack")],
        "screens": [("screen-solo.webp", "RushB app: solo play setups for A site, mid and B site"), ("screen-duo.webp", "RushB app: duo setups for A site, mid and B site"), ("screen-solo-page.webp", "RushB app: 200 IQ Pistol setup with description and video")],
        "body": setups_body, "faq": SETUPS_FAQ,
    },
    {
        "slug": "ai-coach/", "nav": "AI Coach",
        "title": "CS2 AI Coach: Ask About Any Tactic | RushB",
        "description": "Ask the RushB AI coach anything about CS2: tactics, setups, settings, demos and how to climb to FACEIT level 10. Personal advice for your level and role.",
        "crumb": "AI Coach",
        "h1": 'Your <span class="accent">AI coach</span> for CS2',
        "lead": "Ask anything about CS2 and your game — tactics, decisions, settings, demos — and get advice for your level and role.",
        "screens": [("screen-ai-coach.webp", "RushB app: AI coach chat with example questions")],
        "body": ai_body, "faq": AI_FAQ,
    },
    {
        "slug": "binds/", "nav": "Binds",
        "title": "CS2 Binds: Grenade Binds & Console Commands | RushB",
        "description": "CS2 binds that still work in 2026: one key for each grenade, mouse-wheel jump, how to throw nades faster and why the jump-throw bind no longer works.",
        "crumb": "Binds",
        "h1": 'CS2 <span class="accent">binds</span> &amp; grenade binds',
        "lead": "Binds that still work on Valve servers, one key for each grenade and the console basics — plus why you no longer need a jump-throw bind.",
        "screens": [("screen-binds.webp", "RushB app: binds section with copyable commands")],
        "body": binds_body, "faq": BINDS_FAQ,
    },
    {
        "slug": "guides/", "nav": "",
        "title": "CS2 Guides: Nades, Binds & Practice | RushB",
        "description": "Free CS2 guides from the RushB team: how to practice nades, practice commands, grenade binds and smoke lineups for the competitive map pool.",
        "crumb": "Guides",
        "h1": 'CS2 <span class="accent">guides</span>',
        "lead": "Practical guides from the RushB team: how to practise nades, the commands and binds you need, and the lineups worth learning first.",
        "screens": [("screen-lineup-single.webp", "RushB app: B site smoke lineup with throw type and screenshot breakdown"), ("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-tactics-list.webp", "RushB app: tactics for Mirage filtered by buy, pistol, eco and force rounds")],
        "body": guides_body,
    },
    {
        "slug": "guides/cs2-practice-commands/", "nav": "",
        "title": "How to Practice Nades in CS2: Commands & Config | RushB",
        "description": "How to practice nades in CS2: Practice mode, a copy-paste config, commands for infinite nades, rethrow and clearing smokes, and binds that save time.",
        "crumb": "Practice nades", "crumbs": [("Guides", "guides/")],
        "h1": 'How to <span class="accent">practice nades</span> in CS2',
        "lead": "Unlimited grenades, a camera that shows where each nade lands and a key that repeats your last throw — set up in two minutes, offline or with friends.",
        "updated": "2026-11-26", "article": True,
        "screens": [("screen-lineup-single.webp", "RushB app: B site smoke lineup with throw type and screenshot breakdown"), ("screen-nade-filters.webp", "RushB app: nade filters for retakes, insta smokes and one-way smokes"), ("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar")],
        "body": practice_body, "faq": PRACTICE_FAQ,
    },
    {
        "slug": "guides/faceit-level-10/", "nav": "",
        "title": "How to Get FACEIT Level 10 in CS2 (2026) | RushB",
        "description": "How to get FACEIT Level 10 in CS2: the Elo you need, how many matches it takes at your win rate, what Season 10 changes and habits that win more rounds.",
        "crumb": "FACEIT Level 10", "crumbs": [("Guides", "guides/")],
        "h1": 'How to get <span class="accent">FACEIT Level 10</span>',
        "lead": "Level 10 starts at 2,001 Elo. Here is how far you are, how many matches it really takes, and the habits that raise the one number that moves Elo — your win rate.",
        "updated": "2026-11-26", "article": True,
        "screens": [("screen-ai-coach.webp", "RushB app: AI coach chat with example questions"), ("screen-tactics-list.webp", "RushB app: tactics for Mirage filtered by buy, pistol, eco and force rounds"), ("screen-duo.webp", "RushB app: duo setups for A site, mid and B site")],
        "body": level10_body, "faq": LEVEL10_FAQ,
    },
    {
        "slug": "tools/faceit-elo-calculator/", "nav": "",
        "title": "FACEIT Elo Calculator: Matches to Level 10 | RushB",
        "description": "Free FACEIT Elo calculator for CS2: enter your Elo and win rate to see your level, the Elo to the next level and how many matches it takes to reach Level 10.",
        "crumb": "FACEIT Elo calculator",
        "h1": 'FACEIT <span class="accent">Elo calculator</span>',
        "lead": "Enter your Elo and win rate to see your level, the Elo to the next one and about how many matches it takes to reach any level — up to Level 10.",
        "updated": "2026-11-26",
        "aside": calculator_form, "body": calculator_body, "faq": CALCULATOR_FAQ, "scripts": ["elo.js"],
    },
    {
        "slug": "updates/", "nav": "Updates",
        "title": "CS2 Updates & Patch Notes: The Last 50 Updates | RushB",
        "description": "Every recent Counter-Strike 2 update in plain words: map, grenade and gameplay changes, what they mean for your game, and links to Valve’s official patch notes.",
        "crumb": "CS2 updates",
        "h1": 'CS2 <span class="accent">updates</span> &amp; patch notes',
        "lead": "The last 50 Counter-Strike 2 updates from Valve in plain words — what changed and what it means for your game. Newest first, each with a link to the official notes.",
        "updated": "2026-11-26",
        "stats": [("50", "latest updates"), (str(sum(1 for u in UPDATES if "Grenades" in u["tags"])), "touch grenades"), (str(sum(1 for u in UPDATES if "Maps" in u["tags"])), "change maps")],
        "screens": [("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-lineup-single.webp", "RushB app: smoke lineup with throw type and screenshot breakdown"), ("screen-tactics-list.webp", "RushB app: tactics for Mirage filtered by buy, pistol, eco and force rounds")],
        "body": updates_body, "faq": updates_faq(),
    },
    {
        "slug": "faq/", "nav": "",
        "title": "RushB FAQ: Subscription, Features, Support",
        "description": "Answers about RushB: what the app includes, whether it is free, supported devices, how to cancel a subscription and how to contact support.",
        "crumb": "FAQ",
        "h1": 'Questions &amp; <span class="accent">answers</span>',
        "lead": "Everything about RushB: what’s inside, subscriptions, devices and support. Can’t find your answer? Write to support@therushb.com.",
        "screens": [("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-tactics-list.webp", "RushB app: tactics for Mirage filtered by buy, pistol, eco and force rounds"), ("screen-ai-coach.webp", "RushB app: AI coach chat with example questions")],
        "body": faq_body, "faq": FAQ, "faq_title": "Frequently asked questions",
    },
    {
        "slug": "about/", "nav": "",
        "title": "About RushB – CS2 Guide App",
        "description": "RushB is an independent CS2 guide app by Mosaic Dynamics LTD: lineups, tactics, setups, binds and an AI coach that help players climb to FACEIT level 10.",
        "crumb": "About",
        "h1": 'About <span class="accent">RushB</span>',
        "lead": "An independent CS2 companion app that puts lineups, tactics, setups, binds and an AI coach in one place.",
        "screens": [("screen-nades-single.webp", "RushB app: single grenade lineups on the Mirage radar"), ("screen-tactics-list.webp", "RushB app: tactics for Mirage filtered by buy, pistol, eco and force rounds"), ("screen-ai-coach.webp", "RushB app: AI coach chat with example questions")],
        "body": about_body,
    },
]

_i = next(i for i, p in enumerate(PAGES) if p["slug"] == "lineups/molotovs/") + 1
PAGES[_i:_i] = map_pages()
