import streamlit as st
import base64
import re
import html as _html
from agent import index_documents, build_agent

# ─────────────────────────────────────────────────────────────────────────────
# SVG ICONS
# ─────────────────────────────────────────────────────────────────────────────

def _b64(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


_AVATAR_USER = _b64(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="16" fill="#4f46e5"/>'
    '<path d="M16 8a5 5 0 1 1 0 10A5 5 0 0 1 16 8zm0 12c5.52 0 10 2.24 10 5v2H6v-2c0-2.76 4.48-5 10-5z" fill="white"/>'
    '</svg>'
)

_AVATAR_BOT = _b64(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">'
    '<stop offset="0%" stop-color="#4f46e5"/>'
    '<stop offset="100%" stop-color="#7c3aed"/>'
    '</linearGradient></defs>'
    '<rect width="32" height="32" rx="16" fill="url(#g)"/>'
    '<rect x="7" y="11" width="18" height="13" rx="3" fill="none" stroke="white" stroke-width="1.5"/>'
    '<circle cx="11.5" cy="17.5" r="1.5" fill="white"/>'
    '<circle cx="20.5" cy="17.5" r="1.5" fill="white"/>'
    '<line x1="16" y1="7" x2="16" y2="11" stroke="white" stroke-width="1.5" stroke-linecap="round"/>'
    '<circle cx="16" cy="6" r="1.5" fill="white"/>'
    '</svg>'
)

_ICO_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"'
    ' aria-hidden="true" focusable="false"'
    ' fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
    '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
    '<polyline points="2 17 12 22 22 17"/>'
    '<polyline points="2 12 12 17 22 12"/>'
    '</svg>'
)

_ICO_DB = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24"'
    ' aria-hidden="true" focusable="false"'
    ' fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
    '<path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>'
    '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'
    '</svg>'
)

_ICO_GLOBE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24"'
    ' aria-hidden="true" focusable="false"'
    ' fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="10"/>'
    '<line x1="2" y1="12" x2="22" y2="12"/>'
    '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
    '</svg>'
)

_ICO_BRAIN = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"'
    ' aria-hidden="true" focusable="false"'
    ' fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08'
    ' 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>'
    '<path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08'
    ' 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>'
    '</svg>'
)

_ICO_ZAPS = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"'
    ' aria-hidden="true" focusable="false"'
    ' fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
    '</svg>'
)

_ICO_LAYERS = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"'
    ' aria-hidden="true" focusable="false"'
    ' fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
    '<polyline points="2 17 12 22 22 17"/>'
    '<polyline points="2 12 12 17 22 12"/>'
    '</svg>'
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

*, *::before, *::after {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
}

/* ── Hide Streamlit chrome ───────────────────────────────────────────────── */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

header[data-testid="stHeader"] {
    background: transparent !important;
}
/* ── Background ─────────────────────────────────────────────────────────── */
.stApp {
    background-color: #f3f4ff;
    background-image:
        radial-gradient(ellipse 65% 55% at 10% 15%, rgba(99,102,241,.13) 0%, transparent 70%),
        radial-gradient(ellipse 55% 65% at 90% 85%, rgba(124,58,237,.11) 0%, transparent 70%),
        radial-gradient(ellipse 45% 45% at 65% 10%, rgba(79,70,229,.07)  0%, transparent 70%);
    background-attachment: fixed;
}

/* ── Layout ─────────────────────────────────────────────────────────────── */
.main .block-container {
    max-width: 820px !important;
    padding-top: 0 !important;
    padding-bottom: 7rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────  */
[data-testid="stSidebar"] > div:first-child {
    background: rgba(255,255,255,.62) !important;
    backdrop-filter: blur(24px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
    border-right: 1px solid rgba(99,102,241,.1) !important;
    box-shadow: 4px 0 32px rgba(79,70,229,.05) !important;
}

/* Force sidebar always visible - hide all toggle/collapse buttons */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { display: none !important; }

/* Force sidebar to stay on screen even when Streamlit marks it as collapsed */
[data-testid="stSidebar"] {
    transform: none !important;
    margin-left: 0 !important;
    min-width: 290px !important;
    width: 290px !important;
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
}

/* ── Chat messages ────────────────────────────────────────────────────────  */
[data-testid="stChatMessage"] {
    animation: msgIn .4s cubic-bezier(.16,1,.3,1) both;
    padding: .25rem 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatMessageContent"] {
    border-radius: 2px 16px 16px 16px !important;
    background: rgba(255,255,255,.84) !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
    border: 1px solid rgba(99,102,241,.1) !important;
    box-shadow: 0 2px 20px rgba(0,0,0,.04), 0 1px 4px rgba(99,102,241,.06) !important;
    padding: .875rem 1.125rem !important;
}
@keyframes msgIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Chat input ───────────────────────────────────────────────────────────  */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,.9) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1.5px solid rgba(99,102,241,.18) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 48px rgba(79,70,229,.12), 0 2px 8px rgba(0,0,0,.03) !important;
    transition: border-color .25s, box-shadow .25s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 8px 48px rgba(79,70,229,.2), 0 0 0 3px rgba(99,102,241,.1) !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────  */
.stButton > button {
    background: rgba(255,255,255,.78) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1.5px solid rgba(99,102,241,.18) !important;
    border-radius: 10px !important;
    color: #4f46e5 !important;
    font-size: .78rem !important;
    font-weight: 500 !important;
    letter-spacing: .005em !important;
    transition: all .2s cubic-bezier(.16,1,.3,1) !important;
    box-shadow: 0 1px 6px rgba(99,102,241,.07) !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,.06) !important;
    border-color: #6366f1 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(99,102,241,.16) !important;
}
.stButton > button:active { transform: translateY(0) scale(.98) !important; }

/* ── Misc ─────────────────────────────────────────────────────────────────  */
hr { border: none !important; border-top: 1px solid rgba(99,102,241,.08) !important; margin: 1rem 0 !important; }
h1,h2,h3,h4 { color: #0f172a !important; letter-spacing: -.02em !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,.22); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,.42); }

/* ── Header ───────────────────────────────────────────────────────────────  */
.nx-header {
    display: flex; align-items: center; gap: .875rem;
    padding: 1rem 0; margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(99,102,241,.1);
}
.nx-logo {
    width: 40px; height: 40px; border-radius: 11px; flex-shrink: 0;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 16px rgba(79,70,229,.4), inset 0 1px 0 rgba(255,255,255,.15);
}
.nx-brand { flex: 1; }
.nx-name {
    font-size: 1.1rem; font-weight: 800; letter-spacing: -.035em; line-height: 1.1;
    background: linear-gradient(130deg, #3730a3 0%, #6d28d9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.nx-tag { font-size: .7rem; color: #94a3b8; font-weight: 400; letter-spacing: .01em; margin-top: 3px; }
.nx-online { display: flex; align-items: center; gap: 5px; font-size: .68rem; color: #10b981; font-weight: 500; }
.nx-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #10b981;
    animation: statusPulse 2s ease-in-out infinite;
}
@keyframes statusPulse {
    0%,100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,.4); }
    50%      { opacity: .7; box-shadow: 0 0 0 4px rgba(16,185,129,0); }
}

/* ── Agent trace ──────────────────────────────────────────────────────────  */
.nx-trace {
    margin: .5rem 0 .625rem 3.25rem;
    animation: traceIn .35s cubic-bezier(.16,1,.3,1) both;
}
@keyframes traceIn {
    from { opacity: 0; transform: translateY(6px) scale(.985); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
.nx-trace-hdr {
    font-size: .6rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .11em; color: #94a3b8;
    display: flex; align-items: center; gap: 5px; margin-bottom: 6px;
}
.nx-step {
    position: relative;
    background: rgba(255,255,255,.72);
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(99,102,241,.1);
    border-left: 3px solid var(--c, #6366f1);
    border-radius: 2px 10px 10px 2px;
    padding: .75rem .875rem; margin-bottom: .4rem;
}
.nx-step-kb  { --c: #4f46e5; }
.nx-step-web { --c: #059669; }
.nx-step-hdr { display: flex; align-items: center; gap: .5rem; margin-bottom: .5rem; }
.nx-badge {
    display: inline-flex; align-items: center; gap: .3rem;
    padding: .2rem .55rem; border-radius: 20px;
    font-size: .68rem; font-weight: 600; letter-spacing: .02em;
}
.nx-badge-kb  { background: rgba(79,70,229,.09); color: #4f46e5; border: 1px solid rgba(79,70,229,.18); }
.nx-badge-web { background: rgba(5,150,105,.09);  color: #059669; border: 1px solid rgba(5,150,105,.18); }
.nx-step-n {
    font-size: .62rem; font-weight: 700; color: #94a3b8;
    background: rgba(148,163,184,.1); padding: .1rem .4rem; border-radius: 20px;
}
.nx-thought {
    font-size: .76rem; color: #475569; font-style: italic; line-height: 1.55;
    padding: .45rem .6rem; border-radius: 6px; margin-bottom: .45rem;
    background: rgba(248,250,252,.9); border-left: 2px solid rgba(99,102,241,.22);
}
.nx-qlbl {
    font-size: .59rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .09em; color: #94a3b8; margin-bottom: 3px;
}
.nx-q {
    font-family: 'SF Mono','Fira Code','Cascadia Code',ui-monospace,monospace !important;
    font-size: .73rem; color: #334155;
    background: rgba(241,245,249,.9); padding: .3rem .55rem; border-radius: 5px;
}

/* ── Thinking animation ───────────────────────────────────────────────────  */
.nx-thinking {
    display: flex; align-items: center; gap: .625rem;
    padding: .75rem .875rem; margin: .5rem 0 .5rem 3.25rem;
    background: rgba(255,255,255,.65);
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(99,102,241,.1); border-radius: 10px;
    animation: traceIn .3s ease both;
}
.nx-thinking-txt { font-size: .76rem; color: #64748b; font-weight: 500; }
.nx-dots { display: flex; gap: 3px; align-items: center; }
.nx-dots span {
    width: 5px; height: 5px; border-radius: 50%; background: #6366f1; display: block;
    animation: dotB 1.4s ease-in-out infinite;
}
.nx-dots span:nth-child(2) { animation-delay: .17s; }
.nx-dots span:nth-child(3) { animation-delay: .34s; }
@keyframes dotB {
    0%,80%,100% { transform: scale(.5); opacity: .3; }
    40%         { transform: scale(1);  opacity: 1;  }
}

/* ── Empty state ──────────────────────────────────────────────────────────  */
.nx-empty {
    text-align: center; padding: 2.5rem 1rem 1.5rem;
    animation: fadeIn .6s ease both;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.nx-empty-logo {
    width: 52px; height: 52px; border-radius: 15px; margin: 0 auto 1rem;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 28px rgba(79,70,229,.32), inset 0 1px 0 rgba(255,255,255,.15);
}
.nx-empty-h   { font-size: 1.25rem; font-weight: 800; color: #0f172a; letter-spacing: -.035em; margin-bottom: .5rem; }
.nx-empty-sub { font-size: .82rem; color: #64748b; max-width: 340px; margin: 0 auto; line-height: 1.65; }

/* ── Example label ────────────────────────────────────────────────────────  */
.nx-ex-lbl {
    font-size: .62rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: .1em; color: #94a3b8; margin-bottom: .5rem;
}

/* ── Sidebar components ───────────────────────────────────────────────────  */
.nx-sb-section {
    background: rgba(255,255,255,.5);
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(99,102,241,.09); border-radius: 11px;
    padding: .875rem; margin-bottom: .625rem;
}
.nx-sb-lbl {
    font-size: .6rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .11em; color: #6366f1;
    display: flex; align-items: center; gap: 5px; margin-bottom: .625rem;
}
.nx-flow-item { display: flex; gap: .5rem; align-items: flex-start; padding: .25rem 0; }
.nx-flow-num {
    width: 18px; height: 18px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white; font-size: .6rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; margin-top: 1px;
}
.nx-flow-txt { font-size: .73rem; color: #475569; line-height: 1.5; }
.nx-tool-row {
    display: flex; align-items: flex-start; gap: .5rem;
    padding: .4rem 0; border-bottom: 1px solid rgba(99,102,241,.06);
}
.nx-tool-row:last-child { border-bottom: none; }
.nx-tool-ic {
    width: 26px; height: 26px; border-radius: 6px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
}
.nx-tool-ic-kb  { background: rgba(79,70,229,.1); color: #4f46e5; }
.nx-tool-ic-web { background: rgba(5,150,105,.1);  color: #059669; }
.nx-tool-nm { font-size: .75rem; font-weight: 600; color: #0f172a; line-height: 1.3; }
.nx-tool-ds { font-size: .68rem; color: #64748b; line-height: 1.4; margin-top: 1px; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_thought(log: str) -> str:
    m = re.match(r"Thought:\s*(.*?)(?:\nAction:|\Z)", log, re.DOTALL | re.IGNORECASE)
    if m:
        t = m.group(1).strip()
        if t:
            return t
    for line in log.split("\n"):
        line = line.strip()
        if line and not line.lower().startswith(("action", "observation")):
            return line.replace("Thought:", "").strip()
    return ""


def _render_trace(steps: list) -> str:
    if not steps:
        return ""
    parts = [
        f'<div class="nx-trace">'
        f'<div class="nx-trace-hdr">{_ICO_BRAIN} Agent Reasoning</div>'
    ]
    for i, (action, _obs) in enumerate(steps, 1):
        tool = action.tool
        query = str(action.tool_input)
        thought = _extract_thought(action.log)
        is_kb = tool == "KnowledgeBase"
        step_cls  = "nx-step-kb"   if is_kb else "nx-step-web"
        badge_cls = "nx-badge-kb"  if is_kb else "nx-badge-web"
        icon  = _ICO_DB    if is_kb else _ICO_GLOBE
        label = "Knowledge Base" if is_kb else "Web Search"
        thought_html = (
            f'<div class="nx-thought">{_html.escape(thought)}</div>' if thought else ""
        )
        parts.append(
            f'<div class="nx-step {step_cls}">'
            f'<div class="nx-step-hdr">'
            f'<span class="nx-step-n">Step {i}</span>'
            f'<span class="nx-badge {badge_cls}">{icon} {label}</span>'
            f'</div>'
            f'{thought_html}'
            f'<div class="nx-qlbl">Query</div>'
            f'<div class="nx-q">{_html.escape(query)}</div>'
            f'</div>'
        )
    parts.append("</div>")
    return "".join(parts)


_THINKING_HTML = (
    '<div class="nx-thinking">'
    '<div class="nx-dots"><span></span><span></span><span></span></div>'
    '<span class="nx-thinking-txt">Analyzing and selecting tools\u2026</span>'
    '</div>'
)

_HEADER_HTML = f"""
<div class="nx-header">
    <div class="nx-logo">{_ICO_LOGO}</div>
    <div class="nx-brand">
        <div class="nx-name">Meridian Analytics Intelligence Assistant</div>
        <div class="nx-tag">Internal knowledge and live market intelligence — one conversation</div>
    </div>
    <div class="nx-online"><div class="nx-dot"></div>Online</div>
</div>
"""

_EMPTY_HTML = f"""
<div class="nx-empty">
    <div class="nx-empty-logo">{_ICO_LOGO}</div>
    <div class="nx-empty-h">Ask Meridian Intelligence</div>
    <div class="nx-empty-sub">
        I'll search your internal Meridian Analytics knowledge base and the live web,
        choosing the right source for every question.
    </div>
</div>
"""

_SIDEBAR_HTML = f"""
<div class="nx-sb-section">
    <div class="nx-sb-lbl">{_ICO_ZAPS} How It Works</div>
    <div class="nx-flow-item"><div class="nx-flow-num">1</div><div class="nx-flow-txt"><strong>Reason</strong> — evaluate what kind of question it is</div></div>
    <div class="nx-flow-item"><div class="nx-flow-num">2</div><div class="nx-flow-txt"><strong>Route</strong> — choose the best tool for the job</div></div>
    <div class="nx-flow-item"><div class="nx-flow-num">3</div><div class="nx-flow-txt"><strong>Retrieve</strong> — query internal docs or the live web</div></div>
    <div class="nx-flow-item"><div class="nx-flow-num">4</div><div class="nx-flow-txt"><strong>Respond</strong> — synthesize a grounded answer</div></div>
</div>
<div class="nx-sb-section">
    <div class="nx-sb-lbl">{_ICO_LAYERS} Available Tools</div>
    <div class="nx-tool-row">
        <div class="nx-tool-ic nx-tool-ic-kb">{_ICO_DB}</div>
        <div>
            <div class="nx-tool-nm">Knowledge Base</div>
            <div class="nx-tool-ds">Internal Meridian Analytics docs, strategies, project briefs, and org knowledge</div>
        </div>
    </div>
    <div class="nx-tool-row">
        <div class="nx-tool-ic nx-tool-ic-web">{_ICO_GLOBE}</div>
        <div>
            <div class="nx-tool-nm">Web Search</div>
            <div class="nx-tool-ds">Live market intelligence, industry news, competitive landscape</div>
        </div>
    </div>
</div>
<div class="nx-sb-section">
    <div class="nx-sb-lbl">{_ICO_BRAIN} Built For</div>
    <div class="nx-flow-txt" style="font-size:.73rem;color:#475569;line-height:1.6;">
        Operations, strategy, and consulting teams who need instant access to internal knowledge
        and live market intelligence — without switching tools.
    </div>
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Meridian Analytics Intelligence Assistant",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _init():
    index_documents()
    return build_agent()


with st.spinner("Initializing Meridian Analytics Intelligence Assistant..."):
    agent = _init()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(_SIDEBAR_HTML, unsafe_allow_html=True)
    if st.session_state.get("messages"):
        st.markdown("---")
        if st.button("Clear conversation"):
            st.session_state.messages = []
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(_HEADER_HTML, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Empty state
if not st.session_state.messages:
    st.markdown(_EMPTY_HTML, unsafe_allow_html=True)

# Example questions
st.markdown('<div class="nx-ex-lbl">Try asking</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Who are Meridian's top competitors?"):
        st.session_state.pending_query = "Who are Meridian's top competitors?"
with c2:
    if st.button("What is Project Lighthouse?"):
        st.session_state.pending_query = "What is Project Lighthouse?"
with c3:
    if st.button("Latest trends in enterprise healthcare AI?"):
        st.session_state.pending_query = "What are the latest trends in enterprise healthcare AI?"

# Chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=_AVATAR_USER):
            st.markdown(msg["content"])
    else:
        if msg.get("steps"):
            st.markdown(_render_trace(msg["steps"]), unsafe_allow_html=True)
        with st.chat_message("assistant", avatar=_AVATAR_BOT):
            st.markdown(msg["content"])

# Input
query = st.chat_input("Ask anything — I'll find it in our knowledge base or the web...")

# Handle example button clicks
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

if query:
    with st.chat_message("user", avatar=_AVATAR_USER):
        st.markdown(query)

    thinking_slot = st.empty()
    thinking_slot.markdown(_THINKING_HTML, unsafe_allow_html=True)

    try:
        result = agent.invoke({"input": query})
        answer = result.get("output", "I could not generate a response.")
        steps = result.get("intermediate_steps", [])
    except Exception as e:
        answer = f"An error occurred: {str(e)}"
        steps = []

    thinking_slot.empty()
    if steps:
        thinking_slot.markdown(_render_trace(steps), unsafe_allow_html=True)

    with st.chat_message("assistant", avatar=_AVATAR_BOT):
        st.markdown(answer)

    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({"role": "assistant", "content": answer, "steps": steps})
