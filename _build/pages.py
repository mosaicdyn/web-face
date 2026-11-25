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
  body(r)      HTML sections; r is the relative path to the site root
  faq          [(question, answer_html)] -> also output as FAQPage schema
"""

ACTIVE_DUTY = ["Ancient", "Anubis", "Cache", "Dust II", "Inferno", "Mirage", "Nuke"]


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
cl_grenadepreview 1
mp_buy_anywhere 1
mp_buytime 9999
mp_warmup_end
bind n sv_rethrow_last_grenade"""

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
        section(prose(f'''          <h2>Lineups for the competitive map pool</h2>
          <p>Valve’s Active Duty pool is the set of maps used in Premier and at Majors. Since July 2026 it is:</p>
''') + "\n" + chips(ACTIVE_DUTY) + "\n" + prose(f'''          <p style="margin-top:20px">RushB has a database of 2000+ lineups across the competitive maps — from the standard smokes every team uses to pro-level utility. Single nades, combos and several throws from the same spot are all filtered by map and situation.</p>
          <h2>How to practise lineups faster</h2>
          <p>Learn a lineup in a private match before you use it in Premier or on FACEIT. Start an offline game with bots, open the console and paste this practice config:</p>
          {code(PRACTICE_CONFIG)}
          <p>Now you can rebuy grenades anywhere, see where each throw will land and press <code>N</code> to repeat your last grenade without walking back to the spot. More commands are on the <a href="{r}binds/">binds and console commands</a> page.</p>
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
    rows = "".join(
        f"<tr><td><code>{c}</code></td><td>{d}</td></tr>" for c, d in [
            ("sv_cheats 1", "Allows practice commands on your own server. Needed for most commands below."),
            ("sv_infinite_ammo 1", "Infinite ammo and grenades."),
            ("ammo_grenade_limit_total 5", "Carry all grenade types at once."),
            ("sv_grenade_trajectory_prac_pipreview 1", "Shows a preview of where the grenade will land."),
            ("sv_grenade_trajectory_prac_trailtime 8", "Keeps the grenade’s flight path on screen for 8 seconds."),
            ("cl_grenadepreview 1", "Shows the arc while you hold the throw."),
            ("sv_rethrow_last_grenade", "Throws your last grenade again from the same spot (needs sv_cheats 1)."),
            ("noclip", "Fly through the map to look at a smoke from the enemy side."),
            ("mp_buy_anywhere 1", "Buy anywhere on the map."),
            ("mp_buytime 9999", "Buy time never runs out."),
            ("mp_warmup_end", "Ends the warmup."),
            ("bot_kick", "Removes all bots."),
            ("mp_restartgame 1", "Restarts the match after 1 second."),
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
          <h2>Practice config for lineups</h2>
          <p>Paste this into the console in an offline match with bots to practise grenades:</p>
          {code(PRACTICE_CONFIG)}
          <h2>Useful practice commands</h2>
          <p>These commands only work on your own server or in an offline match, not in Premier or on FACEIT.</p>
          <table class="cmd-table"><thead><tr><th>Command</th><th>What it does</th></tr></thead><tbody>{rows}</tbody></table>
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
    ("Where do I save binds so I don’t type them every time?",
     "<p>Put them in an autoexec config file in your CS2 cfg folder and add <code>+exec autoexec</code> to the game’s launch options in Steam.</p>"),
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
        "title": "CS2 Lineups: Smokes, Flashes, HE & Molotovs | RushB",
        "description": "2000+ CS2 grenade lineups in one app: smokes, flashes, HE grenades and molotovs for every competitive map, with position, aim point and video.",
        "crumb": "Nades",
        "h1": 'CS2 <span class="accent">grenade lineups</span> for every map',
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
        "title": "CS2 Binds & Console Commands | RushB",
        "description": "CS2 binds and console commands that still work in 2026: mouse-wheel jump, practice config for lineups, rethrow and grenade trajectory commands.",
        "crumb": "Binds",
        "h1": 'CS2 <span class="accent">binds</span> &amp; console commands',
        "lead": "Binds that still work on Valve servers, a ready practice config for lineups and the console commands you actually need.",
        "screens": [("screen-binds.webp", "RushB app: binds section with copyable commands")],
        "body": binds_body, "faq": BINDS_FAQ,
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
