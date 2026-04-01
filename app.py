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

HARDCODED_USERS = {
    "admin@little.africa": {
        "password": hash_password("admin123"),
        "role": "admin",
        "active": True,
        "created_at": "2025-01-01T00:00:00",
        "hardcoded": True
    },
    "monicah.wachira@little.africa": {
        "password": hash_password("A76cgFXvUWZfMON"),
        "role": "user",
        "active": True,
        "created_at": "2025-01-01T00:00:00",
        "hardcoded": True
    },
    "emily.njau@little.africa": {
        "password": hash_password("A76cgFXvUWZfEmI"),
        "role": "user",
        "active": True,
        "created_at": "2025-01-01T00:00:00",
        "hardcoded": True
    },
    "jael.davina@little.africa": {
        "password": hash_password("A76cgFXvUWZfJaE"),
        "role": "user",
        "active": True,
        "created_at": "2025-01-01T00:00:00",
        "hardcoded": True
    },
    "winnie.owendi@little.africa": {
        "password": hash_password("A76cgFXvUWZfWIn"),
        "role": "user",
        "active": True,
        "created_at": "2025-01-01T00:00:00",
        "hardcoded": True
    },
    "peter.mwangi@little.africa": {
        "password": hash_password("A76cgFXvUWZfPeT"),
        "role": "user",
        "active": True,
        "created_at": "2025-01-01T00:00:00",
        "hardcoded": True
    },
}

def load_users() -> dict:
    users = {k: v.copy() for k, v in HARDCODED_USERS.items()}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                saved = json.load(f)
            for email, info in saved.items():
                if email not in HARDCODED_USERS:
                    users[email] = info
                else:
                    users[email]["active"] = info.get("active", True)
                    if info.get("role"):
                        users[email]["role"] = info["role"]
        except Exception:
            pass
    return users

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
    .login-wrapper { display:flex; justify-content:center; align-items:center; padding-top:80px; }
    .login-box { background:#0000FF; color:white; padding:40px 48px; border-radius:12px;
                 text-align:center; max-width:420px; width:100%; }
    .login-box h2 { margin-bottom:4px; font-size:1.8rem; }
    .login-box p  { color:#c8c8ff; margin-bottom:28px; font-size:0.95rem; }
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
            "Email":   email,
            "Role":    info.get("role", "user"),
            "Status":  "✅ Active" if info.get("active", True) else "🚫 Revoked",
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
                st.write(""); st.write("")
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
        target_df         = pd.read_excel("data.xlsx", sheet_name="Target")
        data_2025_df      = pd.read_excel("data.xlsx", sheet_name="2025")
        data_2026_df      = pd.read_excel("data.xlsx", sheet_name="2026")
        data_2026_week_df = pd.read_excel("data.xlsx", sheet_name="2026_week_data")
        return target_df, data_2025_df, data_2026_df, data_2026_week_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

target_df, data_2025_df, data_2026_df, data_2026_week_df = load_data()
if target_df is None:
    st.stop()

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
MONTH_COLS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
WEEK_COLS  = [f"week {i}" for i in range(1, 14)]

current_user = st.session_state["current_user"]
current_role = st.session_state["current_role"]

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
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

    corporate = st.selectbox(
        "Corporate",
        ["All"] + sorted(target_df["Corporates"].dropna().unique()),
        key="sb_corporate"
    )
    industry = st.selectbox(
        "Industry",
        ["All"] + sorted(target_df["industry_"].dropna().unique()),
        key="sb_industry"
    )
    assignee = st.selectbox(
        "Assignee",
        ["All"] + sorted(target_df["Assignee_"].dropna().unique()),
        key="sb_assignee"
    )

    available_months_2026 = [m for m in MONTH_COLS if m in data_2026_df.columns]
    month_filter = st.selectbox(
        "Month (2026)",
        ["All"] + available_months_2026,
        key="sb_month"
    )

    st.markdown("---")
    st.markdown("### 🔴 Churn Filter")
    churn_period = st.selectbox(
        "Show Churned Corporates",
        ["None", "Churned (30 days)", "Churned (60 days)", "Churned (90 days)"],
        key="sb_churn"
    )

# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────
if current_role == "admin":
    with st.expander("🔐 Admin Panel – User Management", expanded=False):
        show_admin_panel()

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
# Filter using the Target sheet as master reference for industry/assignee,
# then propagate the matching Corporates list to all sheets.
# This avoids dropping corporates that exist in 2026 but lack metadata rows.

filtered_target    = target_df.copy()
filtered_2025      = data_2025_df.copy()
filtered_2026      = data_2026_df.copy()
filtered_2026_week = data_2026_week_df.copy()

if corporate != "All":
    filtered_target    = filtered_target[filtered_target["Corporates"] == corporate]
    filtered_2025      = filtered_2025[filtered_2025["Corporates"] == corporate]
    filtered_2026      = filtered_2026[filtered_2026["Corporates"] == corporate]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]

if industry != "All":
    corps_in_industry  = target_df[target_df["industry_"] == industry]["Corporates"].unique()
    filtered_target    = filtered_target[filtered_target["Corporates"].isin(corps_in_industry)]
    filtered_2025      = filtered_2025[filtered_2025["Corporates"].isin(corps_in_industry)]
    filtered_2026      = filtered_2026[filtered_2026["Corporates"].isin(corps_in_industry)]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Corporates"].isin(corps_in_industry)]

if assignee != "All":
    corps_by_assignee  = target_df[target_df["Assignee_"] == assignee]["Corporates"].unique()
    filtered_target    = filtered_target[filtered_target["Corporates"].isin(corps_by_assignee)]
    filtered_2025      = filtered_2025[filtered_2025["Corporates"].isin(corps_by_assignee)]
    filtered_2026      = filtered_2026[filtered_2026["Corporates"].isin(corps_by_assignee)]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Corporates"].isin(corps_by_assignee)]

months_2026 = available_months_2026 if month_filter == "All" else [month_filter]

if filtered_2026.empty:
    st.warning("No 2026 data available for the selected filters.")
    st.stop()

# ─────────────────────────────────────────────
# CHURN HELPER
# ─────────────────────────────────────────────
def get_churned_by_period(days: int) -> pd.DataFrame:
    weeks_threshold = max(1, min(days // 7, len(WEEK_COLS)))
    recent_cols = WEEK_COLS[-weeks_threshold:]
    not_in_2026 = set(data_2025_df["Corporates"]) - set(data_2026_df["Corporates"])
    zero_recent = set()
    if not data_2026_week_df.empty:
        wk = data_2026_week_df.copy()
        existing = [c for c in recent_cols if c in wk.columns]
        if existing:
            for c in existing:
                wk[c] = pd.to_numeric(wk[c], errors="coerce").fillna(0)
            wk["recent_total"] = wk[existing].sum(axis=1)
            zero_recent = set(wk[wk["recent_total"] == 0]["Corporates"])
    churned = not_in_2026 | zero_recent
    result = []
    for corp in churned:
        r25 = data_2025_df[data_2025_df["Corporates"] == corp]
        rt  = target_df[target_df["Corporates"] == corp]
        if not r25.empty:
            r25r = r25.iloc[0]
            rtr  = rt.iloc[0] if not rt.empty else None
            result.append({
                "Corporate":    corp,
                "Industry":     r25r.get("industry_", "—"),
                "Assignee":     r25r.get("Assignee_", "—"),
                "2025 Total":   float(r25r[[m for m in MONTH_COLS if m in r25r.index]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()),
                "Target":       float(rtr[[m for m in MONTH_COLS if m in rtr.index]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()) if rtr is not None else 0,
                "Churn Period": f"{days} days"
            })
    return pd.DataFrame(result)

# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────
st.title("🚕 Little Retention: Corporate Performance")

# ─────────────────────────────────────────────
# CHURN PERIOD VIEW
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
# AGGREGATION  ←  THE CORE FIX
#
# PROBLEM: Old code intersected corporates across all 3 sheets, so any
# corporate missing from even one sheet was silently dropped — causing
# totals to be lower than the Excel sheet totals.
#
# FIX: Sum each sheet independently, then outer-join the results.
# Every corporate from every sheet is preserved; missing values → 0.
# KPI totals come directly from the filtered sheet sums, not from any join.
# ─────────────────────────────────────────────

def sum_months(df: pd.DataFrame, month_cols: list, label: str) -> pd.DataFrame:
    """Return a Corporates + label dataframe with numeric month sums."""
    cols = [m for m in month_cols if m in df.columns]
    tmp  = df[["Corporates"] + cols].copy()
    for c in cols:
        tmp[c] = pd.to_numeric(tmp[c], errors="coerce").fillna(0)
    tmp[label] = tmp[cols].sum(axis=1)
    return tmp[["Corporates", label]]

totals_2026   = sum_months(filtered_2026,   months_2026, "2026")
totals_2025   = sum_months(filtered_2025,   months_2026, "2025")
totals_target = sum_months(filtered_target, months_2026, "Target")

# Outer-join — no corporates dropped
merged = (
    totals_2026
    .merge(totals_2025,   on="Corporates", how="outer")
    .merge(totals_target, on="Corporates", how="outer")
    .fillna(0)
)

# Attach industry / assignee metadata (target sheet is master; 2025 as fallback)
meta = (
    target_df[["Corporates","industry_","Assignee_"]]
    .drop_duplicates("Corporates")
)
meta_2025 = (
    data_2025_df[["Corporates","industry_","Assignee_"]]
    .drop_duplicates("Corporates")
    .rename(columns={"industry_":"ind_2025","Assignee_":"asn_2025"})
)
merged = merged.merge(meta, on="Corporates", how="left")
merged = merged.merge(meta_2025, on="Corporates", how="left")
merged["industry_"] = merged["industry_"].fillna(merged["ind_2025"]).fillna("—")
merged["Assignee_"] = merged["Assignee_"].fillna(merged["asn_2025"]).fillna("—")
merged = merged.drop(columns=["ind_2025","asn_2025"])

merged["% vs 2025"]   = merged.apply(
    lambda r: round((r["2026"]-r["2025"])/r["2025"]*100, 1) if r["2025"] != 0 else 0.0, axis=1)
merged["% vs Target"] = merged.apply(
    lambda r: round((r["2026"]-r["Target"])/r["Target"]*100, 1) if r["Target"] != 0 else 0.0, axis=1)

# ── KPI TOTALS: sum directly from each filtered sheet — no join filtering ──
total_2026   = totals_2026["2026"].sum()
total_2025   = totals_2025["2025"].sum()
total_target = totals_target["Target"].sum()
shortfall    = total_target - total_2026

active_corps   = filtered_2026["Corporates"].nunique()
churned_30     = get_churned_by_period(30)
num_churned_30 = len(churned_30)
growth_vs_target = round((total_2026-total_target)/total_target*100, 1) if total_target != 0 else 0.0
growth_vs_2025   = round((total_2026-total_2025)  /total_2025  *100, 1) if total_2025   != 0 else 0.0

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
st.header("📊 Key Performance Indicators")
st.markdown("""
<style>
.kpi-card { padding:16px 20px; border-radius:10px; text-align:center; margin-bottom:8px; }
.kpi-card .kpi-label { font-size:0.78rem; font-weight:600; opacity:0.85; margin-bottom:6px; }
.kpi-card .kpi-value { font-size:1.5rem; font-weight:700; }
.kpi-red    { background:#FF0000; color:white; }
.kpi-blue   { background:#0000FF; color:white; }
.kpi-yellow { background:#FFCC00; color:#1a1a1a; }
.kpi-green  { background:#00C853; color:white; }
.kpi-orange { background:#FF6D00; color:white; }
.kpi-teal   { background:#00796B; color:white; }
.kpi-pink   { background:#C2185B; color:white; }
</style>
""", unsafe_allow_html=True)

r1c1, r1c2, r1c3, r1c4 = st.columns(4)
with r1c1:
    st.markdown(f'<div class="kpi-card kpi-red"><div class="kpi-label">🎯 Total Target (2026)</div>'
                f'<div class="kpi-value">{total_target:,.0f}</div></div>', unsafe_allow_html=True)
with r1c2:
    st.markdown(f'<div class="kpi-card kpi-blue"><div class="kpi-label">📅 Total 2025</div>'
                f'<div class="kpi-value">{total_2025:,.0f}</div></div>', unsafe_allow_html=True)
with r1c3:
    st.markdown(f'<div class="kpi-card kpi-yellow"><div class="kpi-label">📅 Total 2026</div>'
                f'<div class="kpi-value">{total_2026:,.0f}</div></div>', unsafe_allow_html=True)
with r1c4:
    sf_cls = "kpi-orange" if shortfall > 0 else "kpi-green"
    sf_lbl = "⚠️ Shortfall to Target" if shortfall > 0 else "✅ Surplus vs Target"
    st.markdown(f'<div class="kpi-card {sf_cls}"><div class="kpi-label">{sf_lbl}</div>'
                f'<div class="kpi-value">{abs(shortfall):,.0f}</div></div>', unsafe_allow_html=True)

r2c1, r2c2, r2c3, r2c4 = st.columns(4)
with r2c1:
    gt_cls = "kpi-green" if growth_vs_target >= 0 else "kpi-red"
    gt_arr = "▲" if growth_vs_target >= 0 else "▼"
    st.markdown(f'<div class="kpi-card {gt_cls}"><div class="kpi-label">📈 Growth Rate vs Target</div>'
                f'<div class="kpi-value">{gt_arr} {abs(growth_vs_target):.1f}%</div></div>', unsafe_allow_html=True)
with r2c2:
    g25_cls = "kpi-green" if growth_vs_2025 >= 0 else "kpi-orange"
    g25_arr = "▲" if growth_vs_2025 >= 0 else "▼"
    st.markdown(f'<div class="kpi-card {g25_cls}"><div class="kpi-label">📈 Growth Rate vs 2025</div>'
                f'<div class="kpi-value">{g25_arr} {abs(growth_vs_2025):.1f}%</div></div>', unsafe_allow_html=True)
with r2c3:
    st.markdown(f'<div class="kpi-card kpi-teal"><div class="kpi-label">✅ Active Corporates (2026)</div>'
                f'<div class="kpi-value">{active_corps}</div></div>', unsafe_allow_html=True)
with r2c4:
    ch_cls = "kpi-pink" if num_churned_30 > 0 else "kpi-green"
    st.markdown(f'<div class="kpi-card {ch_cls}"><div class="kpi-label">🔴 Churned (Last 30 Days)</div>'
                f'<div class="kpi-value">{num_churned_30}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COMPARISON TABLE
# ─────────────────────────────────────────────
def fmt_pct(val):
    if val > 0:   return f"+{val:.1f}% 😍"
    elif val < 0: return f"{val:.1f}% 🤬"
    else:         return f"0.0% 😐"

display_df = merged.copy()
display_df["% vs 2025"]   = display_df["% vs 2025"].apply(fmt_pct)
display_df["% vs Target"] = display_df["% vs Target"].apply(fmt_pct)

st.header("📋 Comparison Table (2026 vs 2025 vs Target)")
st.dataframe(
    display_df
    .rename(columns={"Corporates":"Corporate","industry_":"Industry","Assignee_":"Assignee"})
    [["Corporate","Industry","Assignee","Target","2025","2026","% vs 2025","% vs Target"]]
    .sort_values("2026", ascending=False),
    use_container_width=True, hide_index=True
)

# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
st.header("📈 Performance Charts")

# Monthly aggregation — sum directly from each filtered sheet, per month
monthly_rows = []
for m in months_2026:
    def col_sum(df, col):
        if col not in df.columns:
            return 0.0
        return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()
    monthly_rows.append({
        "Month":  m,
        "Target": col_sum(filtered_target, m),
        "2025":   col_sum(filtered_2025,   m),
        "2026":   col_sum(filtered_2026,   m),
    })
monthly_chart_df = pd.DataFrame(monthly_rows)

col_c1, col_c2 = st.columns(2)
with col_c1:
    fig_line = go.Figure()
    clr = {"Target":"#FF0000","2025":"#0000FF","2026":"#00C853"}
    for metric in ["Target","2025","2026"]:
        fig_line.add_trace(go.Scatter(
            x=monthly_chart_df["Month"], y=monthly_chart_df[metric], name=metric,
            mode="lines+markers+text",
            text=monthly_chart_df[metric].round(0).astype(int).astype(str),
            textposition="top center",
            line=dict(width=2, color=clr[metric]), marker=dict(size=8)
        ))
    fig_line.update_layout(
        title="Monthly Performance: 2026 vs 2025 vs Target",
        xaxis_title="Month", yaxis_title="Revenue",
        template="plotly_white", height=400
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_c2:
    agg_asn = (
        merged.groupby("Assignee_")["2026"].sum()
        .reset_index().rename(columns={"Assignee_":"Assignee"})
        .sort_values("2026", ascending=False)
    )
    fig_pie = px.pie(
        agg_asn, names="Assignee", values="2026",
        title="2026 Revenue Breakdown by Assignee",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

col_c3, col_c4 = st.columns(2)
with col_c3:
    agg_ind = (
        merged.groupby("industry_")["2026"].sum()
        .reset_index().rename(columns={"industry_":"Industry"})
        .sort_values("2026", ascending=True)
    )
    fig_bar_ind = px.bar(
        agg_ind, x="2026", y="Industry", orientation="h",
        title="2026 Revenue by Industry",
        color="2026", color_continuous_scale="Blues"
    )
    fig_bar_ind.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_bar_ind, use_container_width=True)

with col_c4:
    yoy_show = merged[["Corporates","% vs 2025","2026"]].copy()
    top10 = yoy_show.nlargest(10, "% vs 2025")
    bot10 = yoy_show.nsmallest(10, "% vs 2025")
    yoy_combined = pd.concat([top10, bot10]).drop_duplicates().sort_values("% vs 2025", ascending=True)
    fig_yoy = px.bar(
        yoy_combined, x="% vs 2025", y="Corporates", orientation="h",
        title="Top Growth & Biggest Declines vs 2025 (%)",
        color="% vs 2025", color_continuous_scale="RdYlGn", color_continuous_midpoint=0
    )
    fig_yoy.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_yoy, use_container_width=True)

# Target attainment by assignee
st.header("🎯 Target Attainment by Assignee")
attain = (
    merged.groupby("Assignee_")[["Target","2026"]].sum()
    .reset_index().rename(columns={"Assignee_":"Assignee","2026":"Revenue 2026"})
)
attain["Attainment %"] = (attain["Revenue 2026"] / attain["Target"] * 100).replace([np.inf,-np.inf], 0).fillna(0).round(1)
fig_attain = px.bar(
    attain, x="Assignee", y="Attainment %",
    title="Target Attainment % per Assignee (2026)",
    color="Attainment %", color_continuous_scale="RdYlGn",
    color_continuous_midpoint=100, text="Attainment %"
)
fig_attain.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target = 100%")
fig_attain.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_attain.update_layout(height=400, showlegend=False)
st.plotly_chart(fig_attain, use_container_width=True)

# ─────────────────────────────────────────────
# WEEKLY TREND
# ─────────────────────────────────────────────
st.header("📅 2026 Weekly Trend per Corporate")
if not filtered_2026_week.empty:
    present_weeks = [w for w in WEEK_COLS if w in filtered_2026_week.columns]
    for col in present_weeks:
        filtered_2026_week[col] = pd.to_numeric(filtered_2026_week[col], errors="coerce").fillna(0)

    if corporate != "All":
        plot_df       = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]
        corps_to_plot = [corporate]
    else:
        total_rev     = filtered_2026_week[present_weeks].sum(axis=1)
        top_idx       = total_rev.nlargest(5).index
        plot_df       = filtered_2026_week.loc[top_idx]
        corps_to_plot = plot_df["Corporates"].unique()

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        fig_weekly = go.Figure()
        for corp in corps_to_plot:
            crow = plot_df[plot_df["Corporates"] == corp]
            if crow.empty:
                continue
            vals = [float(crow.iloc[0][w]) for w in present_weeks]
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
        if len(present_weeks) >= 2:
            heat_data = []
            for corp in corps_to_plot:
                crow = plot_df[plot_df["Corporates"] == corp]
                if crow.empty:
                    continue
                vals = [float(crow.iloc[0][w]) for w in present_weeks]
                heat_data.append([corp] + vals)
            if heat_data:
                heat_df = pd.DataFrame(heat_data, columns=["Corporate"] + present_weeks).set_index("Corporate")
                fig_heat = px.imshow(heat_df, title="Weekly Revenue Heatmap",
                                     color_continuous_scale="Blues", aspect="auto")
                fig_heat.update_layout(height=400)
                st.plotly_chart(fig_heat, use_container_width=True)

    def calc_slope(row):
        vals = [float(row.get(w, 0)) for w in present_weeks]
        if len(vals) < 2:
            return 0
        slope, _ = np.polyfit(range(len(vals)), vals, 1)
        return round(slope, 2)

    filtered_2026_week["Trend Slope"] = filtered_2026_week.apply(calc_slope, axis=1)
    st.dataframe(filtered_2026_week, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# CHURNED CORPORATES (Global)
# ─────────────────────────────────────────────
churned_all    = set(data_2025_df["Corporates"]) - set(data_2026_df["Corporates"])
churned_global = []
for corp in churned_all:
    rt  = target_df[target_df["Corporates"] == corp]
    r25 = data_2025_df[data_2025_df["Corporates"] == corp]
    if not r25.empty:
        r25r = r25.iloc[0]
        rtr  = rt.iloc[0] if not rt.empty else None
        churned_global.append({
            "Corporate":  corp,
            "Industry":   r25r.get("industry_", "—"),
            "Assignee":   r25r.get("Assignee_", "—"),
            "2025 Total": float(r25r[[m for m in MONTH_COLS if m in r25r.index]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()),
            "Target":     float(rtr[[m for m in MONTH_COLS if m in rtr.index]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()) if rtr is not None else 0,
        })

if churned_global:
    churned_global_df = pd.DataFrame(churned_global)
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
st.header("🤖 Retention Intelligence Bot")
st.markdown("Ask me anything about corporate retention, churn risk, growth opportunities, or assignee performance.")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

def build_bot_context() -> str:
    lines = []
    active_set  = set(data_2026_df["Corporates"])
    churned_set = set(data_2025_df["Corporates"]) - active_set
    lines.append(f"Active corporates in 2026: {len(active_set)}")
    lines.append(f"Churned (in 2025 but not 2026): {len(churned_set)}")
    if churned_set:
        lines.append("Churned list: " + ", ".join(sorted(churned_set)[:40]))

    lines.append("\n=== YoY per corporate ===")
    present_months_bot = [m for m in MONTH_COLS if m in data_2026_df.columns]
    all_corps = set(data_2026_df["Corporates"]) | set(data_2025_df["Corporates"])
    yoy_rows = []
    for corp in all_corps:
        r26 = data_2026_df[data_2026_df["Corporates"] == corp]
        r25 = data_2025_df[data_2025_df["Corporates"] == corp]
        v26 = float(r26.iloc[0][[m for m in present_months_bot if m in r26.columns]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()) if not r26.empty else 0.0
        v25 = float(r25.iloc[0][[m for m in present_months_bot if m in r25.columns]].apply(pd.to_numeric, errors="coerce").fillna(0).sum()) if not r25.empty else 0.0
        pct = round((v26-v25)/v25*100, 1) if v25 != 0 else 0.0
        rt  = target_df[target_df["Corporates"] == corp]
        ind = rt["industry_"].values[0] if not rt.empty else "—"
        asn = rt["Assignee_"].values[0] if not rt.empty else "—"
        yoy_rows.append((corp, v25, v26, pct, ind, asn))
    yoy_rows.sort(key=lambda x: x[3])
    for corp, v25, v26, pct, ind, asn in yoy_rows:
        lines.append(f"  {corp}: 2025={v25:,.0f}, 2026={v26:,.0f}, YoY={pct:+.1f}%, Industry={ind}, Assignee={asn}")

    lines.append("\n=== Weekly data ===")
    wk_df = data_2026_week_df.copy()
    present_wk = [c for c in WEEK_COLS if c in wk_df.columns]
    for c in present_wk:
        wk_df[c] = pd.to_numeric(wk_df[c], errors="coerce").fillna(0)
    if len(present_wk) >= 2:
        fh = present_wk[:len(present_wk)//2]
        sh = present_wk[len(present_wk)//2:]
        wk_df["fh"] = wk_df[fh].sum(axis=1)
        wk_df["sh"] = wk_df[sh].sum(axis=1)
        wk_df["trend"] = wk_df.apply(lambda r: round((r["sh"]-r["fh"])/r["fh"]*100,1) if r["fh"]!=0 else 0, axis=1)
        for _, row in wk_df.iterrows():
            rt  = target_df[target_df["Corporates"]==row["Corporates"]]
            asn = rt["Assignee_"].values[0] if not rt.empty else "—"
            ind = rt["industry_"].values[0] if not rt.empty else "—"
            wvals = ", ".join([f"{row.get(w,0):.0f}" for w in present_wk])
            lines.append(f"  {row['Corporates']}: weeks=[{wvals}], trend={row['trend']:+.1f}%, Assignee={asn}, Industry={ind}")

    lines.append(f"\n=== Totals ===")
    lines.append(f"Total target: {total_target:,.0f}")
    lines.append(f"Total 2026:   {total_2026:,.0f}")
    lines.append(f"Total 2025:   {total_2025:,.0f}")
    lines.append(f"Shortfall:    {shortfall:,.0f}")
    lines.append(f"Growth vs target: {growth_vs_target:+.1f}%")
    lines.append(f"Growth vs 2025:   {growth_vs_2025:+.1f}%")

    lines.append("\n=== Industry performance ===")
    for _, row in merged.groupby("industry_")[["2025","2026"]].sum().reset_index().iterrows():
        p = round((row["2026"]-row["2025"])/row["2025"]*100,1) if row["2025"]!=0 else 0
        lines.append(f"  {row['industry_']}: 2025={row['2025']:,.0f}, 2026={row['2026']:,.0f}, YoY={p:+.1f}%")

    lines.append("\n=== Assignee performance ===")
    for _, row in merged.groupby("Assignee_")[["2025","2026"]].sum().reset_index().iterrows():
        p = round((row["2026"]-row["2025"])/row["2025"]*100,1) if row["2025"]!=0 else 0
        lines.append(f"  {row['Assignee_']}: 2025={row['2025']:,.0f}, 2026={row['2026']:,.0f}, YoY={p:+.1f}%")

    return "\n".join(lines)

SYSTEM_PROMPT = """You are the Little Retention Intelligence Bot — an expert analyst for Little Africa's corporate taxi retention team.

Use the data below to give precise, actionable, structured answers.
Always include: corporate name, assignee, industry, revenue figures, % change where relevant.
Flag churn risk when weekly trend is declining >30% or YoY is negative.
Ground every answer in the data. If something is not in the data, say so clearly.

=== RETENTION DATA ===
{context}
=== END DATA ===
"""

def chat_with_bot(user_message: str, history: list) -> str:
    import urllib.request, urllib.error

    api_key = ""
    try:
        api_key = str(st.secrets["ANTHROPIC_API_KEY"]).strip()
    except Exception:
        pass

    HARDCODED_API_KEY = ""  # ← paste sk-ant-... here if not using secrets
    if not api_key:
        api_key = HARDCODED_API_KEY.strip()

    if not api_key or not api_key.startswith("sk-"):
        return (
            "⚠️ **Bot not configured — API key missing.**\n\n"
            "In Streamlit Cloud → your app → ⚙️ Settings → Secrets, add:\n"
            "```\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```"
        )

    context  = build_bot_context()
    system   = SYSTEM_PROMPT.format(context=context)
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
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return f"⚠️ API error {e.code}: {body}"
    except Exception as e:
        return f"⚠️ Bot error: {e}"

# Quick questions
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

# Chat display
for turn in st.session_state["chat_history"]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(turn["bot"])

# Chat input
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