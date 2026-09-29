import os
import datetime
import sqlite3
import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(
    page_title="SectorPulse | Strategic Radar",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern UI Custom Styling
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .pulse-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-num {
        font-size: 1.6rem;
        font-weight: 700;
        color: #60a5fa;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Environment & Ecosystem Definition
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

ECOSYSTEM = {
    "Quick Commerce": ["Blinkit", "Zepto", "Instamart", "Zomato"],
    "Mobility & Transit": ["Rapido", "Uber", "Namma Yatri", "Ola"],
    "Logistics & Freight": ["Porter", "Delhivery"]
}

ALL_COMPETITORS = [app for apps in ECOSYSTEM.values() for app in apps]

def get_sector(app_name):
    for sector, apps in ECOSYSTEM.items():
        if app_name in apps:
            return sector
    return "General"

def get_default_move(app_name):
    sector = get_sector(app_name)
    if "Quick Commerce" in sector:
        return f"{app_name} rolls out sub-10 minute dark store fulfillment and zero-fee grocery tiers."
    elif "Mobility" in sector:
        return f"{app_name} launches zero-commission driver incentives and electric vehicle fleet subsidies."
    elif "Logistics" in sector:
        return f"{app_name} deploys automated sortation hubs to slash B2B freight turnaround times."
    else:
        return f"{app_name} adjusts pricing structures to capture market share."

# 4. SQLite Lightweight Signal Memory
conn = sqlite3.connect("marketpulse.db", check_same_thread=False)
conn.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app TEXT,
        sector TEXT,
        content TEXT,
        timestamp TEXT
    )
""")
conn.commit()

def record_signal(app, content):
    sector = get_sector(app)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    with conn:
        conn.execute("INSERT INTO signals (app, sector, content, timestamp) VALUES (?, ?, ?, ?)", (app, sector, content, ts))

def fetch_memory(app):
    cur = conn.cursor()
    cur.execute("SELECT content, timestamp FROM signals WHERE app = ? ORDER BY id DESC LIMIT 3", (app,))
    return [{"content": row[0], "timestamp": row[1]} for row in cur.fetchall()]

# 5. Sidebar Control Panel
st.sidebar.header("📡 Signal Ingestion Hub")
target_app = st.sidebar.selectbox("Select Competitor", ALL_COMPETITORS, key="sidebar_target_app")
st.sidebar.caption(f"Sector: `{get_sector(target_app)}`")

sidebar_signal_text = st.sidebar.text_area(
    "Market Signal / Update", 
    value=get_default_move(target_app), 
    key=f"sidebar_signal_{target_app}"
)

if st.sidebar.button("📥 Broadcast to Memory Bank", use_container_width=True):
    record_signal(target_app, sidebar_signal_text)
    st.sidebar.success(f"Signal logged for {target_app}!")

st.sidebar.markdown("---")
st.sidebar.subheader("Recent Stream Log")
for row in conn.execute("SELECT timestamp, app, content FROM signals ORDER BY id DESC LIMIT 5"):
    st.sidebar.markdown(f"""
    <div style="font-size:0.75rem; color:#9ca3af; margin-bottom:6px; border-left:2px solid #3b82f6; padding-left:6px;">
        <b>[{row[0]}] {row[1]}</b><br/>{row[2][:50]}...
    </div>
    """, unsafe_allow_html=True)

# 6. Main Header Layout
st.title("🎯 SectorPulse: Cross-Sector Strategic Radar")
st.markdown("Autonomous surveillance and LLM strategy synthesis across Quick Commerce, Mobility, and Logistics.")
st.markdown("---")

# Metrics Summary Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="pulse-card"><div style="color:#9ca3af;font-size:0.75rem;">ECOSYSTEM</div><div class="metric-num">{len(ALL_COMPETITORS)} Apps</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="pulse-card"><div style="color:#9ca3af;font-size:0.75rem;">VERTICALS</div><div class="metric-num">{len(ECOSYSTEM)} Sectors</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="pulse-card"><div style="color:#9ca3af;font-size:0.75rem;">ENGINE</div><div class="metric-num">Llama 3.3</div></div>', unsafe_allow_html=True)
with m4:
    total_logs = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    st.markdown(f'<div class="pulse-card"><div style="color:#9ca3af;font-size:0.75rem;">LOGGED SIGNALS</div><div class="metric-num">{total_logs} Events</div></div>', unsafe_allow_html=True)

# 7. Competitive Matrix & Analysis Interface
st.markdown("### ⚔️ Matrix Strategy Simulator")

col_a, col_b = st.columns(2)
with col_a:
    primary_app = st.selectbox("Primary Moving Competitor:", ALL_COMPETITORS, index=0, key="main_primary")
with col_b:
    rival_options = [c for c in ALL_COMPETITORS if c != primary_app]
    rival_app = st.selectbox("Rival Counter-Competitor:", rival_options, index=0, key="main_rival")

# Dynamic key ensures the text area updates its default value cleanly when changing the primary app
active_scenario = st.text_area(
    "💡 Strategic Market Move / Catalyst Under Analysis:",
    value=get_default_move(primary_app),
    height=90,
    key=f"main_scenario_{primary_app}"
)

if st.button("🚀 Generate Executive Counter-Report", type="primary", use_container_width=True):
    if not active_scenario.strip():
        st.warning("Please enter a valid strategic scenario.")
    else:
        record_signal(primary_app, active_scenario)
        p_history = fetch_memory(primary_app)
        r_history = fetch_memory(rival_app)

        prompt = f"""
        You are an elite Chief Strategy Officer analyzing cross-sector market competition.
        
        PRIMARY APPLICANT: {primary_app} ({get_sector(primary_app)})
        CATALYST MOVE: {active_scenario}
        HISTORY CONTEXT FOR {primary_app}: {p_history}
        
        RIVAL TARGET: {rival_app} ({get_sector(rival_app)})
        HISTORY CONTEXT FOR {rival_app}: {r_history}

        Provide a rigorous, high-level executive brief covering:
        1. **Unit Economics & Margin Implications**: How does this shift pricing structures, commissions, or customer acquisition costs?
        2. **Asymmetric Risk Analysis**: Evaluate the immediate churn and market share vulnerability for {rival_app}.
        3. **30-Day Tactical Counter-Actions**: Give 3 precise, actionable defensive maneuvers for {rival_app}.
        """

        if groq_client:
            with st.spinner("Synthesizing market intelligence via Llama 3.3..."):
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### 📋 Executive Intelligence Brief")
                st.markdown(response.choices[0].message.content)
        else:
            st.warning("⚠️ GROQ_API_KEY is missing. Set your environment variable to generate live AI briefs.")