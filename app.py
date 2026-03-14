import streamlit as st
import time
from agent import triage_ticket, PRIORITY_COLORS, CATEGORY_ICONS

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IT Triage Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* Global */
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0D0F14;
    color: #E8EAF0;
  }

  .stApp {
    background-color: #0D0F14;
  }

  /* Header */
  .hero {
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #1E2130;
    margin-bottom: 2rem;
  }
  .hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.5px;
    margin: 0;
  }
  .hero-title span {
    color: #4F8EF7;
  }
  .hero-subtitle {
    font-size: 0.95rem;
    color: #6B7280;
    margin-top: 0.4rem;
    font-weight: 300;
  }

  /* Input card */
  .input-card {
    background: #13161F;
    border: 1px solid #1E2130;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  /* Result cards */
  .result-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  .result-card {
    background: #13161F;
    border: 1px solid #1E2130;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
  }
  .result-card-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4B5563;
    margin-bottom: 0.5rem;
  }
  .result-card-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #E8EAF0;
  }
  .result-card-sub {
    font-size: 0.82rem;
    color: #6B7280;
    margin-top: 0.3rem;
    line-height: 1.4;
  }

  /* Priority badge */
  .priority-badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  /* Tags */
  .tag {
    display: inline-block;
    background: #1E2130;
    border: 1px solid #2A2F45;
    color: #9CA3AF;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    margin-right: 0.4rem;
    margin-top: 0.3rem;
    font-family: 'Space Mono', monospace;
  }

  /* Full-width cards */
  .card-full {
    background: #13161F;
    border: 1px solid #1E2130;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
  }

  /* Reply box */
  .reply-box {
    background: #0A0C10;
    border: 1px solid #2A2F45;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-size: 0.9rem;
    color: #CBD5E1;
    line-height: 1.7;
    margin-top: 0.5rem;
    white-space: pre-wrap;
  }

  /* Divider */
  .section-divider {
    border: none;
    border-top: 1px solid #1E2130;
    margin: 1.5rem 0;
  }

  /* Example tickets */
  .example-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4B5563;
    margin-bottom: 0.75rem;
  }

  /* Streamlit overrides */
  .stTextArea textarea {
    background-color: #0A0C10 !important;
    border: 1px solid #1E2130 !important;
    color: #E8EAF0 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
  }
  .stTextInput input {
    background-color: #0A0C10 !important;
    border: 1px solid #1E2130 !important;
    color: #E8EAF0 !important;
    border-radius: 8px !important;
  }
  .stSelectbox > div > div {
    background-color: #0A0C10 !important;
    border: 1px solid #1E2130 !important;
    color: #E8EAF0 !important;
    border-radius: 8px !important;
  }
  .stButton > button {
    background-color: #4F8EF7 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover {
    opacity: 0.85 !important;
  }
  label, .stTextArea label, .stTextInput label, .stSelectbox label {
    color: #6B7280 !important;
    font-size: 0.8rem !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
  }
  .stSpinner > div {
    border-top-color: #4F8EF7 !important;
  }
  footer { display: none; }
  #MainMenu { display: none; }
  header { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Example tickets ───────────────────────────────────────────────────────────
EXAMPLES = {
    "🔒 Security breach": "Someone just logged into my account from an IP in Russia. I didn't authorize this. I can still access my account but I'm scared my credentials are compromised. Please help urgently.",
    "🌐 VPN down": "I can't connect to the VPN since this morning. I'm working from home and can't access any internal systems. My team is waiting on me to push a critical deployment.",
    "📧 Email quota": "My Outlook keeps showing 'mailbox almost full' and I can't send emails anymore. I have important client meetings today and need this fixed ASAP.",
    "🖥️ Slow laptop": "My laptop has been extremely slow for the past week. It takes 5 minutes to boot and applications freeze constantly. I've tried restarting but nothing changed.",
    "🔑 Access request": "Hi, I just joined the DevOps team last Monday and still don't have access to Jira and Confluence. My manager is Sarah Chen. Can you please grant me access?"
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">IT Triage <span>Agent</span></p>
  <p class="hero-subtitle">Powered by Claude · Classifies, prioritizes and drafts responses for IT support tickets</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    # Example picker
    st.markdown('<p class="example-label">Quick examples</p>', unsafe_allow_html=True)
    example_choice = st.selectbox(
        "Quick examples",
        ["— paste your own ticket —"] + list(EXAMPLES.keys()),
        label_visibility="collapsed"
    )

    default_text = ""
    if example_choice and example_choice != "— paste your own ticket —":
        default_text = EXAMPLES[example_choice]

    ticket_text = st.text_area(
        "Ticket content",
        value=default_text,
        height=180,
        placeholder="Paste or type the IT support ticket here..."
    )

    c1, c2 = st.columns(2)
    with c1:
        user_name = st.text_input("Submitted by", placeholder="e.g. Marie Dupont")
    with c2:
        department = st.text_input("Department", placeholder="e.g. Finance")

    run = st.button("▶  ANALYZE TICKET", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # History
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<p class="example-label">Previous tickets</p>', unsafe_allow_html=True)
        for i, h in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"{h['icon']} {h['category']} · {h['priority']} · {h['preview']}"):
                st.markdown(f"**Summary:** {h['summary']}")

with col_right:
    if run and ticket_text.strip():
        with st.spinner("Analyzing ticket..."):
            result = triage_ticket(ticket_text, user_name, department)

        priority = result.get("priority", "Medium")
        category = result.get("category", "Other")
        icon = CATEGORY_ICONS.get(category, "📋")
        color = PRIORITY_COLORS.get(priority, "#FFD700")

        # Top row: category + priority
        st.markdown(f"""
        <div class="result-grid">
          <div class="result-card">
            <div class="result-card-label">Category</div>
            <div class="result-card-value">{icon} {category}</div>
          </div>
          <div class="result-card">
            <div class="result-card-label">Priority</div>
            <div class="result-card-value">
              <span class="priority-badge" style="background:{color}22; color:{color}; border: 1px solid {color}44;">
                {priority}
              </span>
            </div>
            <div class="result-card-sub">{result.get("priority_reason", "")}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ETA + Tags row
        tags_html = "".join([f'<span class="tag">{t}</span>' for t in result.get("tags", [])])
        st.markdown(f"""
        <div class="result-grid">
          <div class="result-card">
            <div class="result-card-label">Est. Resolution</div>
            <div class="result-card-value">⏱ {result.get("estimated_resolution_time", "—")}</div>
          </div>
          <div class="result-card">
            <div class="result-card-label">Tags</div>
            <div style="margin-top: 0.3rem">{tags_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Summary
        st.markdown(f"""
        <div class="card-full">
          <div class="result-card-label">Technician Summary</div>
          <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.7; margin-top: 0.4rem;">
            {result.get("summary", "")}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Suggested reply
        st.markdown(f"""
        <div class="card-full">
          <div class="result-card-label">Suggested Reply to User</div>
          <div class="reply-box">{result.get("suggested_reply", "")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Save to history
        st.session_state.history.append({
            "icon": icon,
            "category": category,
            "priority": priority,
            "preview": ticket_text[:50] + "...",
            "summary": result.get("summary", "")
        })

    elif run and not ticket_text.strip():
        st.warning("Please enter a ticket before analyzing.")
    else:
        st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:300px; color:#2A2F45; text-align:center;">
          <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
          <div style="font-family: 'Space Mono', monospace; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;">
            Select an example or paste a ticket<br>then click Analyze
          </div>
        </div>
        """, unsafe_allow_html=True)
