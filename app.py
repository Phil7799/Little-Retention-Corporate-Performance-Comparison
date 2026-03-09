import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import json
import hashlib
import re
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Little Retention",
    page_icon="https://res.cloudinary.com/dnq8ne9lx/image/upload/v1753860594/infograph_ewfmm6.ico",
    layout="wide"
)

# ─────────────────────────────────────────────
# AUTH CONFIG
# ─────────────────────────────────────────────
ADMIN_EMAIL = "admin@little.africa"
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retention_users.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        initial = {
            ADMIN_EMAIL: {
                "password": hash_password("admin123"),
                "role": "admin",
                "active": True,
                "created_at": datetime.now().isoformat()
            }
        }
        save_users(initial)
        return initial
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_valid_email(email: str) -> bool:
    return bool(re.match(r'^[\w.\-+]+@little\.africa$', email.strip().lower()))

def authenticate(email: str, password: str) -> tuple:
    users = load_users()
    email = email.strip().lower()
    if email not in users:
        return False, "Email not registered."
    user = users[email]
    if not user.get("active", True):
        return False, "Your access has been revoked. Please contact the admin."
    if user["password"] != hash_password(password):
        return False, "Incorrect password."
    return True, "ok"

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def show_login():
    st.markdown("""
    <style>
    .login-wrapper {
        display: flex; justify-content: center; align-items: center;
        padding-top: 80px;
    }
    .login-box {
        background: #0000FF; color: white;
        padding: 40px 48px; border-radius: 12px;
        text-align: center; max-width: 420px; width: 100%;
    }
    .login-box h2 { margin-bottom: 4px; font-size: 1.8rem; }
    .login-box p  { color: #c8c8ff; margin-bottom: 28px; font-size: 0.95rem; }
    </style>
    <div class="login-wrapper">
      <div class="login-box">
        <h2>🚕 Little Retention</h2>
        <p>Sign in with your @little.africa account</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.4, 1])
    with col_m:
        email_input    = st.text_input("Email", placeholder="you@little.africa", key="login_email")
        password_input = st.text_input("Password", type="password", key="login_password")
        login_btn      = st.button("Sign In", use_container_width=True)
        if login_btn:
            if not email_input:
                st.error("Please enter your email.")
            elif not is_valid_email(email_input):
                st.error("Only @little.africa email addresses are allowed.")
            elif not password_input:
                st.error("Please enter your password.")
            else:
                ok, msg = authenticate(email_input, password_input)
                if ok:
                    users = load_users()
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"]  = email_input.strip().lower()
                    st.session_state["current_role"]  = users[email_input.strip().lower()]["role"]
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────
def show_admin_panel():
    st.write("## 🔐 Admin Panel – User Management")
    users = load_users()
    st.write("### Registered Users")
    user_rows = []
    for email, info in users.items():
        user_rows.append({
            "Email": email,
            "Role": info.get("role", "user"),
            "Status": "✅ Active" if info.get("active", True) else "🚫 Revoked",
            "Created": info.get("created_at", "—")[:10],
        })
    st.dataframe(pd.DataFrame(user_rows), use_container_width=True, hide_index=True)
    st.markdown("---")
    col_add, col_rev = st.columns(2)
    with col_add:
        st.write("#### ➕ Add New User")
        new_email    = st.text_input("New user email (@little.africa)", key="new_email")
        new_password = st.text_input("Temporary password", type="password", key="new_pass")
        new_role     = st.selectbox("Role", ["user", "admin"], key="new_role")
        if st.button("Add User", key="add_user_btn"):
            new_email_clean = new_email.strip().lower()
            if not is_valid_email(new_email_clean):
                st.error("Email must be @little.africa format.")
            elif new_email_clean in users:
                st.warning("This email is already registered.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                users[new_email_clean] = {
                    "password": hash_password(new_password),
                    "role": new_role,
                    "active": True,
                    "created_at": datetime.now().isoformat()
                }
                save_users(users)
                st.success(f"✅ {new_email_clean} added successfully!")
                st.rerun()
    with col_rev:
        st.write("#### 🔧 Manage Access")
        other_users = [e for e in users if e != st.session_state["current_user"]]
        if not other_users:
            st.info("No other users to manage.")
        else:
            target = st.selectbox("Select user", other_users, key="manage_target")
            target_info = users[target]
            is_active = target_info.get("active", True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if is_active:
                    if st.button("🚫 Revoke Access", key="revoke_btn"):
                        users[target]["active"] = False
                        save_users(users)
                        st.success(f"Access revoked for {target}.")
                        st.rerun()
                else:
                    if st.button("✅ Restore Access", key="restore_btn"):
                        users[target]["active"] = True
                        save_users(users)
                        st.success(f"Access restored for {target}.")
                        st.rerun()
            with c2:
                new_pw = st.text_input("Reset password", type="password", key="reset_pw")
                if st.button("🔑 Reset Password", key="reset_btn"):
                    if len(new_pw) < 6:
                        st.error("Min 6 characters.")
                    else:
                        users[target]["password"] = hash_password(new_pw)
                        save_users(users)
                        st.success(f"Password reset for {target}.")
                        st.rerun()
            with c3:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete User", key="delete_btn"):
                    del users[target]
                    save_users(users)
                    st.success(f"{target} deleted.")
                    st.rerun()
    st.markdown("---")

# ─────────────────────────────────────────────
# AUTH GATE
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    show_login()
    st.stop()

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        target_df        = pd.read_excel("data.xlsx", sheet_name="Target")
        data_2025_df     = pd.read_excel("data.xlsx", sheet_name="2025")
        data_2026_df     = pd.read_excel("data.xlsx", sheet_name="2026")
        data_2026_week_df = pd.read_excel("data.xlsx", sheet_name="2026_week_data")
        return target_df, data_2025_df, data_2026_df, data_2026_week_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

target_df, data_2025_df, data_2026_df, data_2026_week_df = load_data()

if target_df is None:
    st.stop()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
MONTH_COLS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NUM  = {m: i+1 for i, m in enumerate(MONTH_COLS)}
WEEK_COLS  = [f"week {i}" for i in range(1, 11)]

current_user = st.session_state["current_user"]
current_role = st.session_state["current_role"]

# ─────────────────────────────────────────────
# SIDEBAR  ← All filters + user info live here
# ─────────────────────────────────────────────
with st.sidebar:
    # User card
    st.markdown(f"""
    <div style='background:#0000FF;color:white;padding:12px 16px;border-radius:8px;
                margin-bottom:12px;font-size:0.85rem;'>
        👤 <b>{current_user}</b><br>
        <span style='color:#c8c8ff;font-size:0.78rem;'>{current_role.capitalize()}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out"):
        for key in ["authenticated", "current_user", "current_role"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    # Corporate filter
    corporate = st.selectbox(
        "Corporate",
        ["All"] + sorted(target_df["Corporates"].unique()),
        key="sb_corporate"
    )

    # Industry filter
    industry = st.selectbox(
        "Industry",
        ["All"] + sorted(target_df["industry_"].unique()),
        key="sb_industry"
    )

    # Assignee filter
    assignee = st.selectbox(
        "Assignee",
        ["All"] + sorted(target_df["Assignee_"].unique()),
        key="sb_assignee"
    )

    # Month filter (2026 months present in data)
    available_months_2026 = [m for m in MONTH_COLS if m in data_2026_df.columns]
    month_filter = st.selectbox(
        "Month (2026)",
        ["All"] + available_months_2026,
        key="sb_month"
    )

    # Churned period filter
    st.markdown("---")
    st.markdown("### 🔴 Churn Filter")
    churn_period = st.selectbox(
        "Show Churned Corporates",
        ["None", "Churned (30 days)", "Churned (60 days)", "Churned (90 days)"],
        key="sb_churn"
    )

# ─────────────────────────────────────────────
# ADMIN PANEL (admins only, in expander in main area)
# ─────────────────────────────────────────────
if current_role == "admin":
    with st.expander("🔐 Admin Panel – User Management", expanded=False):
        show_admin_panel()

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
filtered_target      = target_df.copy()
filtered_2025        = data_2025_df.copy()
filtered_2026        = data_2026_df.copy()
filtered_2026_week   = data_2026_week_df.copy()

if corporate != "All":
    filtered_target    = filtered_target[filtered_target["Corporates"] == corporate]
    filtered_2025      = filtered_2025[filtered_2025["Corporates"] == corporate]
    filtered_2026      = filtered_2026[filtered_2026["Corporates"] == corporate]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]

if industry != "All":
    filtered_target    = filtered_target[filtered_target["industry_"] == industry]
    filtered_2025      = filtered_2025[filtered_2025["industry_"] == industry]
    filtered_2026      = filtered_2026[filtered_2026["industry_"] == industry]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["industry_"] == industry]

if assignee != "All":
    filtered_target    = filtered_target[filtered_target["Assignee_"] == assignee]
    filtered_2025      = filtered_2025[filtered_2025["Assignee_"] == assignee]
    filtered_2026      = filtered_2026[filtered_2026["Assignee_"] == assignee]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Assignee_"] == assignee]

# Determine months to use
if month_filter == "All":
    months_2026 = available_months_2026
else:
    months_2026 = [month_filter]

if filtered_target.empty or filtered_2025.empty or filtered_2026.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ─────────────────────────────────────────────
# CHURN DETECTION HELPERS
# ─────────────────────────────────────────────
def get_churned_by_period(days: int):
    """
    'Churned' = corporate had rides in 2025 but has 0 rides in the
    last `days`-worth of 2026 weekly data (or is missing from 2026).
    We approximate days → weeks (7 days ≈ 1 week, max 6 weeks available).
    """
    weeks_threshold = max(1, min(days // 7, len(WEEK_COLS)))
    recent_cols = WEEK_COLS[-weeks_threshold:]

    # Corporates in 2025 but not at all in 2026
    not_in_2026 = set(data_2025_df["Corporates"]) - set(data_2026_df["Corporates"])

    # Corporates in 2026 weekly data with 0 rides in the recent window
    if not data_2026_week_df.empty:
        wk = data_2026_week_df.copy()
        for c in recent_cols:
            if c in wk.columns:
                wk[c] = pd.to_numeric(wk[c], errors="coerce").fillna(0)
        existing_recent_cols = [c for c in recent_cols if c in wk.columns]
        if existing_recent_cols:
            wk["recent_total"] = wk[existing_recent_cols].sum(axis=1)
            zero_recent = set(wk[wk["recent_total"] == 0]["Corporates"])
        else:
            zero_recent = set()
    else:
        zero_recent = set()

    churned = not_in_2026 | zero_recent
    result = []
    for corp in churned:
        row_2025 = data_2025_df[data_2025_df["Corporates"] == corp]
        row_target = target_df[target_df["Corporates"] == corp]
        if not row_2025.empty:
            r25 = row_2025.iloc[0]
            rt  = row_target.iloc[0] if not row_target.empty else None
            result.append({
                "Corporate":  corp,
                "Industry":   r25.get("industry_", "—"),
                "Assignee":   r25.get("Assignee_", "—"),
                "2025 Total": float(r25[[m for m in MONTH_COLS if m in r25.index]].sum()),
                "Target":     float(rt[[m for m in MONTH_COLS if m in rt.index]].sum()) if rt is not None else 0,
                "Churn Period": f"{days} days"
            })
    return pd.DataFrame(result)

# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────
st.title("🚕 Little Retention: Corporate Performance")

# ─────────────────────────────────────────────
# CHURN PERIOD VIEW (when filter active)
# ─────────────────────────────────────────────
if churn_period != "None":
    days_map = {"Churned (30 days)": 30, "Churned (60 days)": 60, "Churned (90 days)": 90}
    days = days_map[churn_period]
    churned_df_period = get_churned_by_period(days)
    st.header(f"🔴 {churn_period} – Inactive Corporates")
    if churned_df_period.empty:
        st.success("No churned corporates found for this period.")
    else:
        st.info(f"Found **{len(churned_df_period)}** corporates inactive in the last {days} days.")
        st.dataframe(churned_df_period.sort_values("2025 Total", ascending=False),
                     use_container_width=True, hide_index=True)
    st.markdown("---")

# ─────────────────────────────────────────────
# BUILD COMPARISON DATA
# ─────────────────────────────────────────────
common_corporates = set(filtered_target["Corporates"]).intersection(
    set(filtered_2025["Corporates"]), set(filtered_2026["Corporates"])
)

if not common_corporates:
    st.warning("No common corporates found for the selected filters.")
    st.stop()

comparison_data = []
for corp in common_corporates:
    row_target = filtered_target[filtered_target["Corporates"] == corp].iloc[0]
    row_2025   = filtered_2025[filtered_2025["Corporates"] == corp].iloc[0]
    row_2026   = filtered_2026[filtered_2026["Corporates"] == corp].iloc[0]
    for month in months_2026:
        target_val = float(row_target.get(month, 0) or 0)
        val_2025   = float(row_2025.get(month, 0) or 0)
        val_2026   = float(row_2026.get(month, 0) or 0)
        pct_2025   = ((val_2026 - val_2025) / val_2025 * 100) if val_2025 != 0 else 0
        pct_target = ((val_2026 - target_val) / target_val * 100) if target_val != 0 else 0
        comparison_data.append({
            "Corporate":               corp,
            "Month":                   month,
            "Target":                  target_val,
            "2025":                    val_2025,
            "2026":                    val_2026,
            "Industry":                row_target["industry_"],
            "Assignee":                row_target["Assignee_"],
            "% vs 2025":               pct_2025,
            "% vs Target":             pct_target
        })

comparison_df = pd.DataFrame(comparison_data)

# Aggregated by month for charts
comparison_df_chart = comparison_df.groupby("Month")[["Target", "2025", "2026"]].sum().reindex(months_2026).reset_index()

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_target = comparison_df_chart["Target"].sum()
total_2025   = comparison_df_chart["2025"].sum()
total_2026   = comparison_df_chart["2026"].sum()
shortfall    = total_target - total_2026

# Active corporates (in 2026)
active_corps = len(filtered_2026["Corporates"].unique())

# Churned last 30 days
churned_30 = get_churned_by_period(30)
num_churned_30 = len(churned_30)

# Growth rate vs target
growth_vs_target = ((total_2026 - total_target) / total_target * 100) if total_target != 0 else 0
# Growth rate vs 2025
growth_vs_2025 = ((total_2026 - total_2025) / total_2025 * 100) if total_2025 != 0 else 0

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
st.header("📊 Key Performance Indicators")

st.markdown("""
<style>
.kpi-card {
    padding: 16px 20px; border-radius: 10px; text-align: center;
    margin-bottom: 8px;
}
.kpi-card .kpi-label { font-size: 0.78rem; font-weight: 600; opacity: 0.85; margin-bottom: 6px; }
.kpi-card .kpi-value { font-size: 1.5rem; font-weight: 700; }
.kpi-card .kpi-sub   { font-size: 0.75rem; margin-top: 4px; opacity: 0.8; }
.kpi-red    { background:#FF0000; color:white; }
.kpi-blue   { background:#0000FF; color:white; }
.kpi-yellow { background:#FFCC00; color:#1a1a1a; }
.kpi-green  { background:#00C853; color:white; }
.kpi-orange { background:#FF6D00; color:white; }
.kpi-purple { background:#6200EA; color:white; }
.kpi-teal   { background:#00796B; color:white; }
.kpi-pink   { background:#C2185B; color:white; }
</style>
""", unsafe_allow_html=True)

# Row 1
r1c1, r1c2, r1c3, r1c4 = st.columns(4)
with r1c1:
    st.markdown(f"""<div class="kpi-card kpi-red">
        <div class="kpi-label">🎯 Total Target (2026)</div>
        <div class="kpi-value">{total_target:,.0f}</div>
    </div>""", unsafe_allow_html=True)
with r1c2:
    st.markdown(f"""<div class="kpi-card kpi-blue">
        <div class="kpi-label">📅 Total 2025</div>
        <div class="kpi-value">{total_2025:,.0f}</div>
    </div>""", unsafe_allow_html=True)
with r1c3:
    st.markdown(f"""<div class="kpi-card kpi-yellow">
        <div class="kpi-label">📅 Total 2026</div>
        <div class="kpi-value">{total_2026:,.0f}</div>
    </div>""", unsafe_allow_html=True)
with r1c4:
    shortfall_class = "kpi-orange" if shortfall > 0 else "kpi-green"
    shortfall_label = "⚠️ Shortfall to Target" if shortfall > 0 else "✅ Surplus vs Target"
    st.markdown(f"""<div class="kpi-card {shortfall_class}">
        <div class="kpi-label">{shortfall_label}</div>
        <div class="kpi-value">{abs(shortfall):,.0f}</div>
    </div>""", unsafe_allow_html=True)

# Row 2
r2c1, r2c2, r2c3, r2c4 = st.columns(4)
with r2c1:
    gt_class = "kpi-green" if growth_vs_target >= 0 else "kpi-red"
    gt_arrow = "▲" if growth_vs_target >= 0 else "▼"
    st.markdown(f"""<div class="kpi-card {gt_class}">
        <div class="kpi-label">📈 Growth Rate vs Target</div>
        <div class="kpi-value">{gt_arrow} {abs(growth_vs_target):.1f}%</div>
    </div>""", unsafe_allow_html=True)
with r2c2:
    g25_class = "kpi-green" if growth_vs_2025 >= 0 else "kpi-orange"
    g25_arrow = "▲" if growth_vs_2025 >= 0 else "▼"
    st.markdown(f"""<div class="kpi-card {g25_class}">
        <div class="kpi-label">📈 Growth Rate vs 2025</div>
        <div class="kpi-value">{g25_arrow} {abs(growth_vs_2025):.1f}%</div>
    </div>""", unsafe_allow_html=True)
with r2c3:
    st.markdown(f"""<div class="kpi-card kpi-teal">
        <div class="kpi-label">✅ Active Corporates (2026)</div>
        <div class="kpi-value">{active_corps}</div>
    </div>""", unsafe_allow_html=True)
with r2c4:
    churn_class = "kpi-pink" if num_churned_30 > 0 else "kpi-green"
    st.markdown(f"""<div class="kpi-card {churn_class}">
        <div class="kpi-label">🔴 Churned (Last 30 Days)</div>
        <div class="kpi-value">{num_churned_30}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COMPARISON TABLE
# ─────────────────────────────────────────────
def format_pct(val):
    if val > 0:   return f"+{val:.1f}% 😍"
    elif val < 0: return f"{val:.1f}% 🤬"
    else:         return f"0.0% 😐"

display_df = comparison_df.copy()
display_df["% vs 2025"]  = display_df["% vs 2025"].apply(format_pct)
display_df["% vs Target"] = display_df["% vs Target"].apply(format_pct)

st.header("📋 Comparison Table (2026 vs 2025 vs Target)")
st.dataframe(display_df[["Corporate","Month","Industry","Assignee","Target","2025","2026","% vs 2025","% vs Target"]],
             use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
st.header("📈 Performance Charts")

# — Chart 1: Monthly line comparison
col_c1, col_c2 = st.columns(2)
with col_c1:
    fig_line = go.Figure()
    colors = {"Target": "#FF0000", "2025": "#0000FF", "2026": "#00C853"}
    for metric in ["Target", "2025", "2026"]:
        fig_line.add_trace(go.Scatter(
            x=comparison_df_chart["Month"],
            y=comparison_df_chart[metric],
            name=metric,
            mode="lines+markers+text",
            text=comparison_df_chart[metric].round(0).astype(int).astype(str),
            textposition="top center",
            line=dict(width=2, color=colors[metric]),
            marker=dict(size=8)
        ))
    fig_line.update_layout(
        title="Monthly Performance: 2026 vs 2025 vs Target",
        xaxis_title="Month", yaxis_title="Revenue",
        template="plotly_white", height=400, showlegend=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

# — Chart 2: Revenue by Assignee (pie)
with col_c2:
    assignee_rev = filtered_2026.copy()
    assignee_rev = assignee_rev.merge(
        target_df[["Corporates", "Assignee_"]], on="Corporates", how="left"
    )
    if "Assignee_" not in assignee_rev.columns and "Assignee_x" in assignee_rev.columns:
        assignee_rev["Assignee_"] = assignee_rev["Assignee_x"]
    
    rev_cols_2026 = [m for m in months_2026 if m in assignee_rev.columns]
    if rev_cols_2026 and "Assignee_" in assignee_rev.columns:
        assignee_rev["Total"] = assignee_rev[rev_cols_2026].sum(axis=1)
        agg_assignee = assignee_rev.groupby("Assignee_")["Total"].sum().reset_index()
        fig_pie = px.pie(
            agg_assignee, names="Assignee_", values="Total",
            title="Revenue Breakdown by Assignee (2026)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

# — Chart 3: Revenue by Industry (bar)
col_c3, col_c4 = st.columns(2)
with col_c3:
    industry_2026 = filtered_2026.copy()
    industry_2026 = industry_2026.merge(
        target_df[["Corporates", "industry_"]], on="Corporates", how="left"
    )
    if "industry_" not in industry_2026.columns and "industry__x" in industry_2026.columns:
        industry_2026["industry_"] = industry_2026["industry__x"]
    
    rev_cols_2026 = [m for m in months_2026 if m in industry_2026.columns]
    if rev_cols_2026 and "industry_" in industry_2026.columns:
        industry_2026["Total"] = industry_2026[rev_cols_2026].sum(axis=1)
        agg_industry = industry_2026.groupby("industry_")["Total"].sum().reset_index().sort_values("Total", ascending=True)
        fig_bar_ind = px.bar(
            agg_industry, x="Total", y="industry_", orientation="h",
            title="Revenue by Industry (2026)",
            color="Total", color_continuous_scale="Blues"
        )
        fig_bar_ind.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar_ind, use_container_width=True)

# — Chart 4: YoY growth per corporate (top 15)
with col_c4:
    yoy_data = []
    for corp in common_corporates:
        r25 = filtered_2025[filtered_2025["Corporates"] == corp].iloc[0]
        r26 = filtered_2026[filtered_2026["Corporates"] == corp].iloc[0]
        v25 = float(r25[[m for m in months_2026 if m in r25.index]].sum() or 0)
        v26 = float(r26[[m for m in months_2026 if m in r26.index]].sum() or 0)
        pct = ((v26 - v25) / v25 * 100) if v25 != 0 else 0
        yoy_data.append({"Corporate": corp, "YoY %": pct, "2026 Rev": v26})
    yoy_df = pd.DataFrame(yoy_data).sort_values("YoY %", ascending=False).head(15)
    fig_yoy = px.bar(
        yoy_df, x="YoY %", y="Corporate", orientation="h",
        title="Top 15 Corporates: YoY Growth vs 2025 (%)",
        color="YoY %", color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0
    )
    fig_yoy.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_yoy, use_container_width=True)

# — Chart 5: Weekly trend
st.header("📅 2026 Weekly Trend per Corporate")
if not filtered_2026_week.empty:
    for col in WEEK_COLS:
        if col in filtered_2026_week.columns:
            filtered_2026_week[col] = pd.to_numeric(filtered_2026_week[col], errors="coerce").fillna(0)

    if corporate != "All":
        plot_df = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]
        corps_to_plot = [corporate]
    else:
        total_rev = filtered_2026_week[[c for c in WEEK_COLS if c in filtered_2026_week.columns]].sum(axis=1)
        top_idx = total_rev.nlargest(5).index
        plot_df = filtered_2026_week.loc[top_idx]
        corps_to_plot = plot_df["Corporates"].unique()

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        fig_weekly = go.Figure()
        present_weeks = [w for w in WEEK_COLS if w in plot_df.columns]
        for corp in corps_to_plot:
            corp_row = plot_df[plot_df["Corporates"] == corp]
            if corp_row.empty:
                continue
            vals = [float(corp_row.iloc[0][w]) for w in present_weeks]
            fig_weekly.add_trace(go.Scatter(
                x=present_weeks, y=vals, mode="lines+markers", name=corp,
                line=dict(width=2), marker=dict(size=6)
            ))
        fig_weekly.update_layout(
            title="Weekly Revenue Trend (Top 5 or Selected)",
            xaxis_title="Week", yaxis_title="Revenue",
            template="plotly_white", height=400
        )
        st.plotly_chart(fig_weekly, use_container_width=True)

    with col_w2:
        # Week-over-week change heatmap
        if len(present_weeks) >= 2:
            heat_data = []
            for corp in corps_to_plot:
                corp_row = plot_df[plot_df["Corporates"] == corp]
                if corp_row.empty:
                    continue
                vals = [float(corp_row.iloc[0][w]) for w in present_weeks]
                heat_data.append([corp] + vals)
            if heat_data:
                heat_df = pd.DataFrame(heat_data, columns=["Corporate"] + present_weeks)
                heat_df = heat_df.set_index("Corporate")
                fig_heat = px.imshow(
                    heat_df, title="Weekly Revenue Heatmap",
                    color_continuous_scale="Blues", aspect="auto"
                )
                fig_heat.update_layout(height=400)
                st.plotly_chart(fig_heat, use_container_width=True)

    # Weekly data table with slope
    def calc_slope(row):
        vals = [float(row[w]) for w in present_weeks if pd.notna(row.get(w, 0))]
        if len(vals) < 2:
            return 0
        x = list(range(1, len(vals)+1))
        slope, _ = np.polyfit(x, vals, 1)
        return round(slope, 2)

    filtered_2026_week["Trend Slope"] = filtered_2026_week.apply(calc_slope, axis=1)
    st.dataframe(filtered_2026_week, use_container_width=True, hide_index=True)

# — Chart 6: Target attainment per assignee
st.header("🎯 Target Attainment by Assignee")
attain_data = comparison_df.groupby("Assignee").agg(
    Target=("Target", "sum"),
    Revenue_2026=("2026", "sum")
).reset_index()
attain_data["Attainment %"] = (attain_data["Revenue_2026"] / attain_data["Target"] * 100).round(1)
fig_attain = px.bar(
    attain_data, x="Assignee", y="Attainment %",
    title="Target Attainment % per Assignee (2026)",
    color="Attainment %", color_continuous_scale="RdYlGn",
    color_continuous_midpoint=100, text="Attainment %"
)
fig_attain.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target = 100%")
fig_attain.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_attain.update_layout(height=400, showlegend=False)
st.plotly_chart(fig_attain, use_container_width=True)

# ─────────────────────────────────────────────
# CHURNED CORPORATES (Global)
# ─────────────────────────────────────────────
churned_all = set(data_2025_df["Corporates"]) - set(data_2026_df["Corporates"])
churned_global = []
for corp in churned_all:
    if corp in target_df["Corporates"].values:
        rt = target_df[target_df["Corporates"] == corp].iloc[0]
        r25 = data_2025_df[data_2025_df["Corporates"] == corp].iloc[0]
        churned_global.append({
            "Corporate": corp,
            "Industry":  rt["industry_"],
            "Assignee":  rt["Assignee_"],
            "2025 Total": float(r25[[m for m in MONTH_COLS if m in r25.index]].sum()),
            "Target":     float(rt[[m for m in MONTH_COLS if m in rt.index]].sum())
        })

churned_global_df = pd.DataFrame(churned_global)
if not churned_global_df.empty:
    st.header("❌ Churned Corporates (Active in 2025, Inactive in 2026)")
    st.dataframe(churned_global_df.sort_values("2025 Total", ascending=False),
                 use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# SUMMARY NOTE
# ─────────────────────────────────────────────
if total_2026 >= total_target:
    advice = "Great job 💥! 2026 performance has met or exceeded the target. Keep it up!"
else:
    advice = (
        f"You need to do better 👎🏻. An additional **{shortfall:,.0f}** is needed to meet target.\n\n"
        "- **Increase Engagement**: Targeted marketing campaigns for at-risk accounts.\n"
        "- **Optimize Operations**: Streamline for efficiency.\n"
        "- **Upsell Opportunities**: Cross-sell to existing clients.\n"
        "- **Training**: Boost corporate user productivity."
    )

st.header("📝 Summary Note")
st.markdown(f"""
**Total Target (2026):** {total_target:,.0f} &nbsp;|&nbsp;
**Total 2025:** {total_2025:,.0f} &nbsp;|&nbsp;
**Total 2026:** {total_2026:,.0f} &nbsp;|&nbsp;
**Shortfall:** {shortfall:,.0f}

**Growth vs 2025:** {growth_vs_2025:+.1f}% &nbsp;|&nbsp;
**Growth vs Target:** {growth_vs_target:+.1f}%

**Advice:**  
{advice}
""")

# ─────────────────────────────────────────────
# 🤖 RETENTION BOT
# ─────────────────────────────────────────────
st.markdown("---")
st.header("🤖 Nexus Phil")
st.markdown(
    "Ask me anything about corporate retention, churn risk, growth opportunities, or assignee performance."
)

# Initialise chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── Build rich data context for the bot ──────────────────────────────────────
def build_bot_context() -> str:
    lines = []

    # --- Active / churned summary ---
    active_set  = set(data_2026_df["Corporates"])
    churned_set = set(data_2025_df["Corporates"]) - active_set
    lines.append(f"Active corporates in 2026: {len(active_set)}")
    lines.append(f"Churned corporates (in 2025, missing from 2026): {len(churned_set)}")
    if churned_set:
        lines.append("Churned corporates: " + ", ".join(sorted(churned_set)[:30]))

    # --- YoY performance per corporate ---
    lines.append("\n=== YoY performance (2026 vs 2025, available months) ===")
    yoy_rows = []
    present_months = [m for m in MONTH_COLS if m in data_2026_df.columns]
    for corp in set(data_2026_df["Corporates"]).intersection(set(data_2025_df["Corporates"])):
        r26 = data_2026_df[data_2026_df["Corporates"] == corp].iloc[0]
        r25 = data_2025_df[data_2025_df["Corporates"] == corp].iloc[0]
        v26 = float(r26[[m for m in present_months if m in r26.index]].sum())
        v25 = float(r25[[m for m in present_months if m in r25.index]].sum())
        pct = round(((v26 - v25) / v25 * 100), 1) if v25 != 0 else 0
        rt  = target_df[target_df["Corporates"] == corp]
        industry = rt["industry_"].values[0] if not rt.empty else "—"
        assignee = rt["Assignee_"].values[0] if not rt.empty else "—"
        yoy_rows.append((corp, v25, v26, pct, industry, assignee))

    yoy_rows.sort(key=lambda x: x[3])           # ascending → declining first
    for corp, v25, v26, pct, ind, asn in yoy_rows:
        lines.append(f"  {corp}: 2025={v25:,.0f}, 2026={v26:,.0f}, YoY={pct:+.1f}%, Industry={ind}, Assignee={asn}")

    # --- Weekly trend (last 6 weeks) ---
    lines.append("\n=== Weekly data (2026) ===")
    wk_df = data_2026_week_df.copy()
    for c in WEEK_COLS:
        if c in wk_df.columns:
            wk_df[c] = pd.to_numeric(wk_df[c], errors="coerce").fillna(0)
    
    present_wk = [c for c in WEEK_COLS if c in wk_df.columns]
    if len(present_wk) >= 2:
        first_half = present_wk[:len(present_wk)//2]
        second_half = present_wk[len(present_wk)//2:]
        wk_df["first_half"]  = wk_df[first_half].sum(axis=1)
        wk_df["second_half"] = wk_df[second_half].sum(axis=1)
        wk_df["trend_pct"]   = wk_df.apply(
            lambda r: round((r["second_half"]-r["first_half"])/r["first_half"]*100, 1)
            if r["first_half"] != 0 else 0, axis=1
        )
        for _, row in wk_df.iterrows():
            rt = target_df[target_df["Corporates"] == row["Corporates"]]
            asn = rt["Assignee_"].values[0] if not rt.empty else "—"
            ind = rt["industry_"].values[0] if not rt.empty else "—"
            weekly_vals = ", ".join([f"{row.get(w,0):.0f}" for w in present_wk])
            lines.append(
                f"  {row['Corporates']}: weeks=[{weekly_vals}], "
                f"trend={row['trend_pct']:+.1f}%, Assignee={asn}, Industry={ind}"
            )

    # --- Target context ---
    lines.append("\n=== Target context ===")
    lines.append(f"Total target (2026, Jan-Feb): {total_target:,.0f}")
    lines.append(f"Total 2026 actual: {total_2026:,.0f}")
    lines.append(f"Total 2025 actual: {total_2025:,.0f}")
    lines.append(f"Shortfall: {shortfall:,.0f}")
    lines.append(f"Growth vs target: {growth_vs_target:+.1f}%")
    lines.append(f"Growth vs 2025: {growth_vs_2025:+.1f}%")

    # --- Industry breakdown ---
    lines.append("\n=== Industry performance 2026 vs 2025 ===")
    ind_rows = []
    for corp, v25, v26, pct, ind, asn in yoy_rows:
        ind_rows.append({"Industry": ind, "2025": v25, "2026": v26})
    if ind_rows:
        ind_df = pd.DataFrame(ind_rows).groupby("Industry")[["2025","2026"]].sum().reset_index()
        for _, row in ind_df.iterrows():
            p = round((row["2026"]-row["2025"])/row["2025"]*100, 1) if row["2025"] != 0 else 0
            lines.append(f"  {row['Industry']}: 2025={row['2025']:,.0f}, 2026={row['2026']:,.0f}, YoY={p:+.1f}%")

    # --- Assignee performance ---
    lines.append("\n=== Assignee performance ===")
    asn_rows = []
    for corp, v25, v26, pct, ind, asn in yoy_rows:
        asn_rows.append({"Assignee": asn, "2025": v25, "2026": v26})
    if asn_rows:
        asn_df = pd.DataFrame(asn_rows).groupby("Assignee")[["2025","2026"]].sum().reset_index()
        for _, row in asn_df.iterrows():
            p = round((row["2026"]-row["2025"])/row["2025"]*100, 1) if row["2025"] != 0 else 0
            lines.append(f"  {row['Assignee']}: 2025={row['2025']:,.0f}, 2026={row['2026']:,.0f}, YoY={p:+.1f}%")

    return "\n".join(lines)

SYSTEM_PROMPT = """You are the Little Retention Intelligence Bot — an expert data analyst for Little Africa's corporate taxi ride retention team.

You have access to detailed retention data below. Use it to give precise, actionable answers.
Always be concise, structured, and professional. Use bullet points and numbers where helpful.
When relevant, always mention: the corporate name, assignee, industry, revenue figures, and % change.

Your key analytical tasks:
1. Churn risk detection (weekly decline >30%)
2. Churned corporates identification  
3. YoY decline vs 2025 (silent churn)
4. Growth leaders
5. Industry performance trends
6. Assignee/account-manager risk
7. Weekly retention priority list
8. Personal assignee performance
9. Growth opportunities

Always ground your answers strictly in the data provided. If something is not in the data, say so clearly.

=== RETENTION DATA ===
{context}
=== END DATA ===
"""

def chat_with_bot(user_message: str, history: list) -> str:
    """Call the Anthropic API with full context."""
    import urllib.request
    context = build_bot_context()
    system  = SYSTEM_PROMPT.format(context=context)

    messages = []
    for turn in history:
        messages.append({"role": "user",      "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1500,
        "system": system,
        "messages": messages
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except Exception as e:
        return f"⚠️ Bot error: {e}"

# ── Quick-question buttons ────────────────────────────────────────────────────
st.markdown("**💡 Quick questions:**")
quick_questions = [
    "Which corporates are at risk of churning this month?",
    "Which corporates have already churned in 2026?",
    "Which corporates are declining vs 2025?",
    "Which corporates have the highest growth this year?",
    "Which industries are growing and which are declining?",
    "Which account managers have the highest churn risk?",
    "What are the top 5 retention priorities this week?",
    "Which corporates reduced rides in the last 2 weeks?",
    "Which corporates have the biggest growth opportunity?",
]

qq_cols = st.columns(3)
for i, q in enumerate(quick_questions):
    with qq_cols[i % 3]:
        if st.button(q, key=f"qq_{i}", use_container_width=True):
            st.session_state["chat_history"].append({"user": q, "bot": "..."})
            with st.spinner("Analysing data..."):
                answer = chat_with_bot(q, st.session_state["chat_history"][:-1])
            st.session_state["chat_history"][-1]["bot"] = answer
            st.rerun()

# ── Chat display ──────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for turn in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(turn["bot"])

# ── User input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about retention, churn, growth, or assignee performance…")
if user_input:
    st.session_state["chat_history"].append({"user": user_input, "bot": "..."})
    with st.spinner("Analysing data..."):
        answer = chat_with_bot(user_input, st.session_state["chat_history"][:-1])
    st.session_state["chat_history"][-1]["bot"] = answer
    st.rerun()

if st.session_state["chat_history"]:
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state["chat_history"] = []
        st.rerun()