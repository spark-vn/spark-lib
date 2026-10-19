#!/usr/bin/env python3
"""Doc content.json roi sinh ra index.html (mot file, chi tai font tu Google Fonts).

Ba nhom layout:
  split  1 the lon "doc truoc" + cac the con      (chi nhom dau)
  grid   luoi the doc dong nhat, co the kem tab loc (moi nhom giua)
  dark   dai mau dam: kenh ho tro + danh sach doc  (chi nhom cuoi)
"""
import base64
import json
import html
import pathlib
import urllib.parse

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
meta = data["meta"]

for _g in data["groups"]:
    if _g["template"] == "split" or _g.get("keep_order"):
        continue
    for _docs in ([sg["docs"] for sg in _g["subgroups"]] if "subgroups" in _g else [_g.get("docs", [])]):
        _docs.sort(key=lambda d: (bool(d.get("highlight")), d.get("created", "")), reverse=True)
DOC_BASE = meta["doc_base"]

FAVICON = "data:image/png;base64," + base64.b64encode((HERE / "assets" / "favicon.png").read_bytes()).decode()


def _img64(name):
    return "data:image/png;base64," + base64.b64encode((HERE / "assets" / name).read_bytes()).decode()


def _lark_icon(name):
    raw = (HERE / "assets" / "lark-icons" / f"{name}.svg").read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(raw).decode()


def esc(s):
    return html.escape(str(s), quote=True)


def docs_of(group):
    if "subgroups" in group:
        return [d for sg in group["subgroups"] for d in sg["docs"]]
    return group.get("docs", [])


total_docs = sum(len(docs_of(g)) for g in data["groups"])

LEVEL = {"Cơ bản": "lv1", "Trung cấp": "lv2", "Nâng cao": "lv3"}

KIND_PATH = {"docx": "/docx/", "base": "/base/", "file": "/file/", "wiki": "/wiki/", "slides": "/slides/"}
KIND_LABEL = {"wiki": "Wiki", "docx": "Doc", "base": "Base", "file": "File", "slides": "Slides", "pdf": "PDF", "web": "Web", "folder": "Folder"}
KIND_CLS = {"wiki": "kd-wiki", "docx": "kd-doc", "base": "kd-base", "file": "kd-file", "slides": "kd-slides", "pdf": "kd-pdf", "web": "kd-web", "folder": "kd-file"}


def doc_url(doc):
    if "url" in doc:
        return doc["url"]
    kind = doc.get("kind", "docx")
    return DOC_BASE + KIND_PATH.get(kind, "/docx/") + doc["token"]


def attrs(doc):
    return (
        f'href="{esc(doc_url(doc))}" target="_blank" rel="noopener" '
        f'data-topics="{esc(" ".join(doc.get("topics", [])))}" '
        f'data-title="{esc(doc["title"].lower())}" '
        f'data-desc="{esc(doc["desc"].lower())}"'
    )


def meta_row(doc):
    bits = [
        f'<span class="badge {LEVEL.get(doc["level"], "lv1")}">{esc(doc["level"])}</span>',
        f'<span class="badge lang">{esc(doc["lang"])}</span>',
    ]
    if not doc["shared"]:
        bits.append('<span class="badge lock">Cần quyền</span>')
    return "".join(bits)


def card(d, sg=None):
    sgattr = f' data-sg="{esc(sg)}"' if sg else ""
    hl = " card-hl" if d.get("highlight") else ""
    hl_badge = '<span class="hl-badge">Nổi bật</span>' if d.get("highlight") else ""
    return f"""          <a class="card item{hl}"{sgattr} {attrs(d)}>
            {hl_badge}
            <div class="badges">{meta_row(d)}</div>
            <h3>{esc(d['title'])}</h3>
            <p>{esc(d['desc'])}</p>
            <div class="card-foot"><span class="time"><svg class="ico-clock" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 4v4.5l3 1.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>{d['minutes']} phút</span><span class="go">Mở →</span></div>
          </a>
"""


VIS_DECK = """<div class="vis vis-deck" aria-hidden="true">
              <div class="deck-s s3"></div><div class="deck-s s2"></div>
              <div class="deck-s s1">
                <div class="ds-top"><i></i><i></i><i></i></div>
                <div class="ds-title"></div><div class="ds-sub"></div>
                <div class="ds-row"><span class="ds-bars"><b style="height:38%"></b><b style="height:62%"></b><b style="height:48%"></b><b style="height:84%"></b><b style="height:70%"></b></span><span class="ds-lines"><em></em><em></em><em></em></span></div>
              </div>
            </div>"""

_NODES = [
    ("Nhắn tin", "lark-messenger-icon-01", 72, 40),
    ("Họp video", "lark-meeting-icon", 72, 100),
    ("Tài liệu", "lark-docs-icon-01", 72, 160),
    ("Base", "lark-bitable-icon-01", 448, 40),
    ("Phê duyệt", "lark-approval-icon-01", 448, 100),
    ("Email", "lark-email-icon-01", 448, 160),
]
_NW = 112


def _vis_nodes():
    bird = _img64("lark-bird.png")
    paths, nodes = [], []
    for name, icon, x, y in _NODES:
        left = x < 260
        sx = x + _NW / 2 if left else x - _NW / 2
        ex = 226 if left else 294
        mx = (sx + ex) / 2
        paths.append(f'<path d="M{sx} {y} C{mx} {y}, {mx} 100, {ex} 100"/>')
        tx = x - _NW / 2
        nodes.append(
            f'<g transform="translate({tx} {y - 16})"><rect class="nd" width="{_NW}" height="32" rx="10"/>'
            f'<image href="{_lark_icon(icon)}" x="6" y="5" width="22" height="22"/>'
            f'<text x="{32}" y="20.5">{name}</text>'
            f'<circle class="port" cx="{_NW if left else 0}" cy="16" r="3"/></g>'
        )
    m_paths, m_nodes = [], []
    for k, (name, icon, x, y) in enumerate(_NODES):
        left = x < 260
        cy = 40 + (k % 3) * 65
        cx = 40 if left else 280
        sx = cx + 22 if left else cx - 22
        ex = 124 if left else 196
        mx = (sx + ex) / 2
        m_paths.append(f'<path d="M{sx} {cy} C{mx} {cy}, {mx} 105, {ex} 105"/>')
        m_nodes.append(f'<rect class="nd" x="{cx - 22}" y="{cy - 22}" width="44" height="44" rx="12"/>'
                       f'<image href="{_lark_icon(icon)}" x="{cx - 13}" y="{cy - 13}" width="26" height="26"/>')
    mobile_svg = f"""<svg class="flow-m" viewBox="0 0 320 210" preserveAspectRatio="xMidYMid meet">
                <g class="flow-lines">{''.join(m_paths)}</g>
                <g class="flow-nodes">{''.join(m_nodes)}</g>
                <g class="flow-hub">
                  <circle class="hub-ring" cx="160" cy="105" r="46" style="transform-origin:160px 105px"/>
                  <circle class="hub-disc" cx="160" cy="105" r="36"/>
                  <image href="{bird}" x="136" y="87" width="48" height="38"/>
                </g>
              </svg>"""
    return f"""<div class="vis vis-flow" aria-hidden="true">
              {mobile_svg}
              <svg class="flow-d" viewBox="0 0 520 200" preserveAspectRatio="xMidYMid meet">
                <g class="flow-lines">{''.join(paths)}</g>
                <g class="flow-nodes">{''.join(nodes)}</g>
                <g class="flow-hub">
                  <circle class="hub-ring" cx="260" cy="100" r="44"/>
                  <circle class="hub-disc" cx="260" cy="100" r="34"/>
                  <image href="{bird}" x="238" y="83" width="44" height="35"/>
                </g>
              </svg>
            </div>"""




def showcase(d):
    vis = VIS_DECK if d.get("kind") == "slides" else _vis_nodes()
    cta = "Xem slide" if d.get("kind") == "slides" else "Đọc tài liệu"
    return f"""        <a class="show item" {attrs(d)}>
          {vis}
          <div class="show-body">
            <div class="badges">{meta_row(d)}<span class="time"><svg class="ico-clock" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 4v4.5l3 1.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>{d['minutes']} phút</span></div>
            <h3>{esc(d['title'])}</h3>
            <p>{esc(d['desc'])}</p>
            <span class="show-cta">{cta} <b>→</b></span>
          </div>
        </a>
"""


def t_split(g):
    docs = g.get("docs", [])
    if not docs:
        return ""
    solo = " split-solo" if len(docs) == 1 else ""
    return f'      <div class="split{solo}">\n' + "".join(showcase(d) for d in docs) + "      </div>\n"


def t_grid(g):
    if "subgroups" in g:
        tabs = '<button type="button" class="tab on" data-tab="all">Tất cả</button>'
        cards = ""
        for i, sg in enumerate(g["subgroups"]):
            key = f"sg{i}"
            tabs += (
                f'<button type="button" class="tab" data-tab="{key}">'
                f'{esc(sg["name"])}</button>'
            )
            cards += "".join(card(d, sg=key) for d in sg["docs"])
        return f'      <div class="tabs">{tabs}</div>\n      <div class="grid">\n{cards}      </div>\n'
    docs = g.get("docs", [])
    body = "".join(card(d) for d in docs)
    few = " few" if len(docs) < 4 else ""
    return f'      <div class="grid{few}">\n{body}      </div>\n'


def t_dark(g):
    def chan(i, c):
        body = f"""
            <span class="chan-n">{i}</span>
            <b>{esc(c['name'])}</b><span>{esc(c['desc'])}</span>"""
        if c.get("url"):
            ext = "" if c["url"].startswith(("tel:", "mailto:")) else ' target="_blank" rel="noopener"'
            return f"""          <a class="chan chan-link" href="{esc(c['url'])}"{ext}>{body}
            <span class="chan-go">{esc(c.get('cta', 'Mở'))} →</span>
          </a>
"""
        return f"""          <div class="chan">{body}
          </div>
"""

    chans = "".join(chan(i, c) for i, c in enumerate(g.get("channels", []), 1))
    docs = g.get("docs", [])
    links = ""
    if docs:
        links_body = "".join(
            f"""          <a class="dlink item" {attrs(d)}>
            <span class="dlink-t">{esc(d['title'])}</span>
            <span class="dlink-d">{esc(d['desc'])}</span>
            <span class="arrow">→</span>
          </a>
"""
            for d in docs
        )
        links = f"""        <div class="dlinks">
          <h3 class="dsub">Tài liệu kèm theo</h3>
{links_body}        </div>
"""
    return f"""      <div class="dark-grid{' dark-full' if not docs else ''}">
        <div class="chans">
{chans}        </div>
{links}      </div>
"""


def more_link(g):
    m = g.get("more")
    if not m:
        return ""
    return (f'      <div class="sec-more"><a href="{esc(m["url"])}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2.5h8.5A1.5 1.5 0 0 1 21 10v8.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/></svg>'
            f'{esc(m["label"])} <b>→</b></a></div>\n')


TEMPLATES = {"split": t_split, "grid": t_grid, "dark": t_dark}

navs, sections = [], []
for gi, g in enumerate(data["groups"], 1):
    navs.append(
        f'<a class="nav-item" href="#{esc(g["id"])}" data-nav="{esc(g["id"])}">'
        f'{esc(g.get("nav", g["name"]))}</a>'
    )
    cls = " ".join(
        filter(
            None,
            [
                "section",
                "dark" if g["template"] == "dark" else "",
            ],
        )
    )
    sections.append(
        f"""  <section class="{cls}" id="{esc(g['id'])}">
    <div class="wrap">
      <div class="sec-head">
        <span class="sec-num">Chuyên mục {gi:02d}</span>
        <h2>{esc(g['name'])}</h2>
        <p class="lead">{esc(g['lead'])}</p>
      </div>
{TEMPLATES[g['template']](g)}{more_link(g)}      <p class="sec-empty" style="display:none;">Không có tài liệu phù hợp trong nhóm này.</p>
    </div>
  </section>
"""
    )

all_docs = [d for g in data["groups"] for d in docs_of(g)]
topic_tabs = ""



SPARK_LOGO = f'<img class="spark-logo" src="{_img64("spark-logo.png")}" alt="Spark">'
SPARK_LOGO_WHITE = f'<img class="spark-logo" src="{_img64("spark-logo-white.png")}" alt="Spark">'
LARK_PARTNER = f'<img class="lark-partner" src="{_img64("lark-partner-dark.png")}" alt="Lark Partner">'


BOLT = """<svg class="bolt" viewBox="0 0 240 340" aria-hidden="true">
  <defs>
    <linearGradient id="bEdge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#c9d6ff"/><stop offset=".35" stop-color="#3d6bff"/>
      <stop offset=".7" stop-color="#0F47F5"/><stop offset="1" stop-color="#8b5cf6"/>
    </linearGradient>
    <linearGradient id="bFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a2a6e" stop-opacity=".95"/><stop offset="1" stop-color="#0b0b2a" stop-opacity=".9"/>
    </linearGradient>
    <linearGradient id="bCore" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#a9bcff"/><stop offset="1" stop-color="#7a5cff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="bClip"><path d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z"/></clipPath>
    <filter id="bGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
    <filter id="bSoft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
    <filter id="bTail" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
  </defs>
  <path class="bolt-aura" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="#2f5bff" filter="url(#bGlow)"/>
  <path d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="url(#bFill)" stroke="url(#bEdge)" stroke-width="3" stroke-linejoin="round"/>
  <g clip-path="url(#bClip)" class="arcs" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path class="arc a1" d="M162 20 L146 52 L156 57 L128 104 L139 108 L104 170"/>
    <path class="arc a2" d="M118 196 L110 228 L121 232 L100 276 L110 281 L90 322"/>
    <path class="arc a3" d="M190 132 L168 150 L176 158 L146 184 L154 190 L126 214"/>
  </g>
  <path class="bolt-core" d="M162 26 L80 172 H128 L104 290 L178 148" fill="none" stroke="url(#bCore)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#bSoft)"/>
  <path d="M162 26 L80 172 H128 L104 290 L178 148" fill="none" stroke="#fff" stroke-opacity=".85" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
  <g class="comet">
    <path class="c-tail" pathLength="100" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="none" stroke="#5b86ff" stroke-width="9" stroke-linejoin="round" filter="url(#bTail)"/>
    <path class="c-body" pathLength="100" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="none" stroke="#bcd0ff" stroke-width="4" stroke-linejoin="round" filter="url(#bSoft)"/>
    <path class="c-head" pathLength="100" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <g class="comet c2">
    <path class="c-tail" pathLength="100" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="none" stroke="#8b5cf6" stroke-width="8" stroke-linejoin="round" filter="url(#bTail)"/>
    <path class="c-head" pathLength="100" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="none" stroke="#e9dcff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <path class="bolt-flash" d="M150 6 L40 190 H112 L78 334 L206 128 H134 L184 6 Z" fill="#ffffff"/>
</svg>"""

HTML = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0b0916">
<meta name="description" content="{esc(meta['subtitle'])}">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['subtitle'])}">
<meta property="og:type" content="website">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<title>{esc(meta['title'])}</title>
<style>
:root {{
  --bg: #0b0916;
  --bg-2: #100d1d;
  --card: #15121f;
  --card-2: #1b1729;
  --line: rgba(255,255,255,.07);
  --line-2: rgba(255,255,255,.13);
  --text: #f4f3f8;
  --dim: #b4b1bf;
  --mute: #8a8698;
  --brand: #0F47F5;
  --brand-2: #3d6bff;
  --brand-3: #9db4ff;
  --violet: #8b5cf6;
  --r-sm: 8px;
  --r-md: 16px;
  --r-lg: 22px;
  --r-full: 999px;
  --font: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; }}
html {{ background: var(--bg); overflow-x: clip; }}
body {{
  background: var(--bg); color: var(--text); font-family: var(--font);
  font-size: 15px; line-height: 1.6; -webkit-font-smoothing: antialiased; overflow-x: hidden;
}}
a {{ color: inherit; text-decoration: none; }}
h1, h2, h3 {{ text-wrap: balance; }}
button {{ font-family: inherit; }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding: 0 24px; }}
:focus-visible {{ outline: 2px solid var(--brand-2); outline-offset: 3px; border-radius: var(--r-sm); }}
::selection {{ background: rgba(61,107,255,.45); color: #fff; }}

/* ============ floating header ============ */
header {{ position: sticky; top: 0; z-index: 30; padding: 12px 0 0; }}
.head-in {{
  display: flex; align-items: center; gap: 18px; height: 56px; padding: 0 10px 0 18px;
  background: rgba(22,19,36,.72); border: 1px solid var(--line-2); border-radius: 14px;
  backdrop-filter: saturate(160%) blur(16px); -webkit-backdrop-filter: saturate(160%) blur(16px);
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
}}
.logo {{ display: flex; align-items: center; flex-shrink: 0; }}
.spark-logo {{ height: 26px; width: auto; display: block; }}
.logo-label {{
  margin-left: 12px; padding-left: 12px; border-left: 1px solid var(--line-2);
  font-size: 13px; font-weight: 500; color: var(--dim); white-space: nowrap;
}}
nav {{
  display: flex; gap: 4px; overflow-x: auto; flex: 1; scrollbar-width: none; justify-content: flex-start;
  mask-image: linear-gradient(90deg, transparent 0, #000 16px, #000 calc(100% - 24px), transparent 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 16px, #000 calc(100% - 24px), transparent 100%);
  padding: 0 12px;
}}
nav::-webkit-scrollbar {{ display: none; }}
nav > .nav-item:first-child {{ margin-left: auto; }}
nav > .nav-item:last-child {{ margin-right: auto; }}
.nav-item {{
  font-size: 14px; font-weight: 500; color: var(--dim); white-space: nowrap;
  padding: 8px 12px; border-radius: 9px; transition: color .2s, background .2s;
}}
@media (max-width: 1180px) {{ .nav-item {{ font-size: 13px; padding: 7px 9px; }} }}
.nav-item:hover {{ color: #fff; background: rgba(255,255,255,.05); }}
.nav-item.on {{ color: #fff; background: rgba(255,255,255,.08); }}
.cta {{
  flex-shrink: 0; display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 16px; border-radius: 10px; font-size: 13.5px; font-weight: 600; color: #fff;
  background: linear-gradient(180deg, #3d6bff, #0F47F5); box-shadow: 0 6px 18px rgba(15,71,245,.45), inset 0 1px 0 rgba(255,255,255,.25);
  transition: filter .2s, transform .2s;
}}
.cta:hover {{ filter: brightness(1.12); transform: translateY(-1px); }}

/* hero search */
.search-row {{ margin-top: 20px; max-width: 460px; }}
.search-box {{ position: relative; }}
.search-box svg.ico-search {{
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  width: 16px; height: 16px; color: #8fb4ff; pointer-events: none;
}}
.search-box input {{
  width: 100%; height: 42px; padding: 0 40px 0 40px; font: inherit; font-size: 14px; color: var(--text);
  background: rgba(255,255,255,.06); border: 1px solid rgba(125,155,255,.35); border-radius: 8px; outline: none;
  transition: border-color .2s, box-shadow .2s, background .2s;
}}
.search-box input::placeholder {{ color: var(--mute); }}
.search-box input:focus {{ border-color: rgba(125,155,255,.8); background: rgba(255,255,255,.09); box-shadow: 0 0 0 3px rgba(61,107,255,.22); }}
.search-box input::-webkit-search-cancel-button {{ display: none; }}
.search-clear {{
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  width: 26px; height: 26px; border: none; background: rgba(255,255,255,.08); border-radius: 50%;
  color: var(--dim); font-size: 16px; line-height: 26px; text-align: center; cursor: pointer; display: none; padding: 0;
}}
.search-clear:hover {{ background: rgba(255,255,255,.16); color: #fff; }}
.search-clear.on {{ display: block; }}

/* ============ hero ============ */
.hero {{ position: relative; padding: 70px 0 40px; overflow-x: clip; }}
.hero::before {{
  content: ""; position: absolute; left: 50%; bottom: -160px; width: 1200px; height: 420px; transform: translateX(-30%);
  background: radial-gradient(closest-side, rgba(61,107,255,.30), rgba(139,92,246,.12) 55%, transparent 75%);
  pointer-events: none;
}}
.hero-grid {{ position: relative; display: grid; grid-template-columns: 1.5fr .5fr; gap: 24px; align-items: center; min-height: 520px; }}
.hero-partner {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
.hero-partner .lark-partner {{ height: 40px; width: auto; display: block; padding-right: 16px; border-right: 1px solid var(--line-2); }}
.ft-logos {{ display: flex; align-items: center; gap: 16px; }}
.ft-logos .lark-partner {{ height: 36px; width: auto; display: block; }}
.ft-logos .spark-logo {{ height: 30px; }}
.ft-x {{ color: var(--dim); font-size: 20px; font-weight: 300; line-height: 1; opacity: .7; }}
.hero-kicker {{
  display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; color: var(--dim);
  padding: 6px 14px 6px 8px; border: 1px solid var(--line-2); border-radius: var(--r-full); background: rgba(255,255,255,.03);
}}
.hero-kicker i {{
  font-style: normal; font-size: 11px; font-weight: 700; color: #fff; padding: 2px 8px; border-radius: var(--r-full);
  background: linear-gradient(90deg, #0F47F5, #8b5cf6);
}}
@media (min-width: 1200px) {{ .hero h1 .h1-line {{ white-space: nowrap; }} }}
.hero h1 {{ margin-top: 22px; font-size: 50px; line-height: 1.08; letter-spacing: -.035em; font-weight: 500; }}
.hero h1 .dim {{ color: var(--mute); }}
.hero-sub {{ margin-top: 20px; font-size: 17px; line-height: 1.65; color: var(--dim); max-width: 58ch; font-weight: 300; text-wrap: pretty; }}

.hero-actions {{ margin-top: 26px; display: flex; gap: 10px; flex-wrap: wrap; }}
.hbtn {{
  display: inline-flex; align-items: center; justify-content: center; gap: 8px; height: 40px; padding: 0 18px; border-radius: 8px;
  font-size: 14.5px; font-weight: 400; color: #fff; transition: filter .2s, transform .2s, background .2s;
}}
.hbtn-primary {{ background: linear-gradient(90deg, #3d6bff, #0F47F5 55%, #5b3cf0); }}
.hbtn-primary:hover {{ filter: brightness(1.12); transform: translateY(-1px); }}
.hbtn-ghost {{ background: #26232f; border: 1px solid rgba(255,255,255,.06); }}
.hbtn-ghost:hover {{ background: #312d3c; transform: translateY(-1px); }}
.hero-featured {{
  margin-top: 14px; display: inline-flex; align-items: center; gap: 10px; max-width: 100%;
  padding: 5px 14px 5px 5px; border-radius: var(--r-full);
  background: linear-gradient(90deg, rgba(61,107,255,.18), rgba(255,255,255,.03) 60%);
  border: 1px solid rgba(110,145,255,.4); transition: border-color .2s, background .2s;
}}
.hero-featured:hover {{ border-color: rgba(140,170,255,.75); background: linear-gradient(90deg, rgba(61,107,255,.28), rgba(255,255,255,.05) 60%); }}
.hf-tag {{
  flex-shrink: 0; font-size: 11.5px; font-weight: 700; letter-spacing: .04em; color: #fff;
  padding: 4px 10px; border-radius: var(--r-full); background: linear-gradient(90deg, #45caff, #3370ff);
}}
.hf-title {{ font-size: 13.5px; font-weight: 500; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.hf-go {{ flex-shrink: 0; font-size: 13px; font-weight: 600; color: #8fb4ff; }}
.sec-more {{ margin-top: 22px; text-align: center; }}
.sec-more a {{
  display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px; border-radius: 10px;
  font-size: 14px; font-weight: 500; color: var(--text);
  background: rgba(255,255,255,.04); border: 1px solid var(--line-2); transition: background .2s, border-color .2s;
}}
.sec-more a:hover {{ background: rgba(255,255,255,.08); border-color: rgba(125,155,255,.5); }}
.sec-more svg {{ color: var(--brand-3); }}
.sec-more b {{ color: var(--brand-3); }}
.search-status {{ display: flex; gap: 12px; align-items: center; margin-top: 12px; }}
.search-status:not(:has(.on)) {{ display: none; }}
.search-count {{ font-size: 13.5px; color: var(--dim); white-space: nowrap; display: none; }}
.search-count.on {{ display: inline; }}
.filter-reset {{
  display: none; align-items: center; gap: 6px; padding: 6px 12px; font-size: 13px; font-weight: 500;
  color: var(--text); background: rgba(255,255,255,.06); border: 1px solid var(--line-2);
  border-radius: var(--r-full); cursor: pointer; white-space: nowrap; -webkit-appearance: none; appearance: none;
}}
.filter-reset:hover {{ background: rgba(255,255,255,.12); }}
.filter-reset.on {{ display: inline-flex; }}

.hero-art {{ position: relative; height: 520px; display: flex; align-items: center; justify-content: center; }}
.hero-art::after {{
  content: ""; position: absolute; left: 50%; bottom: 10px; width: 360px; height: 70px; transform: translateX(-50%);
  background: radial-gradient(closest-side, rgba(120,150,255,.55), rgba(139,92,246,.18) 60%, transparent);
  filter: blur(6px);
}}
.hero-art::after {{ animation: floor 4s ease-in-out infinite; }}
@keyframes floor {{ 0%, 100% {{ opacity: .75; transform: translateX(-50%) scaleX(.92); }} 50% {{ opacity: 1; transform: translateX(-50%) scaleX(1.06); }} }}
.bolt {{
  position: relative; z-index: 1; height: 470px; width: auto;
  filter: drop-shadow(0 0 30px rgba(61,107,255,.4));
  transform: perspective(900px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  transition: transform .35s cubic-bezier(.2,.8,.2,1);
  will-change: transform;
}}
.hero-art.tilt .bolt {{ transition: transform .08s linear; }}
.bolt-aura {{ opacity: .7; animation: breathe 4s ease-in-out infinite; transform-origin: 120px 170px; }}
@keyframes breathe {{ 0%, 100% {{ opacity: .5; transform: scale(.97); }} 50% {{ opacity: .9; transform: scale(1.04); }} }}
.bolt-core {{ animation: flicker 3s ease-in-out infinite; }}
@keyframes flicker {{ 0%,100% {{ opacity: .8; }} 45% {{ opacity: .45; }} 50% {{ opacity: .95; }} 55% {{ opacity: .55; }} }}
.comet path {{ animation: orbit 3.6s linear infinite; }}
.comet .c-head {{ stroke-dasharray: 2 98; }}
.comet .c-body {{ stroke-dasharray: 7 93; stroke-dashoffset: 5; animation-name: orbit5; }}
.comet .c-tail {{ stroke-dasharray: 16 84; stroke-dashoffset: 14; animation-name: orbit14; opacity: .9; }}
.comet.c2 path {{ animation-delay: -1.8s; }}
.comet.c2 {{ opacity: .75; }}
.hero-art.tilt .comet path {{ animation-duration: 1.8s; }}
@keyframes orbit {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: -100; }} }}
@keyframes orbit5 {{ from {{ stroke-dashoffset: 5; }} to {{ stroke-dashoffset: -95; }} }}
@keyframes orbit14 {{ from {{ stroke-dashoffset: 14; }} to {{ stroke-dashoffset: -86; }} }}
.arc {{ stroke: #e8f2ff; stroke-width: 1.3; opacity: 0; filter: drop-shadow(0 0 3px #8fb4ff) drop-shadow(0 0 8px #3d6bff); }}
.arc.a1 {{ animation: zap 3.4s linear infinite; }}
.arc.a2 {{ animation: zap 4.1s linear infinite 1.1s; }}
.arc.a3 {{ animation: zap 4.9s linear infinite 2.2s; }}
@keyframes zap {{ 0%, 100% {{ opacity: 0; }} 2% {{ opacity: .9; }} 4% {{ opacity: .1; }} 6% {{ opacity: .8; }} 9% {{ opacity: 0; }} }}
.bolt-flash {{ opacity: 0; pointer-events: none; }}
.hero-art.strike .bolt-flash {{ animation: flash .7s ease-out; }}
.hero-art.strike .bolt {{ animation: jolt .45s ease-out; }}
.hero-art.strike .arc {{ animation: zap .7s linear 1; }}
@keyframes flash {{ 0% {{ opacity: 0; }} 8% {{ opacity: .85; }} 20% {{ opacity: .15; }} 30% {{ opacity: .6; }} 100% {{ opacity: 0; }} }}
@keyframes jolt {{
  0% {{ filter: drop-shadow(0 0 30px rgba(61,107,255,.4)) brightness(1); }}
  15% {{ filter: drop-shadow(0 0 80px rgba(170,195,255,1)) brightness(1.6); }}
  100% {{ filter: drop-shadow(0 0 30px rgba(61,107,255,.4)) brightness(1); }}
}}
.ring {{
  position: absolute; z-index: 0; left: 50%; bottom: 22px; width: 300px; height: 60px; margin-left: -150px;
  border-radius: 50%; border: 2px solid rgba(160,185,255,.9); box-shadow: 0 0 24px rgba(91,134,255,.8), inset 0 0 18px rgba(91,134,255,.6);
  opacity: 0; transform: scale(.2); pointer-events: none;
}}
.hero-art.strike .ring {{ animation: ripple 1.3s cubic-bezier(.15,.7,.3,1) forwards; }}
.hero-art.strike .ring.r2 {{ animation-delay: .15s; }}
.hero-art.strike .ring.r3 {{ animation-delay: .3s; border-color: rgba(167,139,250,.8); }}
@keyframes ripple {{ 0% {{ opacity: .95; transform: scale(.15); }} 100% {{ opacity: 0; transform: scale(1.7); }} }}
.sparks {{ position: absolute; z-index: 2; left: 50%; bottom: 40px; width: 0; height: 0; pointer-events: none; }}
.spk {{
  position: absolute; left: 0; top: 0; width: 3px; height: 26px; margin: -13px 0 0 -1.5px; border-radius: 3px;
  background: linear-gradient(180deg, #fff 0%, #bcd0ff 40%, rgba(140,170,255,0)); box-shadow: 0 0 12px 2px rgba(160,190,255,.95);
  opacity: 0; transform: rotate(calc(var(--a) + 90deg)) translateY(0);
}}
.hero-art.strike .spk {{ animation: burst var(--t) cubic-bezier(.1,.7,.3,1) forwards; }}
@keyframes burst {{
  0% {{ opacity: 1; transform: rotate(calc(var(--a) + 90deg)) translateY(0) scaleY(1.4); }}
  100% {{ opacity: 0; transform: rotate(calc(var(--a) + 90deg)) translateY(calc(var(--d) * -1.5)) scaleY(.3); }}
}}

/* ============ stats strip ============ */
.stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 18px; }}
.stat {{
  position: relative; overflow: hidden; display: flex; gap: 16px; align-items: center; padding: 20px 22px;
  border-radius: 14px; border: 1px solid rgba(255,255,255,.09);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06);
  transition: transform .25s, border-color .25s, box-shadow .25s;
}}
.st-lark {{ background: linear-gradient(100deg, rgba(0,186,170,.16) 0%, rgba(51,112,255,.10) 45%, rgba(255,255,255,.025) 100%), #13111f; }}
.st-docs {{ background: linear-gradient(100deg, rgba(61,107,255,.22) 0%, rgba(110,80,240,.10) 50%, rgba(255,255,255,.025) 100%), #13111f; }}
.st-academy {{ background: linear-gradient(100deg, rgba(139,92,246,.24) 0%, rgba(219,39,119,.10) 55%, rgba(249,120,2,.08) 100%), #13111f; }}
.stat:hover {{ transform: translateY(-2px); border-color: rgba(255,255,255,.18); box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 18px 40px -22px rgba(61,107,255,.6); }}
.stat-ico {{
  flex-shrink: 0; width: 50px; height: 50px; border-radius: 12px; display: grid; place-items: center;
  background: linear-gradient(160deg, #2b2838, #17151f);
  border: 1px solid rgba(255,255,255,.12);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.12), 0 8px 18px rgba(0,0,0,.45);
}}
.stat-ico img {{ width: 30px; height: auto; display: block; }}
.spark-grad {{
  display: block; width: 24px; height: 28px;
  background: linear-gradient(160deg, #45caff 0%, #3370ff 35%, #8b5cf6 70%, #f472b6 100%);
  -webkit-mask-size: contain; mask-size: contain; -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
  -webkit-mask-position: center; mask-position: center;
  filter: drop-shadow(0 0 6px rgba(120,140,255,.6));
}}
.stat p {{ font-size: 15.5px; color: var(--dim); line-height: 1.5; font-weight: 300; }}
.stat b {{ color: #fff; font-weight: 600; }}

/* ============ sections ============ */
.section {{ position: relative; padding: 96px 0 24px; scroll-margin-top: 76px; overflow-x: clip; }}
.section:nth-of-type(odd)::before {{
  content: ""; position: absolute; top: 40px; left: 50%; width: 900px; height: 360px; transform: translateX(-50%);
  background: radial-gradient(closest-side, rgba(61,107,255,.10), transparent 70%); pointer-events: none;
}}
.section > .wrap {{ position: relative; }}
.sec-head {{ text-align: center; max-width: 760px; margin: 0 auto 44px; }}
.sec-num {{ font-size: 12.5px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--brand-3); }}
.sec-head h2 {{ margin-top: 10px; font-size: 42px; line-height: 1.15; letter-spacing: -.03em; font-weight: 500; }}
.lead {{ margin-top: 12px; font-size: 15.5px; color: var(--mute); font-weight: 300; }}
.sec-empty {{ padding: 28px 0; text-align: center; color: var(--mute); font-size: 14px; }}

/* badges */
.badges {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.badge {{
  font-size: 10.5px; font-weight: 600; padding: 3px 8px; border-radius: 6px; white-space: nowrap; letter-spacing: .02em;
  background: rgba(255,255,255,.06); color: var(--dim);
}}
.kind {{ text-transform: uppercase; letter-spacing: .07em; }}
.kd-wiki {{ background: rgba(16,185,129,.13); color: #6ee7b7; }}
.kd-doc {{ background: rgba(61,107,255,.18); color: var(--brand-3); }}
.kd-base {{ background: rgba(245,158,11,.14); color: #fcc96a; }}
.kd-file {{ background: rgba(139,92,246,.18); color: #c9b2ff; }}
.kd-slides {{ background: rgba(244,114,182,.16); color: #f9a8d4; }}
.kd-pdf {{ background: rgba(248,113,113,.16); color: #fca5a5; }}
.kd-web {{ background: rgba(56,189,248,.15); color: #7dd3fc; }}
.lv1 {{ background: rgba(16,185,129,.14); color: #6ee7b7; }}
.lv2 {{ background: rgba(61,107,255,.18); color: #9db4ff; }}
.lv3 {{ background: rgba(245,158,11,.16); color: #fcc96a; }}
.lock {{ background: rgba(248,113,113,.15); color: #fca5a5; }}
.time {{ font-size: 12.5px; color: var(--mute); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px; }}
.ico-clock {{ width: 13px; height: 13px; flex-shrink: 0; }}

/* ============ split / showcase ============ */
.split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.split-solo {{ grid-template-columns: 1fr; }}
.split-solo .show {{ flex-direction: row; min-height: 300px; }}
.split-solo .vis {{ flex: 0 0 52%; height: auto; border-bottom: none; border-right: 1px solid var(--line); }}
.split-solo .show-body {{ justify-content: center; padding: 36px 44px; }}
.split-solo .show h3 {{ font-size: 30px; }}
.split-solo .show p {{ flex: 0 1 auto; font-size: 15.5px; }}
@media (max-width: 860px) {{
  .split-solo .show {{ flex-direction: column; }}
  .split-solo .vis {{ flex: none; height: 200px; border-right: none; border-bottom: 1px solid var(--line); }}
  .split-solo .show-body {{ padding: 24px 22px 26px; }}
  .split-solo .show h3 {{ font-size: 22px; }}
}}
.show {{
  position: relative; display: flex; flex-direction: column; overflow: hidden; border-radius: var(--r-lg);
  background: linear-gradient(180deg, #17142a, #110e1f); border: 1px solid var(--line-2);
  transition: transform .25s, border-color .25s, box-shadow .25s;
}}
.show::before {{
  content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; opacity: 0; transition: opacity .3s;
  background: radial-gradient(500px 220px at 50% 0%, rgba(61,107,255,.22), transparent 70%);
}}
.show:hover {{ transform: translateY(-4px); border-color: rgba(125,155,255,.5); box-shadow: 0 30px 60px -30px rgba(15,71,245,.7); }}
.show:hover::before {{ opacity: 1; }}
.vis {{
  position: relative; height: 210px; overflow: hidden; border-bottom: 1px solid var(--line);
  background:
    radial-gradient(420px 180px at 50% 110%, rgba(61,107,255,.28), transparent 70%),
    radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px) 0 0 / 18px 18px,
    #0f0c1c;
}}
.show-body {{ position: relative; display: flex; flex-direction: column; gap: 12px; padding: 26px 30px 28px; flex: 1; }}
.show-body .badges {{ align-items: center; }}
.show-body .time {{ margin-left: 4px; }}
.show h3 {{ font-size: 24px; line-height: 1.25; letter-spacing: -.02em; font-weight: 500; }}
.show p {{ font-size: 14.5px; color: var(--dim); line-height: 1.7; font-weight: 300; flex: 1; }}
.show-cta {{ margin-top: 6px; font-size: 14px; font-weight: 600; color: var(--brand-3); }}
.show-cta b {{ display: inline-block; transition: transform .25s; }}
.show:hover .show-cta b {{ transform: translateX(5px); }}

/* deck visual */
.deck-s {{
  position: absolute; width: 250px; height: 148px; border-radius: 12px; top: 34px; left: 50%;
  border: 1px solid rgba(157,180,255,.28); background: linear-gradient(160deg, #1c2152, #141238);
  box-shadow: 0 18px 40px rgba(0,0,0,.45); transition: transform .45s cubic-bezier(.2,.8,.2,1);
}}
.deck-s.s3 {{ transform: translateX(-50%) translate(-52px, 18px) rotate(-9deg); opacity: .7; border-color: rgba(157,180,255,.35); }}
.deck-s.s2 {{ transform: translateX(-50%) translate(48px, 10px) rotate(7deg); opacity: .85; border-color: rgba(157,180,255,.4); }}
.deck-s.s1 {{
  transform: translateX(-50%); padding: 14px 16px; border-color: rgba(157,180,255,.5);
  background: linear-gradient(160deg, #23307a, #16144a); box-shadow: 0 20px 50px rgba(15,71,245,.35);
}}
.show:hover .deck-s.s3 {{ transform: translateX(-50%) translate(-70px, 18px) rotate(-13deg); }}
.show:hover .deck-s.s2 {{ transform: translateX(-50%) translate(66px, 12px) rotate(11deg); }}
.show:hover .deck-s.s1 {{ transform: translateX(-50%) translateY(-6px) scale(1.03); }}
.ds-top {{ display: flex; gap: 4px; }}
.ds-top i {{ width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,.3); }}
.ds-title {{ margin-top: 12px; width: 62%; height: 9px; border-radius: 4px; background: linear-gradient(90deg, #fff, #9db4ff); }}
.ds-sub {{ margin-top: 7px; width: 40%; height: 6px; border-radius: 3px; background: rgba(255,255,255,.28); }}
.ds-row {{ margin-top: 14px; display: flex; gap: 14px; align-items: flex-end; }}
.ds-bars {{ display: flex; gap: 5px; align-items: flex-end; height: 52px; }}
.ds-bars b {{ width: 11px; border-radius: 3px 3px 0 0; background: linear-gradient(180deg, #6f8cff, #0F47F5); }}
.ds-bars b:nth-child(4) {{ background: linear-gradient(180deg, #f9a8d4, #8b5cf6); }}
.ds-lines {{ flex: 1; display: flex; flex-direction: column; gap: 7px; padding-bottom: 4px; }}
.ds-lines em {{ height: 5px; border-radius: 3px; background: rgba(255,255,255,.2); }}
.ds-lines em:nth-child(2) {{ width: 80%; }}
.ds-lines em:nth-child(3) {{ width: 60%; }}

/* flow visual */
.vis-flow .flow-m {{ display: none; }}
.vis-flow svg {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; padding: 14px 10px; }}
.flow-lines path {{ fill: none; stroke: rgba(125,155,255,.5); stroke-width: 1.5; stroke-dasharray: 5 6; animation: dash 1.6s linear infinite; }}
.show:hover .flow-lines path {{ stroke: #9db4ff; animation-duration: .8s; }}
@keyframes dash {{ to {{ stroke-dashoffset: -22; }} }}
.flow-nodes .nd {{ fill: #1b1830; stroke: rgba(255,255,255,.14); transition: stroke .3s; }}
.show:hover .flow-nodes .nd {{ stroke: rgba(157,180,255,.45); }}
.flow-nodes text {{ fill: #e4e2ec; font: 500 12.5px var(--font); }}
.flow-nodes .port {{ fill: #0f0c1c; stroke: #6f8cff; stroke-width: 1.5; }}
.hub-ring {{ fill: none; stroke: rgba(125,155,255,.35); stroke-width: 1; stroke-dasharray: 3 5; animation: spin 18s linear infinite; transform-origin: 260px 100px; }}
.hub-disc {{ fill: #f4f6ff; filter: drop-shadow(0 0 18px rgba(80,120,255,.85)); transition: filter .3s; }}
.show:hover .hub-disc {{ filter: drop-shadow(0 0 28px rgba(120,150,255,1)); }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}

/* ============ grid / cards ============ */
.tabs {{
  display: flex; gap: 4px; width: max-content; max-width: 100%; margin: 0 auto 26px; padding: 4px; overflow-x: auto;
  background: rgba(255,255,255,.04); border: 1px solid var(--line); border-radius: 12px;
}}
.tab {{
  -webkit-appearance: none; appearance: none; background: none; border: none; cursor: pointer; white-space: nowrap;
  padding: 8px 16px; border-radius: 9px; font-size: 13.5px; font-weight: 500; color: var(--mute); transition: color .2s, background .2s;
}}
.tab:hover {{ color: #fff; }}
.tab.on {{ color: #fff; background: rgba(255,255,255,.09); box-shadow: inset 0 1px 0 rgba(255,255,255,.08); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 16px; }}
.grid.few {{ display: flex; flex-wrap: wrap; justify-content: center; }}
.grid.few > .card {{ width: 100%; max-width: 280px; }}
.card {{
  position: relative; display: flex; flex-direction: column; gap: 10px; padding: 22px 22px 18px;
  background: linear-gradient(180deg, var(--card-2), var(--card)); border: 1px solid var(--line); border-radius: var(--r-md);
  transition: transform .22s, border-color .22s, box-shadow .22s;
}}
.card::after {{
  content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; opacity: 0; transition: opacity .25s;
  background: radial-gradient(420px 160px at 50% 0%, rgba(61,107,255,.16), transparent 70%);
}}
.card:hover {{ transform: translateY(-3px); border-color: rgba(125,155,255,.42); box-shadow: 0 24px 50px -28px rgba(15,71,245,.75); }}
.card:hover::after {{ opacity: 1; }}
.card h3 {{ font-size: 16.5px; line-height: 1.35; letter-spacing: -.01em; font-weight: 600; }}
.card p {{
  font-size: 13.5px; color: var(--mute); line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}}
.card-foot {{ margin-top: auto; display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--line); }}
.go {{ font-size: 12.5px; font-weight: 600; color: var(--brand-3); opacity: 0; transform: translateX(-4px); transition: opacity .2s, transform .2s; }}
.card:hover .go {{ opacity: 1; transform: none; }}
.card-hl {{
  overflow: hidden; border-color: rgba(110,145,255,.28);
  background:
    radial-gradient(120% 70% at 50% -10%, rgba(61,107,255,.38), rgba(61,107,255,.08) 55%, transparent 80%),
    var(--card);
}}
.card-hl::before {{
  content: ""; position: absolute; left: 12%; right: 12%; top: 0; height: 1px;
  background: linear-gradient(90deg, transparent, #8fb4ff, transparent);
}}
.card-hl .go {{ opacity: 1; transform: none; }}
.hl-badge {{
  position: absolute; top: 20px; right: 20px;
  padding: 3px 10px; font-size: 11.5px; font-weight: 600;
  color: #fff; background: linear-gradient(90deg, #ff7a18, #ff2d20); border-radius: 6px;
}}

/* ============ support ============ */
.dark-grid {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 16px; }}
.dark-grid.dark-full {{ grid-template-columns: 1fr; }}
.chans {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-content: start; }}
.chan {{
  display: flex; flex-direction: column; padding: 22px; border-radius: var(--r-md);
  background: linear-gradient(180deg, var(--card-2), var(--card)); border: 1px solid var(--line);
}}
.chan-n {{
  display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; margin-bottom: 14px;
  font-size: 13px; font-weight: 700; color: #fff; background: linear-gradient(135deg, #0F47F5, #6d4bff);
}}
.chan b {{ display: block; font-size: 15.5px; font-weight: 600; margin-bottom: 6px; }}
.chan > span:not(.chan-n):not(.chan-go) {{ font-size: 13.5px; color: var(--mute); line-height: 1.6; }}
.chan-link {{ transition: transform .22s, border-color .22s, box-shadow .22s; }}
.chan-link:hover {{ transform: translateY(-3px); border-color: rgba(125,155,255,.42); box-shadow: 0 24px 50px -28px rgba(15,71,245,.75); }}
.chan-go {{ margin-top: auto; padding-top: 14px; font-size: 13px; font-weight: 600; color: var(--brand-3); }}
.dlinks {{ padding: 8px 24px; border-radius: var(--r-md); background: linear-gradient(180deg, var(--card-2), var(--card)); border: 1px solid var(--line); }}
.dsub {{ font-size: 12px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--mute); padding: 16px 0 6px; }}
.dlink {{ display: grid; grid-template-columns: 1fr auto; gap: 4px 14px; align-items: center; padding: 15px 0; border-top: 1px solid var(--line); }}
.dlink-t {{ grid-column: 1; grid-row: 1; font-size: 14.5px; font-weight: 600; transition: color .2s; }}
.dlink-d {{
  grid-column: 1; grid-row: 2; font-size: 13px; color: var(--mute); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.arrow {{ grid-column: 2; grid-row: 1 / 3; color: var(--mute); font-size: 17px; transition: transform .2s, color .2s; }}
.dlink:hover .dlink-t, .dlink:hover .arrow {{ color: var(--brand-3); }}
.dlink:hover .arrow {{ transform: translateX(4px); }}

/* ============ CTA band ============ */
.cta-band {{ padding: 110px 0 90px; scroll-margin-top: 0; overflow-x: clip; }}
.cta-box {{
  position: relative; overflow: hidden; text-align: center; padding: 64px 28px; border-radius: 28px;
  border: 1px solid rgba(125,155,255,.25);
  background:
    radial-gradient(700px 300px at 50% 120%, rgba(61,107,255,.45), transparent 70%),
    radial-gradient(400px 200px at 10% 0%, rgba(139,92,246,.25), transparent 70%),
    linear-gradient(180deg, #14112a, #0e0c1d);
}}
.cta-box h2 {{ font-size: 44px; line-height: 1.15; letter-spacing: -.03em; font-weight: 500; }}
.cta-box h2 .dim {{ color: var(--mute); }}
.cta-box p {{ margin: 14px auto 0; max-width: 56ch; color: var(--dim); font-weight: 300; font-size: 16px; }}
.cta-actions {{ margin-top: 28px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
.btn-ghost {{
  display: inline-flex; align-items: center; gap: 6px; padding: 11px 20px; border-radius: 10px; font-size: 14px; font-weight: 600;
  color: var(--text); background: rgba(255,255,255,.05); border: 1px solid var(--line-2); transition: background .2s;
}}
.btn-ghost:hover {{ background: rgba(255,255,255,.1); }}


/* ============ back to top ============ */
.btt {{
  position: fixed; bottom: 26px; right: 26px; z-index: 20; width: 44px; height: 44px; border-radius: 12px;
  border: 1px solid var(--line-2); background: rgba(22,19,36,.85); color: #fff; cursor: pointer;
  backdrop-filter: blur(10px); opacity: 0; pointer-events: none; transition: opacity .25s, transform .25s;
  display: flex; align-items: center; justify-content: center; -webkit-appearance: none; appearance: none;
}}
.btt.on {{ opacity: 1; pointer-events: auto; }}
.btt:hover {{ transform: translateY(-2px); border-color: rgba(125,155,255,.6); }}

/* ============ footer ============ */
footer {{ border-top: 1px solid var(--line); background: #08070f; color: var(--mute); padding: 60px 0 36px; font-size: 13.5px; line-height: 1.75; }}
.ft-grid {{ display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 48px; }}
.ft-brand {{ display: flex; flex-direction: column; gap: 16px; }}
.ft-brand .spark-logo {{ height: 32px; width: auto; align-self: flex-start; }}
.ft-desc {{ font-size: 13.5px; max-width: 38ch; }}
.ft-h {{ font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .12em; color: var(--text); margin-bottom: 14px; }}
.ft-list {{ list-style: none; padding: 0; display: flex; flex-direction: column; gap: 10px; }}
.ft-list li {{ display: flex; align-items: flex-start; gap: 10px; }}
.ft-list svg {{ flex-shrink: 0; width: 16px; height: 16px; margin-top: 4px; color: var(--brand-3); }}
footer a {{ color: var(--dim); transition: color .2s; }}
footer a:hover {{ color: #fff; }}
.ft-divider {{ grid-column: 1 / -1; border: none; border-top: 1px solid var(--line); margin: 6px 0 0; }}
.ft-bottom {{ grid-column: 1 / -1; font-size: 12.5px; color: var(--mute); }}
.empty {{ display: none; padding: 60px 0; text-align: center; color: var(--mute); font-size: 15px; }}
.hide {{ display: none !important; }}

/* ============ responsive ============ */
@media (max-width: 960px) {{
  .badge {{ font-size: 11px; }}
  .logo-label {{ display: none; }}
  .hero-grid {{ grid-template-columns: 1fr; min-height: 0; }}
  .hero-art {{ position: absolute; right: -60px; top: 0; height: 100%; opacity: .35; pointer-events: none; }}
  .hero h1 {{ font-size: 44px; }}
  .stats {{ grid-template-columns: 1fr; }}
  .stat p {{ font-size: 14.5px; }}
  .split, .dark-grid {{ grid-template-columns: 1fr; }}
  .sec-head h2, .cta-box h2 {{ font-size: 34px; }}
  .ft-grid {{ grid-template-columns: 1fr 1fr; gap: 36px; }}
  .ft-brand {{ grid-column: 1 / -1; }}
}}
@media (max-width: 640px) {{
  .wrap {{ padding: 0 16px; }}
  header {{ padding-top: 8px; }}
  .head-in {{ gap: 8px; padding: 0 6px 0 12px; height: 52px; }}
  .logo-label, .cta {{ display: none; }}
  .hero-partner {{ gap: 12px; }}
  .hero-partner .lark-partner {{ height: 34px; padding-right: 0; border-right: none; }}
  .spark-logo {{ height: 22px; }}
  .hero {{ padding: 44px 0 20px; }}
  .hero h1 {{ font-size: 34px; }}
  .hero-sub {{ font-size: 15.5px; }}
  .bolt {{ height: 340px; }}
  .section {{ padding-top: 72px; }}
  .sec-head h2, .cta-box h2 {{ font-size: 28px; }}
  .show-body {{ padding: 22px 22px 24px; }}
  .show h3 {{ font-size: 21px; }}
  .vis {{ height: 180px; }}
  .grid, .chans {{ grid-template-columns: 1fr; }}
  .go {{ opacity: 1; transform: none; }}
  .cta-box {{ padding: 44px 20px; }}
  .ft-grid {{ grid-template-columns: 1fr; gap: 30px; }}
  .btt {{ bottom: 16px; right: 16px; width: 40px; height: 40px; }}
  .hero-art {{ right: -110px; opacity: .16; }}
  .hero h1 {{ font-size: 32px; }}
  .hero-actions {{ gap: 10px; }}
  .hero-actions .hbtn {{ flex: 1 1 0; padding: 0 10px; font-size: 14px; }}
  .hero-featured {{ display: flex; flex-wrap: wrap; row-gap: 6px; border-radius: 14px; padding: 10px 14px; }}
  .search-row {{ margin-top: 22px; }}
  .hf-title {{ white-space: normal; flex: 1 1 60%; }}
  .stats {{ gap: 10px; }}
  .stat {{ padding: 14px 16px; gap: 14px; }}
  .stat-ico {{ width: 42px; height: 42px; border-radius: 11px; }}
  .stat-ico img {{ width: 26px; }}
  .stat p {{ font-size: 14px; }}
  .section {{ padding-top: 64px; }}
  .sec-head {{ margin-bottom: 26px; }}
  .sec-head h2 {{ font-size: 26px; }}
  .lead {{ font-size: 14.5px; }}
  .tabs {{ margin: 0 0 18px; width: auto; }}
  .tab {{ padding: 10px 14px; font-size: 13.5px; }}
  .logo {{ padding: 8px 0; }}
  .grid {{ gap: 10px; }}
  .card {{ padding: 16px 16px 14px; gap: 8px; border-radius: 14px; }}
  .card h3 {{ font-size: 15.5px; }}
  .card p {{ -webkit-line-clamp: 2; font-size: 13.5px; }}
  .card-foot {{ padding-top: 10px; }}
  .badge {{ font-size: 11px; }}
  .vis-flow .flow-m {{ display: block; }}
  .vis-flow .flow-d {{ display: none; }}
  .split-solo .vis {{ height: 210px; }}
  .chan {{ padding: 18px; }}
  .dlinks {{ padding: 6px 18px; }}
  .cta-band {{ padding: 72px 0 60px; }}
  .cta-actions {{ flex-direction: column; align-items: stretch; }}
  footer {{ padding: 44px 0 30px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  *, *::before, *::after {{ transition-duration: .001ms !important; animation: none !important; }}
}}
</style>
</head>
<body>

<header>
  <div class="wrap">
    <div class="head-in">
      <a class="logo" href="https://sparktech.top/#/home" target="_blank" rel="noopener" aria-label="Spark Technology">
        {SPARK_LOGO_WHITE}
      </a>
      <nav>{''.join(navs)}</nav>
      <a class="cta" href="https://www.larksuite.com/vi_vn/download" target="_blank" rel="noopener">Bắt đầu ngay</a>
    </div>
  </div>
</header>

<section class="hero" id="top">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <div class="hero-partner">
          {LARK_PARTNER}
          <span class="hero-kicker"><i>Platinum</i> Đối tác Lark tại Việt Nam</span>
        </div>
        <h1><span class="dim">Thư viện tài liệu Lark</span><br><span class="h1-line">dành cho doanh nghiệp Việt Nam</span></h1>
        <p class="hero-sub">Từ hướng dẫn cơ bản đến ứng dụng chuyên sâu, khám phá kho tài liệu tiếng Việt do Spark tổng hợp và biên soạn, giúp doanh nghiệp khai thác hiệu quả Lark, Lark Base và AI trong công việc.</p>
        <div class="hero-actions">
          <a class="hbtn hbtn-primary" href="https://bytedance.larkoffice.com/wiki/PjXtw0JudiYY2WkFAPfcZBOhntc" target="_blank" rel="noopener">Xem slide giới thiệu</a>
          <a class="hbtn hbtn-ghost" href="#lien-he">Đăng ký tư vấn</a>
        </div>
        <a class="hero-featured" href="{esc(meta['featured']['url'])}" target="_blank" rel="noopener">
          <span class="hf-tag">{esc(meta['featured']['label'])}</span>
          <span class="hf-title">{esc(meta['featured']['title'])}</span>
          <span class="hf-go">Đọc ngay →</span>
        </a>
        <div class="search-row">
          <div class="search-box">
            <svg class="ico-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="search" id="search" placeholder="Tìm tài liệu, ví dụ: phê duyệt, Base, AI..." autocomplete="off">
            <button type="button" class="search-clear" id="search-clear" aria-label="Xoá tìm kiếm">&times;</button>
          </div>
          <div class="search-status">
            <span class="search-count" id="search-count"></span>
          <button type="button" class="filter-reset" id="filter-reset">
            <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg>
            Xoá bộ lọc
          </button>
        </div>
      </div>
      </div>
      <div class="hero-art" id="hero-art">{BOLT}<span class="ring r1"></span><span class="ring r2"></span><span class="ring r3"></span><span class="sparks"><i class="spk" style="--a:-160deg;--d:120px;--t:0.7s"></i><i class="spk" style="--a:-130deg;--d:150px;--t:0.8s"></i><i class="spk" style="--a:-105deg;--d:110px;--t:0.6s"></i><i class="spk" style="--a:-80deg;--d:160px;--t:0.75s"></i><i class="spk" style="--a:-55deg;--d:130px;--t:0.7s"></i><i class="spk" style="--a:-30deg;--d:115px;--t:0.65s"></i><i class="spk" style="--a:-145deg;--d:90px;--t:0.55s"></i><i class="spk" style="--a:-15deg;--d:95px;--t:0.6s"></i><i class="spk" style="--a:-95deg;--d:175px;--t:0.85s"></i><i class="spk" style="--a:-65deg;--d:100px;--t:0.55s"></i></span></div>
    </div>
    <div class="stats">
      <a class="stat st-lark" href="https://sparktech.top/#/home" target="_blank" rel="noopener">
        <span class="stat-ico"><img src="{_img64('lark-bird.png')}" alt=""></span>
        <p><b>Đối tác Platinum của Lark.</b> Triển khai chính thức tại Việt Nam.</p>
      </a>
      <a class="stat st-docs" href="#gioi-thieu">
        <span class="stat-ico"><img src="{_lark_icon('lark-wiki-icon-01')}" alt=""></span>
        <p><b>Cập nhật theo từng phiên bản.</b> Hướng dẫn tiếng Việt, từ nhập môn tới Base và AI.</p>
      </a>
      <a class="stat st-academy" href="#spark-academy">
        <span class="stat-ico"><span class="spark-grad" style="-webkit-mask-image:url({_img64('spark-bolt-white.png')});mask-image:url({_img64('spark-bolt-white.png')})"></span></span>
        <p><b>Lark Academy by Spark.</b> Học nhanh hơn, chuyển đổi nhanh hơn.</p>
      </a>
    </div>
  </div>
</section>

{''.join(sections)}
<div class="wrap"><div class="empty" id="empty">Không có tài liệu nào phù hợp với từ khoá hoặc bộ lọc hiện tại.</div></div>

<section class="cta-band" id="lien-he">
  <div class="wrap">
    <div class="cta-box">
      <h2><span class="dim">Cần triển khai Lark</span><br>cho doanh nghiệp của bạn?</h2>
      <p>Để lại thông tin qua form, đội ngũ Spark sẽ liên hệ tư vấn, cấu hình và đào tạo để cả công ty dùng Lark hiệu quả ngay từ tuần đầu.</p>
      <div class="cta-actions">
        <a class="hbtn hbtn-primary" href="{esc(meta['deploy_form'])}" target="_blank" rel="noopener">Đăng ký tư vấn triển khai →</a>
        <a class="hbtn hbtn-ghost" href="mailto:wengjiajun@sparklark.group" title="wengjiajun@sparklark.group"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7"/></svg>Liên hệ qua email</a>
      </div>
    </div>
  </div>
</section>

<button type="button" class="btt" id="btt" aria-label="Lên đầu trang">
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M18 15l-6-6-6 6"/></svg>
</button>

<footer>
  <div class="wrap">
    <div class="ft-grid">
      <div class="ft-brand">
        <div class="ft-logos"><a href="https://sparktech.top/#/home" target="_blank" rel="noopener" aria-label="Spark Technology">{SPARK_LOGO_WHITE}</a><span class="ft-x">&times;</span>{LARK_PARTNER}</div>
        <p class="ft-desc">Spark Technology &mdash; Đối tác Platinum của Lark tại Việt Nam. Tư vấn, triển khai, đào tạo và đồng hành cùng doanh nghiệp chuyển đổi số trên nền tảng Lark.</p>
      </div>
      <div>
        <p class="ft-h">Liên hệ</p>
        <ul class="ft-list">
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.362 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg><span><a href="tel:+84359791893">+84 359 791 893</a></span></li>
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7"/></svg><span><a href="mailto:wengjiajun@sparklark.group">wengjiajun@sparklark.group</a></span></li>
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></svg><span>WeChat: 13987177342</span></li>
        </ul>
      </div>
      <div>
        <p class="ft-h">Thông tin</p>
        <ul class="ft-list">
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 1116 0z"/><circle cx="12" cy="10" r="3"/></svg><span>140 Đường B2, P. An Khánh,<br>TP. Hồ Chí Minh, Việt Nam</span></li>
          <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg><span><a href="https://sparktech.top/#/home" target="_blank" rel="noopener">sparktech.top</a></span></li>
        </ul>
      </div>
      <hr class="ft-divider">
      <div class="ft-bottom">&copy; 2026 Công ty TNHH Công Nghệ Spark &mdash; MST: 0318871464</div>
    </div>
  </div>
</footer>

<script>
(function () {{
  var $ = function (s) {{ return document.querySelector(s); }};
  var $$ = function (s) {{ return [].slice.call(document.querySelectorAll(s)); }};
  var subtabs = $$('.tabs'), tabs = $$('.tab'), items = $$('.item');
  var sections = $$('.section'), navs = $$('.nav-item'), navBar = $('nav');
  var empty = $('#empty'), heroInput = $('#search');
  var searchCount = $('#search-count'), searchClear = $('#search-clear'), filterReset = $('#filter-reset'), btt = $('#btt');
  var headerEl = $('.head-in');
  function headH() {{ return headerEl.getBoundingClientRect().bottom; }}
  var tab = 'all', terms = [], lock = false, lockTimer;

  function norm(t) {{
    return (t || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/đ/g, 'd');
  }}
  items.forEach(function (el) {{
    var sec = el.closest('.section');
    var group = sec ? sec.querySelector('h2').textContent : '';
    el._hay = norm(el.dataset.title + ' ' + el.dataset.desc + ' ' + group);
  }});

  function setNav(id) {{
    navs.forEach(function (n) {{
      var on = n.dataset.nav === id;
      if (on && !n.classList.contains('on')) {{
        var target = n.offsetLeft - navBar.offsetLeft - (navBar.clientWidth - n.offsetWidth) / 2;
        navBar.scrollTo({{ left: Math.max(0, target), behavior: 'smooth' }});
      }}
      n.classList.toggle('on', on);
    }});
  }}

  function anchorOf(sec) {{ return sec.querySelector('.sec-head') || sec.querySelector('.cta-box') || sec; }}
  function anchorY(sec) {{ return Math.max(0, anchorOf(sec).getBoundingClientRect().top + window.scrollY - headH() - 20); }}

  function current() {{
    var id = sections[0].id, line = Math.min(window.innerHeight * 0.4, headH() + 220);
    sections.forEach(function (s) {{
      if (anchorOf(s).getBoundingClientRect().top <= line) id = s.id;
    }});
    if (window.scrollY < anchorY(sections[0]) - 200) id = null;
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) id = sections[sections.length - 1].id;
    return id;
  }}
  function onScroll() {{
    btt.classList.toggle('on', window.scrollY > 600);
    if (!lock) setNav(current());
  }}

  var anim = 0, guard = 0;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function stopAnim() {{ if (anim) {{ cancelAnimationFrame(anim); clearTimeout(guard); anim = 0; lock = false; setNav(current()); }} }}
  ['wheel', 'touchstart', 'keydown'].forEach(function (ev) {{
    window.addEventListener(ev, function (e) {{ if (ev !== 'keydown' || /^(Arrow|Page|Home|End| )/.test(e.key)) stopAnim(); }}, {{ passive: true }});
  }});
  function scrollToY(y, navId) {{
    if (anim) cancelAnimationFrame(anim);
    clearTimeout(guard);
    var max = document.documentElement.scrollHeight - window.innerHeight;
    y = Math.max(0, Math.min(y, max));
    var start = window.scrollY, dist = y - start;
    lock = true;
    if (navId !== undefined) setNav(navId);
    if (reduce || Math.abs(dist) < 2) {{
      window.scrollTo(0, y); lock = false; anim = 0; return;
    }}
    var dur = Math.min(750, 350 + Math.abs(dist) * 0.06), t0 = null;
    function ease(t) {{ return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }}
    function finish() {{
      clearTimeout(guard); anim = 0; lock = false;
      setNav(navId !== undefined && navId !== null ? navId : current());
    }}
    function step(ts) {{
      if (t0 === null) t0 = ts;
      var k = Math.min(1, (ts - t0) / dur);
      window.scrollTo(0, start + dist * ease(k));
      if (k < 1) anim = requestAnimationFrame(step); else finish();
    }}
    anim = requestAnimationFrame(step);
    guard = setTimeout(function () {{
      if (anim) {{ cancelAnimationFrame(anim); window.scrollTo(0, y); finish(); }}
    }}, dur + 250);
  }}
  function goTo(sec) {{ scrollToY(anchorY(sec), sec.id); }}

  function apply(scroll) {{
    var shown = 0, active = terms.length;
    items.forEach(function (el) {{
      var okG = active || !el.dataset.sg || tab === 'all' || el.dataset.sg === tab;
      var okQ = terms.every(function (w) {{ return el._hay.indexOf(w) > -1; }});
      var on = okG && okQ;
      el.classList.toggle('hide', !on);
      if (on) shown++;
    }});
    subtabs.forEach(function (t) {{ t.classList.toggle('hide', !!active); }});
    var firstHit = null;
    sections.forEach(function (s) {{
      var has = s.querySelector('.item:not(.hide)') !== null;
      var msg = s.querySelector('.sec-empty');
      if (msg) msg.style.display = active && !has ? 'block' : 'none';
      if (has && !firstHit) firstHit = s;
    }});
    empty.style.display = shown === 0 ? 'block' : 'none';
    searchClear.classList.toggle('on', terms.length > 0);
    searchCount.textContent = shown + ' kết quả';
    searchCount.classList.toggle('on', !!active);
    filterReset.classList.toggle('on', !!active);
    if (scroll && active && firstHit) goTo(firstHit);
  }}

  var debounce;
  function readTerms() {{ terms = norm(heroInput.value).split(/\\s+/).filter(Boolean); }}
  heroInput.addEventListener('input', function () {{
    clearTimeout(debounce);
    debounce = setTimeout(function () {{ readTerms(); apply(true); }}, 600);
  }});
  heroInput.addEventListener('keydown', function (e) {{
    if (e.key === 'Escape') {{ resetAll(); heroInput.blur(); }}
    if (e.key === 'Enter') {{ clearTimeout(debounce); readTerms(); apply(true); }}
  }});
  document.addEventListener('keydown', function (e) {{
    var tag = (e.target.tagName || '').toLowerCase();
    if (e.key === '/' && tag !== 'input' && tag !== 'textarea') {{
      e.preventDefault(); scrollToY(0, null); heroInput.focus({{ preventScroll: true }});
    }}
  }});

  function resetAll() {{
    terms = []; tab = 'all'; heroInput.value = '';
    tabs.forEach(function (t) {{ t.classList.toggle('on', t.dataset.tab === 'all'); }});
    apply(false);
  }}
  searchClear.addEventListener('click', function () {{
    terms = []; heroInput.value = ''; apply(false); heroInput.focus();
  }});
  filterReset.addEventListener('click', function () {{ resetAll(); scrollToY(0, null); }});

  function clearSearch() {{
    if (!terms.length && !heroInput.value) return;
    clearTimeout(debounce); terms = []; heroInput.value = ''; apply(false);
  }}

  tabs.forEach(function (t) {{
    t.addEventListener('click', function () {{
      clearSearch();
      tab = t.dataset.tab;
      [].forEach.call(t.parentNode.querySelectorAll('.tab'), function (o) {{ o.classList.toggle('on', o === t); }});
      apply(false);
    }});
  }});

  navs.forEach(function (n) {{
    n.addEventListener('click', function (e) {{
      var sec = document.getElementById(n.dataset.nav);
      if (!sec) return;
      e.preventDefault();
      clearSearch();
      goTo(sec);
      history.replaceState(null, '', '#' + sec.id);
      n.blur();
    }});
  }});
  $$('.stat[href^="#"]').forEach(function (a) {{
    a.addEventListener('click', function (e) {{
      var sec = document.getElementById(a.getAttribute('href').slice(1));
      if (!sec) return;
      e.preventDefault(); goTo(sec);
    }});
  }});
  $$('a[href="#lien-he"]').forEach(function (a) {{
    a.addEventListener('click', function (e) {{
      e.preventDefault();
      scrollToY(anchorY($('#lien-he')), null);
    }});
  }});
  btt.addEventListener('click', function () {{ scrollToY(0, null); }});
  var art = $('#hero-art');
  function strike() {{
    if (!art || reduce || document.hidden) return;
    art.classList.remove('strike'); void art.offsetWidth; art.classList.add('strike');
    setTimeout(function () {{ art.classList.remove('strike'); }}, 1400);
  }}
  if (art && !reduce) {{
    setTimeout(strike, 1200);
    setInterval(strike, 5500);
    art.addEventListener('pointerenter', strike);
  }}
  if (art && window.matchMedia('(hover: hover) and (pointer: fine)').matches && !reduce) {{
    var boltEl = art.querySelector('.bolt');
    art.addEventListener('pointermove', function (e) {{
      var r = art.getBoundingClientRect();
      var dx = (e.clientX - r.left) / r.width - .5, dy = (e.clientY - r.top) / r.height - .5;
      art.classList.add('tilt');
      boltEl.style.setProperty('--ry', (dx * 22).toFixed(2) + 'deg');
      boltEl.style.setProperty('--rx', (-dy * 16).toFixed(2) + 'deg');
    }});
    art.addEventListener('pointerleave', function () {{
      art.classList.remove('tilt');
      boltEl.style.setProperty('--ry', '0deg'); boltEl.style.setProperty('--rx', '0deg');
    }});
  }}
  window.addEventListener('scroll', onScroll, {{ passive: true }});
  if (location.hash) {{
    var h = document.getElementById(location.hash.slice(1));
    if (h && h.classList.contains('section')) setTimeout(function () {{ window.scrollTo(0, anchorY(h)); setNav(h.id); }}, 0);
  }}
  onScroll();
}})();
</script>
</body>
</html>
"""

out = HERE / "index.html"
out.write_text(HTML, encoding="utf-8")
tpl = ", ".join(g["template"] for g in data["groups"])
print(f"wrote {out} ({len(HTML)} bytes) docs={total_docs}")
print(f"layout: {tpl}")
