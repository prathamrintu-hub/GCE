# app.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="GCE Dashboard", layout="wide", initial_sidebar_state="expanded")

# ----- Simple McKinsey-like theme via CSS -----
st.markdown(
    """
    <style>
    :root{
      --gce-blue: #0b5c8a;
      --gce-light: #f3f7fb;
      --gce-accent: #0077b6;
    }
    .reportview-container { background: var(--gce-light); }
    header {background: linear-gradient(90deg, var(--gce-blue), var(--gce-accent)) !important; padding: 16px 20px;}
    .stApp .css-1v3fvcr { padding-top: 0rem; }
    .big-kpi { font-size: 28px; font-weight:700; color:var(--gce-blue); }
    .small-muted { color: #666; font-size:13px; }
    .card { background: white; padding: 14px; border-radius:10px; box-shadow: 0 3px 8px rgba(0,0,0,0.06);}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----- Sidebar -----
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/main/frontend/public/favicon.png", width=64)
    st.title("GCE Dashboard")
    page = st.radio("", ["Overview", "Analytics", "AI Chat", "Data & Settings"])
    st.divider()
    st.write("Quick filters")
    date_from = st.date_input("From", datetime.today() - timedelta(days=30))
    date_to = st.date_input("To", datetime.today())
    st.markdown("---")
    st.caption("Built with ❤️ for GCE")

# ----- Sample data generator -----
@st.cache_data
def make_sample_data(days=60):
    rng = pd.date_range(end=pd.Timestamp.today(), periods=days)
    df = pd.DataFrame({
        "date": rng,
        "revenue": np.round(np.cumsum(np.random.normal(200, 100, size=days)) + 5000, 2),
        "cost": np.round(np.cumsum(np.random.normal(120, 60, size=days)) + 3000, 2),
        "orders": np.random.poisson(20, size=days).cumsum()
    })
    return df

df = make_sample_data(180)
df = df[(df["date"].dt.date >= date_from) & (df["date"].dt.date <= date_to)]

# ----- Pages -----
if page == "Overview":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><div class='big-kpi'>${:,.0f}</div><div class='small-muted'>Total Revenue</div></div>".format(df["revenue"].iloc[-1]), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><div class='big-kpi'>${:,.0f}</div><div class='small-muted'>Total Cost</div></div>".format(df["cost"].iloc[-1]), unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><div class='big-kpi'>{:,}</div><div class='small-muted'>Total Orders</div></div>".format(df["orders"].iloc[-1]), unsafe_allow_html=True)

    st.markdown("### Revenue vs Cost")
    revenue_chart = alt.Chart(df).transform_fold(
        ["revenue", "cost"], as_=["key", "value"]
    ).mark_line(point=True).encode(
        x="date:T",
        y="value:Q",
        color="key:N",
        tooltip=["date:T", "key:N", "value:Q"]
    ).properties(height=380)
    st.altair_chart(revenue_chart, use_container_width=True)

    st.markdown("### Recent data")
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True).head(10), use_container_width=True)

elif page == "Analytics":
    st.header("Analytics")
    st.write("Interactive controls")
    metric = st.selectbox("Choose metric", ["revenue", "cost", "orders"])
    window = st.slider("Smoothing window (days)", 1, 14, 5)

    df["smoothed"] = df[metric].rolling(window=window).mean().fillna(method="bfill")
    chart = alt.Chart(df).mark_area(opacity=0.3).encode(
        x="date:T", y=alt.Y("smoothed:Q", title=metric.title())
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)

    st.markdown("Segment comparison (simulated)")
    # small simulated breakdown
    breakdown = pd.DataFrame({
        "segment": ["Enterprise", "SMB", "Retail"],
        "value": [0.5, 0.3, 0.2]
    })
    st.bar_chart(breakdown.set_index("segment"))

elif page == "AI Chat":
    st.header("AI Chat (placeholder)")
    st.write("This panel will connect to OpenAI / Groq. Add your API key below to enable a simple assistant.")
    openai_key = st.text_input("OpenAI API key (sk-...)", type="password")
    user_msg = st.text_input("Ask a question about your data")
    if st.button("Send") and user_msg:
        if not openai_key:
            st.warning("Add your API key first (this template does not send keys anywhere).")
        else:
            # Placeholder response — replace with actual API call to OpenAI / Groq
            st.info("**Assistant (simulated):** I see your latest revenue is ${:,.0f}. Do you want a 3-point summary?".format(df["revenue"].iloc[-1]))

elif page == "Data & Settings":
    st.header("Data & Settings")
    st.write("Where to get data")
    st.markdown("""
    - Google Sheets: use `gspread` + service account JSON  
    - Local CSV / Excel: drop a file below  
    """)
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                user_df = pd.read_csv(uploaded)
            else:
                user_df = pd.read_excel(uploaded)
            st.success("Loaded file: {}".format(uploaded.name))
            st.dataframe(user_df.head(10))
        except Exception as e:
            st.error("Error reading file: " + str(e))

    st.markdown("---")
    st.write("Advanced")
    if st.checkbox("Show internal environment info"):
        st.write("Python version:", st.runtime.scriptrunner._python_version if hasattr(st.runtime, "scriptrunner") else "n/a")
        st.write("Streamlit version: (check in terminal)")

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
