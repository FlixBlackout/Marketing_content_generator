import streamlit as st
from vector_store import search
from replicate_llm import generate_marketing_image
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="AI Fashion Marketing Generator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state ─────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    # Each entry: { "path": str, "prompt": str, "time": str }
    st.session_state.history = []
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 0


# ── Theme CSS ─────────────────────────────────────────────────────────────────
def inject_css(dark: bool):
    if dark:
        bg_base     = "#0d0f14"
        bg_panel    = "#11141c"
        bg_card     = "#181c27"
        bg_input    = "#1d2130"
        border      = "#252b3b"
        text_1      = "#e8ecf4"
        text_2      = "#7d8799"
        text_3      = "#4a5166"
        accent      = "#3d8ef8"
        accent2     = "#7b5af0"
        accent_glow = "#3d8ef825"
        success     = "#2dd4a0"
        success_bg  = "#182b22"
        sb_bg       = "#0e1018"
        sb_border   = "#1e2233"
        hist_hover  = "#1d2130"
        hist_active = "#1a2340"
        hist_active_border = "#3d8ef8"
        scrollbar   = "#252b3b"
    else:
        bg_base     = "#f0f2f8"
        bg_panel    = "#ffffff"
        bg_card     = "#f5f7fc"
        bg_input    = "#eaedf5"
        border      = "#dce0ec"
        text_1      = "#191c28"
        text_2      = "#5a6075"
        text_3      = "#9ba3b8"
        accent      = "#2f7ef5"
        accent2     = "#6b47e8"
        accent_glow = "#2f7ef518"
        success     = "#1db887"
        success_bg  = "#e8faf4"
        sb_bg       = "#f8f9fd"
        sb_border   = "#dce0ec"
        hist_hover  = "#eef0f8"
        hist_active = "#e8effe"
        hist_active_border = "#2f7ef5"
        scrollbar   = "#dce0ec"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {{
    --bg-base:     {bg_base};
    --bg-panel:    {bg_panel};
    --bg-card:     {bg_card};
    --bg-input:    {bg_input};
    --border:      {border};
    --text-1:      {text_1};
    --text-2:      {text_2};
    --text-3:      {text_3};
    --accent:      {accent};
    --accent2:     {accent2};
    --accent-glow: {accent_glow};
    --success:     {success};
    --sb-bg:       {sb_bg};
    --sb-border:   {sb_border};
    --hist-hover:  {hist_hover};
    --hist-active: {hist_active};
    --hist-active-border: {hist_active_border};
}}

/* ── Base reset ── */
html, body, [class*="css"], .stApp {{
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-1) !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── Hide sidebar collapse/expand arrow button ── */
button[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] button[data-testid="baseButton-header"] {{
    display: none !important;
}}

/* ── Keep sidebar always open ── */
section[data-testid="stSidebar"][aria-expanded="false"] {{
    display: flex !important;
    transform: none !important;
    width: 300px !important;
    min-width: 300px !important;
    margin-left: 0 !important;
}}

/* ── Main content padding ── */
.block-container {{
    padding: 28px 36px 36px !important;
    max-width: 100% !important;
}}

/* ══════════════════════════════════════
   SIDEBAR — History Panel
══════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
    min-width: 300px !important;
    max-width: 300px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}

/* Sidebar inner wrapper */
.sb-inner {{
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}}

/* Sidebar top header */
.sb-header {{
    padding: 20px 18px 14px;
    border-bottom: 1px solid var(--sb-border);
    background: var(--sb-bg);
    position: sticky;
    top: 0;
    z-index: 10;
}}
.sb-header-title {{
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 800;
    color: var(--text-1);
    letter-spacing: .02em;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
}}
.sb-header-sub {{
    font-size: 11px;
    color: var(--text-3);
    letter-spacing: .01em;
}}
.sb-count-badge {{
    background: var(--accent);
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 800;
    border-radius: 20px;
    padding: 2px 8px;
    min-width: 22px;
    text-align: center;
}}

/* History scroll area */
.sb-scroll {{
    flex: 1;
    overflow-y: auto;
    padding: 10px 12px;
}}
.sb-scroll::-webkit-scrollbar {{ width: 3px; }}
.sb-scroll::-webkit-scrollbar-track {{ background: transparent; }}
.sb-scroll::-webkit-scrollbar-thumb {{ background: var(--sb-border); border-radius: 99px; }}

/* History date group label */
.hist-date-label {{
    font-family: 'Syne', sans-serif;
    font-size: 9.5px;
    font-weight: 700;
    color: var(--text-3);
    letter-spacing: .1em;
    text-transform: uppercase;
    padding: 10px 6px 4px;
}}

/* History item card */
.hist-item {{
    display: flex;
    gap: 10px;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid transparent;
    cursor: pointer;
    margin-bottom: 4px;
    transition: background .15s, border-color .15s;
    background: transparent;
    text-decoration: none;
}}
.hist-item:hover {{
    background: var(--hist-hover);
    border-color: var(--border);
}}
.hist-item.active {{
    background: var(--hist-active);
    border-color: var(--hist-active-border);
}}
.hist-thumb {{
    width: 62px;
    height: 62px;
    border-radius: 8px;
    object-fit: cover;
    flex-shrink: 0;
    border: 1px solid var(--border);
    background: var(--bg-card);
}}
.hist-thumb-placeholder {{
    width: 62px;
    height: 62px;
    border-radius: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    opacity: .4;
    flex-shrink: 0;
}}
.hist-meta {{
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 3px;
}}
.hist-prompt {{
    font-size: 12px;
    font-weight: 500;
    color: var(--text-1);
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}}
.hist-time {{
    font-size: 10.5px;
    color: var(--text-3);
    display: flex;
    align-items: center;
    gap: 4px;
}}
.hist-accent-dot {{
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
}}

/* Empty history state */
.hist-empty {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 40px 20px;
    color: var(--text-3);
    text-align: center;
}}
.hist-empty-icon {{ font-size: 36px; opacity: .25; }}
.hist-empty-text {{ font-size: 12px; line-height: 1.6; }}

/* Sidebar bottom: clear button area */
.sb-footer {{
    padding: 12px 14px;
    border-top: 1px solid var(--sb-border);
}}

/* ══════════════════════════════════════
   MAIN AREA
══════════════════════════════════════ */

/* Page header */
.page-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    padding-bottom: 18px;
    border-bottom: 1px solid var(--border);
}}
.page-title {{
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: var(--text-1);
    display: flex;
    align-items: center;
    gap: 10px;
}}
.page-tag {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'Syne', sans-serif;
    font-size: 10.5px;
    font-weight: 700;
    color: {accent};
    letter-spacing: .05em;
}}
.status-pill {{
    display: flex;
    align-items: center;
    gap: 7px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 12px;
    color: var(--text-2);
}}
.status-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: {success};
    box-shadow: 0 0 7px {success};
}}

/* Text area */
.stTextArea textarea {{
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 14px 18px !important;
    transition: border-color .2s, box-shadow .2s !important;
    resize: none !important;
}}
.stTextArea textarea:focus {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 3px {accent_glow} !important;
    outline: none !important;
}}
.stTextArea textarea::placeholder {{ color: var(--text-3) !important; }}
.stTextArea label {{
    color: var(--text-3) !important;
    font-size: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: .09em !important;
    text-transform: uppercase !important;
    margin-bottom: 7px !important;
}}

/* Generate button */
.stButton > button {{
    background: linear-gradient(135deg, {accent} 0%, {accent2} 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 11px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: .05em !important;
    padding: 11px 28px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: opacity .2s, transform .15s, box-shadow .2s !important;
}}
.stButton > button:hover {{
    opacity: .85 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 30px {accent_glow} !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* Download button */
.stDownloadButton > button {{
    background: var(--bg-card) !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 11px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: border-color .2s, color .2s !important;
}}
.stDownloadButton > button:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
}}

/* Toggle */
.stToggle > label {{
    color: var(--text-2) !important;
    font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* Images */
.stImage img {{
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    width: 100% !important;
}}
.img-frame-glow {{
    border-radius: 14px;
    overflow: hidden;
    border: 1.5px solid {accent};
    box-shadow: 0 0 0 3px {accent_glow}, 0 20px 56px #00000022;
    margin-bottom: 20px;
}}
.img-frame-glow .stImage img {{
    border-radius: 12px !important;
    border: none !important;
}}

/* Empty canvas */
.empty-canvas {{
    border-radius: 14px;
    border: 1.5px dashed var(--border);
    background: var(--bg-card);
    min-height: 360px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--text-3);
    margin-bottom: 22px;
}}

/* Section label */
.section-label {{
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: var(--text-3);
    letter-spacing: .1em;
    text-transform: uppercase;
    margin: 6px 0 12px 0;
}}

/* Thumbnail grid cards */
.variant-wrap {{
    border-radius: 11px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: var(--bg-card);
    transition: border-color .2s, box-shadow .2s;
    margin-bottom: 4px;
}}
.variant-wrap:hover {{
    border-color: {accent};
    box-shadow: 0 0 0 2px {accent_glow};
}}
.variant-wrap.v-active {{
    border-color: {accent};
    box-shadow: 0 0 0 2px {accent_glow};
}}
.thumb-placeholder {{
    aspect-ratio: 16/9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    opacity: .16;
    padding: 18px;
}}

/* Caption */
.stCaption {{
    color: var(--text-3) !important;
    font-size: 11px !important;
    text-align: center !important;
    margin-top: 4px !important;
}}

/* Alerts */
div[data-testid="stAlert"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 11px !important;
}}
div[data-testid="stSuccess"] {{
    background: {success_bg} !important;
    border: 1px solid {success} !important;
    border-radius: 11px !important;
}}
div[data-testid="stSuccess"] p {{ color: {success} !important; }}

.stSpinner > div {{ border-top-color: {accent} !important; }}
hr {{ border-color: var(--border) !important; opacity: 1 !important; }}

::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {scrollbar}; border-radius: 99px; }}

[data-testid="column"] {{ padding: 0 6px !important; }}
</style>
""", unsafe_allow_html=True)

inject_css(st.session_state.dark_mode)


# ════════════════════════════════════════════════════════════════════
# SIDEBAR — IMAGE HISTORY PANEL
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    count = len(st.session_state.history)

    # Header
    st.markdown(f"""
    <div class="sb-header">
        <div class="sb-header-title">
            🗂 Generation History
            <span class="sb-count-badge">{count}</span>
        </div>
        <div class="sb-header-sub">Your previously created images</div>
    </div>
    """, unsafe_allow_html=True)

    if count == 0:
        st.markdown("""
        <div class="hist-empty">
            <div class="hist-empty-icon">🖼</div>
            <div class="hist-empty-text">
                No images generated yet.<br>
                Enter a prompt and hit <strong>Generate</strong> to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Group by date
        from collections import defaultdict
        groups = defaultdict(list)
        for idx, entry in enumerate(reversed(st.session_state.history)):
            real_idx = count - 1 - idx
            groups[entry["date"]].append((real_idx, entry))

        for date_label, items in groups.items():
            st.markdown(f'<div class="hist-date-label">{date_label}</div>', unsafe_allow_html=True)
            for real_idx, entry in items:
                is_active = (real_idx == st.session_state.selected_idx)
                active_cls = "active" if is_active else ""
                dot_html = '<span class="hist-accent-dot"></span>' if is_active else ""

                # Thumbnail: use actual image if it exists
                img_path = entry.get("path", "")
                if img_path and os.path.exists(img_path):
                    # Encode image to base64 for inline display
                    import base64
                    with open(img_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                    ext = os.path.splitext(img_path)[1].lstrip(".") or "png"
                    thumb_html = f'<img class="hist-thumb" src="data:image/{ext};base64,{b64}" />'
                else:
                    thumb_html = '<div class="hist-thumb-placeholder">👗</div>'

                prompt_short = entry["prompt"][:80] + ("…" if len(entry["prompt"]) > 80 else "")

                st.markdown(f"""
                <div class="hist-item {active_cls}" onclick="">
                    {thumb_html}
                    <div class="hist-meta">
                        <div class="hist-prompt">{prompt_short}</div>
                        <div class="hist-time">{dot_html} {entry["time"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Invisible button to handle selection
                if st.button("", key=f"sel_{real_idx}", help=f"View: {prompt_short}"):
                    st.session_state.selected_idx = real_idx
                    st.rerun()

        # Clear history button
        st.markdown("---")
        if st.button("🗑  Clear All History", key="clear_history"):
            st.session_state.history = []
            st.session_state.selected_idx = 0
            st.rerun()


# ════════════════════════════════════════════════════════════════════
# MAIN AREA
# ════════════════════════════════════════════════════════════════════

# Header
h_left, h_right = st.columns([3, 1])
with h_left:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding-top:2px;">
        <div class="page-title">👗 Fashion Marketing Studio</div>
        <span class="page-tag">AI · RAG</span>
        <div class="status-pill">
            <div class="status-dot"></div>
            Model ready
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_right:
    mode_icon  = "🌙" if st.session_state.dark_mode else "☀️"
    mode_label = f"{mode_icon}  {'Dark' if st.session_state.dark_mode else 'Light'} Mode"
    new_val = st.toggle(mode_label, value=st.session_state.dark_mode, key="theme_toggle")
    if new_val != st.session_state.dark_mode:
        st.session_state.dark_mode = new_val
        st.rerun()

st.markdown("---")

# ── Prompt + Generate ────────────────────────────────────────────────────────
user_query = st.text_area(
    "Marketing Request",
    placeholder="Example: Create an Instagram ad for summer women's dresses with 20% discount…",
    height=96,
    key="prompt_input",
    label_visibility="visible"
)

generate_button = st.button("⚡  Generate Marketing Image")

st.markdown("---")

# ── Canvas ───────────────────────────────────────────────────────────────────
if generate_button:
    if user_query.strip() == "":
        st.warning("⚠ Please enter a marketing request.")
    else:
        with st.spinner("Generating your marketing visual…"):
            try:
                retrieved_chunks = search(user_query)
                formatted_context = "\n\n".join(retrieved_chunks)

                final_prompt = f"""
You are a professional fashion marketing designer.

Brand Knowledge:
{formatted_context}

Create a high-quality Instagram marketing image for:
{user_query}

Requirements:
- 1080x1080 Instagram format
- Premium lighting
- Fashion editorial style
- Modern typography
- Clear CTA button
"""
                image_path = generate_marketing_image(final_prompt)

                # ── Save to history ──
                now = datetime.now()
                st.session_state.history.append({
                    "path":   image_path,
                    "prompt": user_query.strip(),
                    "time":   now.strftime("%I:%M %p"),
                    "date":   now.strftime("%b %d, %Y"),
                })
                st.session_state.selected_idx = len(st.session_state.history) - 1

                st.success("✅ Image generated successfully!")

                st.markdown('<div class="section-label">Generated Image</div>', unsafe_allow_html=True)
                st.markdown('<div class="img-frame-glow">', unsafe_allow_html=True)
                st.image(image_path, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                with open(image_path, "rb") as file:
                    st.download_button(
                        label="⬇  Download Image",
                        data=file,
                        file_name=os.path.basename(image_path),
                        mime="image/png"
                    )

            except Exception as e:
                st.error(f"❌ Error generating image: {e}")

elif st.session_state.history and st.session_state.selected_idx < len(st.session_state.history):
    # Show selected history item
    entry = st.session_state.history[st.session_state.selected_idx]
    img_path = entry.get("path", "")

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
        <div class="section-label" style="margin:0;">Viewing History</div>
        <span style="font-size:11px;color:var(--text-3);">· {entry['date']} at {entry['time']}</span>
    </div>
    """, unsafe_allow_html=True)

    if img_path and os.path.exists(img_path):
        st.markdown('<div class="img-frame-glow">', unsafe_allow_html=True)
        st.image(img_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with open(img_path, "rb") as file:
            st.download_button(
                label="⬇  Download Image",
                data=file,
                file_name=os.path.basename(img_path),
                mime="image/png"
            )

        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid var(--border);
                    border-left:3px solid var(--accent);border-radius:10px;
                    padding:12px 16px;margin-top:14px;">
            <div style="font-family:'Syne',sans-serif;font-size:10px;font-weight:700;
                        color:var(--text-3);letter-spacing:.09em;text-transform:uppercase;
                        margin-bottom:6px;">Prompt Used</div>
            <div style="font-size:13px;color:var(--text-1);line-height:1.6;">
                {entry['prompt']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-canvas">
            <div style="font-size:40px;opacity:.2;">🔍</div>
            <div style="font-size:14px;font-family:'Syne',sans-serif;font-weight:600;">
                Image file not found
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-canvas">
        <div style="font-size:54px;opacity:.16;">🖼</div>
        <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:600;
                    letter-spacing:.02em;">
            Your generated image will appear here
        </div>
        <div style="font-size:12px;opacity:.4;">Enter a prompt above and click Generate</div>
    </div>
    """, unsafe_allow_html=True)

# ── Recent grid at bottom ─────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="section-label">Recent Generations</div>', unsafe_allow_html=True)
    recent = list(reversed(st.session_state.history))[:3]
    cols = st.columns(3)
    for idx, entry in enumerate(recent):
        real_idx = len(st.session_state.history) - 1 - idx
        with cols[idx]:
            is_active = (real_idx == st.session_state.selected_idx)
            active_cls = "v-active" if is_active else ""
            img_path = entry.get("path", "")
            st.markdown(f'<div class="variant-wrap {active_cls}">', unsafe_allow_html=True)
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.markdown('<div class="thumb-placeholder">👗</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            short = entry["prompt"][:32] + "…" if len(entry["prompt"]) > 32 else entry["prompt"]
            st.caption(f"{entry['time']} · {short}")