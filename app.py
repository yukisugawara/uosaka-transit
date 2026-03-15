import streamlit as st
from datetime import datetime, time, date
from datetime import timedelta as _td

from lib.search import search_routes
from lib.timetable import get_bus_stops, get_shuttle_last_time, get_shuttle_status, is_shuttle_suspended
from lib.i18n import t, t_transport, t_place, t_reason

st.set_page_config(page_title="U-Osaka Transit", page_icon="\u2728", layout="centered")

# Force browser tab title (overrides Streamlit's default suffix)
st.markdown(
    "<script>document.title='U-Osaka Transit';</script>",
    unsafe_allow_html=True,
)

if "lang" not in st.session_state:
    st.session_state.lang = "ja"
if "theme" not in st.session_state:
    # default: light 6:00-17:00, dark otherwise
    hour = datetime.now().hour
    st.session_state.theme = "light" if 6 <= hour < 17 else "dark"
lang = st.session_state.lang
is_dark = st.session_state.theme == "dark"

# ================================================================== #
#  CSS
# ================================================================== #
_dark_vars = """
  --bg: #0f172a; --bg-grad: linear-gradient(160deg, #0f172a, #1e1b4b 50%, #0f172a);
  --card: rgba(255,255,255,0.04); --border: rgba(255,255,255,0.12);
  --text: #e2e8f0; --muted: #94a3b8; --dim: #475569;
  --input-bg: rgba(255,255,255,.05); --input-border: rgba(255,255,255,.1);
  --btn2-bg: rgba(255,255,255,.08); --btn2-border: rgba(255,255,255,.15);
  --btn2-text: #e2e8f0; --pill-free-text: #1a1a2e; --chip-paid-bg: rgba(255,255,255,.08);
  --chip-paid-text: #cbd5e1; --rsum-paid: #cbd5e1;
  --from-text: #c4b5fd; --to-text: #6ee7b7; --node-dim: #64748b;
  --node-bg: rgba(255,255,255,.02); --node-border: rgba(255,255,255,.1);
  --rail-line: rgba(255,255,255,.05);
"""
_light_vars = """
  --bg: #f8fafc; --bg-grad: linear-gradient(160deg, #f8fafc, #eef2ff 50%, #f8fafc);
  --card: rgba(0,0,0,0.02); --border: rgba(0,0,0,0.10);
  --text: #1e293b; --muted: #64748b; --dim: #94a3b8;
  --input-bg: rgba(0,0,0,.03); --input-border: rgba(0,0,0,.12);
  --btn2-bg: rgba(0,0,0,.05); --btn2-border: rgba(0,0,0,.12);
  --btn2-text: #334155; --pill-free-text: #1a1a2e; --chip-paid-bg: rgba(0,0,0,.06);
  --chip-paid-text: #475569; --rsum-paid: #334155;
  --from-text: #7c3aed; --to-text: #059669; --node-dim: #64748b;
  --node-bg: rgba(0,0,0,.03); --node-border: rgba(0,0,0,.12);
  --rail-line: rgba(0,0,0,.08);
"""
_theme_vars = _dark_vars if is_dark else _light_vars

_css_head = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Righteous&family=Noto+Sans+JP:wght@400;700;900&family=Inter:wght@400;600;800&display=swap');"
    ":root {"
    "  --purple:#a78bfa; --green:#34d399; --blue:#38bdf8; --gold:#fbbf24;"
    + _theme_vars +
    "}"
    "html,body,[data-testid='stAppViewContainer'] {"
    "  font-family:'Noto Sans JP','Inter',sans-serif !important;"
    "  background:var(--bg-grad) !important; color:var(--text);"
    "}"
    "[data-testid='stHeader'] { display:none !important; }"
    "footer { visibility:hidden; }"
    "hr { border-color:var(--border) !important; }"
)
_css_body = """

/* animations */
@keyframes fadeUp   { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes grad     { to{background-position:200% center} }
@keyframes dash     { to{stroke-dashoffset:0} }
@keyframes ripple   { 0%{r:22;opacity:.4} 100%{r:34;opacity:0} }

/* ---- header bar ---- */
.topbar {
  display:flex; justify-content:space-between; align-items:center;
  padding:0.6rem 0; animation:fadeIn .6s ease-out;
}
.logo {
  font-family:'Righteous',sans-serif; font-size:2.6rem;
  background:linear-gradient(90deg,var(--purple),var(--blue),var(--green));
  background-size:200% auto;
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  animation:grad 4s linear infinite;
  line-height:1; cursor:pointer;
}
/* header button row */
.hdr-btn-row { margin-bottom:.4rem; }
/* logo as button */
[data-testid="stButton"] button[key="logo_reset"],
button[kind="secondary"]:has(> div > p:first-child) {
  font-family:'Righteous',sans-serif !important;
}
/* ---- section card ---- */
.sec {
  background:var(--card);
  border:1.5px solid var(--border);
  border-radius:16px; padding:1.2rem 1.4rem; margin-bottom:0.8rem;
  animation:fadeUp .5s ease-out both;
}
.sec-route  { border-left:4px solid var(--purple); }
.sec-time   { border-left:4px solid var(--blue); }
.sec-title {
  font-size:0.95rem; font-weight:800; letter-spacing:0.04em;
  color:var(--text); margin-bottom:0.6rem;
  display:flex; align-items:center; gap:0.4rem;
}
.sec-title-icon {
  font-size:1.1rem;
}

/* ---- route card ---- */
.rcard {
  border-radius:16px; padding:1.2rem 1.4rem; margin-bottom:0.8rem;
  background:var(--card); border:1px solid var(--border);
  animation:fadeUp .4s ease-out both;
}
.rcard:nth-of-type(2){animation-delay:.12s}
.rcard-bus  { border-left:4px solid var(--green); }
.rcard-rail { border-left:4px solid var(--blue);  }

.rlabel {
  display:inline-block; padding:0.15rem 0.6rem; border-radius:999px;
  font-size:0.72rem; font-weight:800; letter-spacing:.04em; margin-bottom:0.5rem;
}
.rlabel-bus  { background:linear-gradient(135deg,var(--green),var(--purple)); color:#0f172a; }
.rlabel-rail { background:linear-gradient(135deg,var(--blue),var(--purple));  color:#0f172a; }

/* timeline */
.tl { position:relative; padding-left:1.8rem; margin:0.2rem 0; }
.tl::before {
  content:''; position:absolute; left:0.6rem; top:.4rem; bottom:.4rem;
  width:2px; background:linear-gradient(180deg,var(--purple)44,var(--green)44);
}
.tl-n { position:relative; padding:.3rem 0; }
.tl-n::before {
  content:''; position:absolute; left:-1.3rem; top:.55rem;
  width:8px; height:8px; border-radius:50%;
  background:var(--purple); box-shadow:0 0 6px rgba(167,139,250,.5);
}
.tl-n:last-child::before { background:var(--green); box-shadow:0 0 6px rgba(52,211,153,.5); }
.tl-h { font-weight:700; font-size:.88rem; color:var(--text); }
.tl-s { font-size:.78rem; color:var(--muted); margin-top:.02rem; }

.chip-free {
  display:inline-block; background:linear-gradient(135deg,var(--gold),#f59e0b);
  color:#1a1a2e; font-weight:900; font-size:.68rem;
  padding:.08rem .45rem; border-radius:999px; margin-left:.3rem;
  box-shadow:0 0 6px rgba(251,191,36,.3);
}
.chip-paid {
  display:inline-block; background:var(--chip-paid-bg);
  color:var(--chip-paid-text); font-weight:700; font-size:.68rem;
  padding:.08rem .45rem; border-radius:999px; margin-left:.3rem;
}

.rsum {
  display:flex; justify-content:space-between; align-items:center;
  flex-wrap:wrap; gap:.4rem;
  margin-top:.5rem; padding-top:.4rem;
  border-top:1px solid var(--border); font-size:.82rem;
}
.rsum-t { color:var(--muted); }
.rsum-f0 {
  font-weight:900; font-size:1.05rem;
  background:linear-gradient(90deg,var(--gold),#f59e0b);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.rsum-f1 { font-weight:700; font-size:.95rem; color:var(--rsum-paid); }

/* status */
.pill {
  display:inline-flex; align-items:center; gap:.25rem;
  padding:.2rem .7rem; border-radius:999px; font-size:.75rem; font-weight:700;
}
.pill-ok  { background:rgba(52,211,153,.12); color:var(--green); }
.pill-off { background:rgba(239,68,68,.12);  color:#f87171; }

/* widget overrides */
div[data-testid="stSelectbox"] > div > div {
  background:var(--input-bg)!important;
  border-color:var(--input-border)!important;
  border-radius:10px!important; color:var(--text)!important;
}
[data-testid="stSelectbox"] label,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] span,
[data-testid="stCheckbox"] p,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label { color:var(--muted)!important; font-weight:600!important; font-size:.82rem!important; }
/* ensure all streamlit text inherits theme color */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] div { color: inherit; }
[data-testid="stMarkdownContainer"] p { color:var(--text)!important; }
[data-testid="stWidgetLabel"] p { color:var(--muted)!important; }

button[kind="primary"] {
  background:linear-gradient(135deg,var(--purple),var(--blue))!important;
  border:none!important; border-radius:12px!important;
  font-weight:800!important; font-size:.95rem!important; color:#fff!important;
  padding:.6rem 1.2rem!important;
  box-shadow:0 4px 16px rgba(129,140,248,.3)!important;
  transition:all .15s!important;
}
button[kind="primary"]:hover {
  transform:translateY(-2px)!important;
  box-shadow:0 6px 22px rgba(129,140,248,.45)!important;
}
button[kind="secondary"] {
  background:var(--btn2-bg)!important;
  color:var(--btn2-text)!important;
  border:1px solid var(--btn2-border)!important;
  border-radius:8px!important;
  font-weight:700!important; font-size:.8rem!important;
  letter-spacing:.06em!important;
}
button[kind="secondary"]:hover {
  opacity:.8!important;
}
[data-testid="stAlert"] { border-radius:12px!important; }
.ft { text-align:center; font-size:.68rem; color:var(--dim); padding:.8rem 0 2rem; line-height:1.5; }
</style>
"""
st.markdown(_css_head + _css_body, unsafe_allow_html=True)

# ================================================================== #
#  Header: logo + lang toggle
# ================================================================== #
theme_icon = "\u2600\uFE0F" if is_dark else "\U0001F319"
lang_label = "EN" if lang == "ja" else "JP"

st.markdown('<div class="hdr-btn-row">', unsafe_allow_html=True)
c_logo_btn, _, c_theme, c_lang = st.columns([5, 3, 1, 1])
with c_logo_btn:
    if st.button("\u2728 U-Osaka Transit", key="logo_reset", use_container_width=True):
        for k in ["o", "d", "bs", "sh", "sm"]:
            st.session_state.pop(k, None)
        st.rerun()
with c_theme:
    if st.button(theme_icon, key="theme_btn", use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
with c_lang:
    if st.button(lang_label, key="lang_btn", use_container_width=True):
        st.session_state.lang = "en" if lang == "ja" else "ja"
        # reset selectbox caches so format_func re-renders
        for k in ["o", "d", "bs"]:
            st.session_state.pop(k, None)
        st.rerun()
lang = st.session_state.lang
st.markdown('</div>', unsafe_allow_html=True)

# ================================================================== #
#  Section 1 — Route selector + SVG map
# ================================================================== #
CAMPUSES = ["豊中キャンパス", "吹田キャンパス", "箕面キャンパス"]
CAMPUS_EMOJI = {"豊中キャンパス": "\U0001F333", "吹田キャンパス": "\U0001F3E5", "箕面キャンパス": "\U0001F342"}
CS = {"豊中キャンパス": {"ja": "豊中", "en": "Toyonaka"},
      "吹田キャンパス": {"ja": "吹田", "en": "Suita"},
      "箕面キャンパス": {"ja": "箕面", "en": "Minoh"}}
MAP_ORDER = ["豊中キャンパス", "箕面キャンパス", "吹田キャンパス"]
MAP_X = {"豊中キャンパス": 15, "箕面キャンパス": 50, "吹田キャンパス": 85}
HERE = {"ja": "現在地", "en": "I'm here"}
GOAL = {"ja": "行き先", "en": "Going to"}

_s = lambda c: CS[c][lang]  # noqa: E731

sec1_title = "ルート選択" if lang == "ja" else "SELECT ROUTE"
st.markdown(f'<div class="sec sec-route"><div class="sec-title"><span class="sec-title-icon">\U0001F4CD</span>{sec1_title}</div>', unsafe_allow_html=True)

NONE = "--"
_pick_msg = "選択してください" if lang == "ja" else "Select..."

from_opts = [NONE] + CAMPUSES
col_f, col_t = st.columns(2)
with col_f:
    origin = st.selectbox(
        f"\U0001F4CD {HERE[lang]}", from_opts, index=0,
        format_func=lambda c: _pick_msg if c == NONE else f"{CAMPUS_EMOJI[c]} {_s(c)}",
        key="o")
with col_t:
    to_opts = [NONE] + ([c for c in CAMPUSES if c != origin] if origin != NONE else CAMPUSES)
    destination = st.selectbox(
        f"\U0001F3AF {GOAL[lang]}", to_opts, index=0,
        format_func=lambda c: _pick_msg if c == NONE else f"{CAMPUS_EMOJI[c]} {_s(c)}",
        key="d")

# swap button
if origin != NONE and destination != NONE:
    swap_label = "\U0001F504 入れ替え" if lang == "ja" else "\U0001F504 Swap"
    if st.button(swap_label, key="swap"):
        st.session_state.o = destination
        st.session_state.d = origin
        st.rerun()

# bus stop sub-selector
from_stop = None
bus_stops = get_bus_stops(origin) if origin != NONE else []
if bus_stops:
    sids = [None] + [s["id"] for s in bus_stops]
    slabels = [t("all_stops", lang)] + [t_place(s["name"], lang) for s in bus_stops]
    si = st.selectbox(t("bus_stop_label", lang), range(len(sids)), index=0,
                      format_func=lambda i: slabels[i], key="bs")
    from_stop = sids[si]

# SVG map — viewBox 300x70, nodes at x=45/150/255, r=14
MX = {"豊中キャンパス": 45, "箕面キャンパス": 150, "吹田キャンパス": 255}
CY, R = 36, 14
has_origin = origin != NONE
has_dest = destination != NONE

# theme-aware SVG colors (CSS var() doesn't work inside SVG attributes)
_from_text = "#c4b5fd" if is_dark else "#7c3aed"
_to_text = "#6ee7b7" if is_dark else "#059669"
_node_dim = "#64748b" if is_dark else "#64748b"
_node_bg = "rgba(255,255,255,.02)" if is_dark else "rgba(0,0,0,.03)"
_node_border = "rgba(255,255,255,.1)" if is_dark else "rgba(0,0,0,.12)"
_rail_color = "rgba(255,255,255,.05)" if is_dark else "rgba(0,0,0,.08)"

nodes_svg = ""
for c in MAP_ORDER:
    cx = MX[c]
    em, nm = CAMPUS_EMOJI[c], _s(c)
    if has_origin and c == origin:
        nodes_svg += (
            f'<circle cx="{cx}" cy="{CY}" r="{R}" fill="none" stroke="#a78bfa" stroke-width=".8" opacity=".3">'
            f'<animate attributeName="r" values="{R};{R+8};{R}" dur="2.5s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".3;0;.3" dur="2.5s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{cx}" cy="{CY}" r="{R}" fill="rgba(167,139,250,.1)" stroke="#a78bfa" stroke-width="1.5"'
            f' style="filter:drop-shadow(0 0 4px rgba(167,139,250,.4))"/>'
            f'<text x="{cx}" y="{CY+3}" text-anchor="middle" font-size="11">{em}</text>'
            f'<text x="{cx}" y="{CY+R+10}" text-anchor="middle" font-size="7" font-weight="700" fill="{_from_text}">{nm}</text>'
            f'<text x="{cx}" y="{CY-R-4}" text-anchor="middle" font-size="6.5" font-weight="800" fill="{_from_text}">\U0001F4CD {HERE[lang]}</text>'
        )
    elif has_dest and c == destination:
        nodes_svg += (
            f'<circle cx="{cx}" cy="{CY}" r="{R}" fill="rgba(52,211,153,.1)" stroke="#34d399" stroke-width="1.5"'
            f' style="filter:drop-shadow(0 0 4px rgba(52,211,153,.4))"/>'
            f'<text x="{cx}" y="{CY+3}" text-anchor="middle" font-size="11">{em}</text>'
            f'<text x="{cx}" y="{CY+R+10}" text-anchor="middle" font-size="7" font-weight="700" fill="{_to_text}">{nm}</text>'
            f'<text x="{cx}" y="{CY-R-4}" text-anchor="middle" font-size="6.5" font-weight="800" fill="{_to_text}">\U0001F3AF {GOAL[lang]}</text>'
        )
    else:
        nodes_svg += (
            f'<circle cx="{cx}" cy="{CY}" r="{R}" fill="{_node_bg}" stroke="{_node_border}" stroke-width="1"/>'
            f'<text x="{cx}" y="{CY+3}" text-anchor="middle" font-size="11">{em}</text>'
            f'<text x="{cx}" y="{CY+R+10}" text-anchor="middle" font-size="7" font-weight="600" fill="{_node_dim}">{nm}</text>'
        )

# arrow (only when both selected)
arrow_svg = ""
if has_origin and has_dest:
    ox, dx = MX[origin], MX[destination]
    asx = ox + (R + 2 if dx > ox else -(R + 2))
    aex = dx + (-(R + 2) if dx > ox else (R + 2))
    arrow_svg = (
        f'<defs><marker id="ah" markerWidth="6" markerHeight="4" refX="5" refY="2" orient="auto">'
        f'<polygon points="0 0,6 2,0 4" fill="#818cf8"/></marker></defs>'
        f'<line x1="{asx}" y1="{CY}" x2="{aex}" y2="{CY}" stroke="#818cf8" stroke-width="1.5" '
        f'stroke-dasharray="5,3" marker-end="url(#ah)" opacity=".6">'
        f'<animate attributeName="stroke-dashoffset" values="16;0" dur="1.2s" repeatCount="indefinite"/></line>'
    )

svg = (
    f'<svg viewBox="0 0 300 70" style="width:100%;max-width:520px;display:block;margin:.3rem auto;">'
    f'<line x1="45" y1="{CY}" x2="255" y2="{CY}" stroke="{_rail_color}" stroke-width="1" stroke-dasharray="4,3"/>'
    f'{arrow_svg}{nodes_svg}</svg>'
)
st.markdown(svg, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================================================================== #
#  Section 2 — Time & options
# ================================================================== #
sec2_title = "出発時刻" if lang == "ja" else "DEPARTURE TIME"
st.markdown(f'<div class="sec sec-time"><div class="sec-title"><span class="sec-title-icon">\u23F0</span>{sec2_title}</div>', unsafe_allow_html=True)

use_now = st.checkbox(t("depart_now", lang), value=True)
if use_now:
    depart_time = datetime.now().replace(second=0, microsecond=0)
    st.markdown(
        f'<span style="color:var(--purple);font-weight:700;font-size:1.4rem;">'
        f'{depart_time.strftime("%H:%M")}</span>',
        unsafe_allow_html=True,
    )
else:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        d_date = st.date_input(t("date_label", lang), value=date.today())
    now = datetime.now()
    with c2:
        d_h = st.selectbox("H", range(24), index=now.hour,
                            format_func=lambda h: f"{h:02d}", key="sh")
    with c3:
        d_m = st.selectbox("M", range(60), index=now.minute,
                            format_func=lambda m: f"{m:02d}", key="sm")
    depart_time = datetime.combine(d_date, time(d_h, d_m))

suspended, suspend_reason = is_shuttle_suspended(depart_time.date())
if suspended:
    st.markdown(
        f'<span class="pill pill-off">\U0001F6AB {t_reason(suspend_reason, lang)}</span>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<span class="pill pill-ok">{t("shuttle_running", lang)}</span>',
        unsafe_allow_html=True,
    )

force_no_bus = st.checkbox(t("exclude_bus", lang), value=False)
shuttle_available = (not suspended) and (not force_no_bus)

st.markdown('</div>', unsafe_allow_html=True)

# ================================================================== #
#  Search button
# ================================================================== #
if origin == NONE or destination == NONE:
    hint = "現在地と行き先を選択してください" if lang == "ja" else "Select your origin and destination above"
    st.info(hint)
    st.stop()

if origin == destination:
    st.warning(t("same_campus", lang))
    st.stop()

if not st.button(t("search_btn", lang), type="primary", use_container_width=True):
    st.stop()

# ================================================================== #
#  Results
# ================================================================== #
with st.spinner(t("searching", lang)):
    results = search_routes(origin, destination, depart_time,
                            shuttle_available=shuttle_available, from_stop=from_stop)

if not suspended and not force_no_bus:
    status, _ = get_shuttle_status(origin, destination, depart_time)
    if status == "ended":
        last = get_shuttle_last_time(origin, destination)
        st.warning(t("bus_ended", lang, last=f"（{last}）" if last else ""))
    elif status == "none":
        st.info(t("no_direct_bus", lang))

if not results:
    st.error(t("no_route", lang))
    st.stop()

if results[0].get("next_morning"):
    st.info(t("next_morning", lang))

ICONS = {"徒歩": "\U0001F6B6", "学内バス": "\U0001F68C",
         "大阪モノレール": "\U0001F69D", "阪急宝塚線": "\U0001F683",
         "阪急千里線": "\U0001F683", "北大阪急行": "\U0001F687",
         "阪急バス": "\U0001F68D"}
um, uy = t("min", lang), t("yen", lang)
route_word = "ルート" if lang == "ja" else "Route"

def _ic(tr):
    for k, v in ICONS.items():
        if k in tr:
            return v
    return "\U0001F68B"

COLORS = ["#a78bfa", "#38bdf8", "#34d399", "#fbbf24"]

for route in results:
    rn = route["route_number"]
    d0 = route["segments"][0]["depart"]
    a0 = route["segments"][-1]["arrive"]
    f0 = route["fare"]
    fare_str = f"\u2728 {t('free_label', lang)}" if f0 == 0 else f"{f0}{uy}"
    accent = COLORS[(rn - 1) % len(COLORS)]

    icons_summary = " \u2192 ".join(
        _ic(s["transport"]) for s in route["segments"] if s["transport"] != "徒歩"
    )

    # build card HTML
    steps = ""
    for s in route["segments"]:
        tn = t_transport(s["transport"], lang)
        fn = t_place(s["from"], lang)
        ton = t_place(s["to"], lang)
        ic = _ic(s["transport"])
        if s["transport"] == "徒歩":
            chip = ""
        elif s["fare"] == 0:
            chip = ' <span style="background:linear-gradient(135deg,var(--gold),#f59e0b);color:var(--pill-free-text);font-weight:900;font-size:.7rem;padding:.05rem .4rem;border-radius:999px;">FREE</span>'
        else:
            chip = f' <span style="background:var(--chip-paid-bg);color:var(--chip-paid-text);font-weight:700;font-size:.7rem;padding:.05rem .4rem;border-radius:999px;">{s["fare"]}{uy}</span>'
        steps += (
            f'<div style="padding:.25rem 0;">'
            f'<span style="font-weight:700;font-size:.9rem;color:var(--text);">{ic} {tn}</span>{chip}<br>'
            f'<span style="font-size:.8rem;color:var(--muted);">'
            f'\u2003{fn} {s["depart"]} \u2192 {ton} {s["arrive"]} \u00B7 {s["duration_min"]}{um}</span>'
            f'</div>'
        )

    card = (
        f'<div style="border-left:4px solid {accent};border-radius:14px;'
        f'padding:1rem 1.2rem;margin-bottom:.8rem;'
        f'background:var(--card);border:1px solid var(--border);'
        f'border-left:4px solid {accent};">'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:.3rem;margin-bottom:.5rem;">'
        f'<span style="font-size:1.1rem;font-weight:900;color:{accent};">{route_word} {rn}\u2003{icons_summary}</span>'
        f'<span style="font-size:.85rem;font-weight:700;color:var(--rsum-paid);">{fare_str}</span>'
        f'</div>'
        f'<div style="font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:.4rem;">'
        f'{d0} \u2192 {a0}\u2003\u00B7\u2003{route["duration_min"]}{um}</div>'
        f'{steps}</div>'
    )
    st.markdown(card, unsafe_allow_html=True)

updated = "最終更新: 2025/4/1" if lang == "ja" else "Last updated: 2025/4/1"
st.markdown(
    f'<div class="ft">{t("footer", lang)}<br>{updated}</div>',
    unsafe_allow_html=True,
)
