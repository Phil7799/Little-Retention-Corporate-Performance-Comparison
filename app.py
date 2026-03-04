import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import json
import hashlib
import re
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Little Retention",
    page_icon="https://res.cloudinary.com/dnq8ne9lx/image/upload/v1753860594/infograph_ewfmm6.ico",
    layout="wide"
)

# ─────────────────────────────────────────────
# AUTH CONFIG
# ─────────────────────────────────────────────
ADMIN_EMAIL = "admin@little.africa"          # ← change to your actual email
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retention_users.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        initial = {
            ADMIN_EMAIL: {
                "password": hash_password("admin123"),  # ← change admin password here
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
# LOGGED-IN SIDEBAR HEADER
# ─────────────────────────────────────────────
current_user = st.session_state["current_user"]
current_role = st.session_state["current_role"]

with st.sidebar:
    st.markdown(f"""
    <div style='background:#0000FF;color:white;padding:12px 16px;border-radius:8px;margin-bottom:12px;font-size:0.85rem;'>
        👤 <b>{current_user}</b><br>
        <span style='color:#c8c8ff;font-size:0.78rem;'>{current_role.capitalize()}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Sign Out"):
        for key in ["authenticated", "current_user", "current_role"]:
            st.session_state.pop(key, None)
        st.rerun()

# ─────────────────────────────────────────────
# ADMIN PANEL (admins only)
# ─────────────────────────────────────────────
if current_role == "admin":
    with st.expander("🔐 Admin Panel – User Management", expanded=False):
        show_admin_panel()

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

@st.cache_data
def load_data():
    try:
        target_df = pd.read_excel("data.xlsx", sheet_name="Target")
        data_2025_df = pd.read_excel("data.xlsx", sheet_name="2025")
        data_2026_df = pd.read_excel("data.xlsx", sheet_name="2026")
        data_2026_week_df = pd.read_excel("data.xlsx", sheet_name="2026_week_data")
        return target_df, data_2025_df, data_2026_df, data_2026_week_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

target_df, data_2025_df, data_2026_df, data_2026_week_df = load_data()

if target_df is None or data_2025_df is None or data_2026_df is None or data_2026_week_df is None:
    st.stop()

# Title
st.title(" Little 🚕 Retention: Corporate Performance Comparison")

# Search functionality
st.header("Search")
col1, col2, col3 = st.columns(3)
with col1:
    corporate = st.selectbox("Select Corporate", ["All"] + sorted(target_df["Corporates"].unique()))
with col2:
    industry = st.selectbox("Select Industry", ["All"] + sorted(target_df["industry_"].unique()))
with col3:
    assignee = st.selectbox("Select Assignee", ["All"] + sorted(target_df["Assignee_"].unique()))

# Filter data based on search criteria
filtered_target = target_df.copy()
filtered_2025 = data_2025_df.copy()
filtered_2026 = data_2026_df.copy()
filtered_2026_week = data_2026_week_df.copy()

if corporate != "All":
    filtered_target = filtered_target[filtered_target["Corporates"] == corporate]
    filtered_2025 = filtered_2025[filtered_2025["Corporates"] == corporate]
    filtered_2026 = filtered_2026[filtered_2026["Corporates"] == corporate]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]

if industry != "All":
    filtered_target = filtered_target[filtered_target["industry_"] == industry]
    filtered_2025 = filtered_2025[filtered_2025["industry_"] == industry]
    filtered_2026 = filtered_2026[filtered_2026["industry_"] == industry]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["industry_"] == industry]

if assignee != "All":
    filtered_target = filtered_target[filtered_target["Assignee_"] == assignee]
    filtered_2025 = filtered_2025[filtered_2025["Assignee_"] == assignee]
    filtered_2026 = filtered_2026[filtered_2026["Assignee_"] == assignee]
    filtered_2026_week = filtered_2026_week[filtered_2026_week["Assignee_"] == assignee]

if filtered_target.empty or filtered_2025.empty or filtered_2026.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Prepare data for comparison table
months_2026 = ["Jan", "Feb"]
comparison_data = []

common_corporates = set(filtered_target["Corporates"]).intersection(
    set(filtered_2025["Corporates"]), set(filtered_2026["Corporates"])
)

if not common_corporates:
    st.warning("No common corporates found across all datasets for the selected filters.")
    st.stop()

for corp in common_corporates:
    row_target = filtered_target[filtered_target["Corporates"] == corp].iloc[0]
    row_2025 = filtered_2025[filtered_2025["Corporates"] == corp].iloc[0]
    row_2026 = filtered_2026[filtered_2026["Corporates"] == corp].iloc[0]

    for month in months_2026:
        target_val = row_target.get(month, 0)
        val_2025 = row_2025.get(month, 0)
        val_2026 = row_2026.get(month, 0)
        pct_change_2025 = ((val_2026 - val_2025) / val_2025 * 100) if val_2025 != 0 else 0
        pct_change_target = ((val_2026 - target_val) / target_val * 100) if target_val != 0 else 0
        comparison_data.append({
            "Corporate": corp,
            "Month": month,
            "Target": float(target_val),
            "2025": float(val_2025),
            "2026": float(val_2026),
            "Industry": row_target["industry_"],
            "Assignee": row_target["Assignee_"],
            "% Comparison to 2025": pct_change_2025,
            "% Comparison to Target": pct_change_target
        })

comparison_df_table = pd.DataFrame(comparison_data)

def format_percentage(val):
    if val > 0:
        return f"{val:.2f}% 😍"
    elif val < 0:
        return f"{val:.2f}% 🤬"
    else:
        return f"{val:.2f}% 😐"

comparison_df_table["% Comparison to 2025"] = comparison_df_table["% Comparison to 2025"].apply(format_percentage)
comparison_df_table["% Comparison to Target"] = comparison_df_table["% Comparison to Target"].apply(format_percentage)

comparison_data_chart = []
for month in months_2026:
    target_sum = filtered_target[month].sum()
    val_2025_sum = filtered_2025[month].sum()
    val_2026_sum = filtered_2026[month].sum()
    comparison_data_chart.append({
        "Month": month,
        "Target": float(target_sum),
        "2025": float(val_2025_sum),
        "2026": float(val_2026_sum)
    })

comparison_df_chart = pd.DataFrame(comparison_data_chart)

# KPI Metrics
st.header("Key Performance Indicators")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

total_target = comparison_df_chart["Target"].sum()
total_2025 = comparison_df_chart["2025"].sum()
total_2026 = comparison_df_chart["2026"].sum()
shortfall = total_target - total_2026

st.markdown("""
    <style>
    .kpi-red { background-color: #FF0000; color: white; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    .kpi-blue { background-color: #0000FF; color: white; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    .kpi-yellow { background-color: #FFFF00; color: black; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    .kpi-green { background-color: #00FF00; color: black; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

with col_kpi1:
    st.markdown(f'<div class="kpi-red">Total Target (2026): {total_target:,.2f}</div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="kpi-blue">Total 2025: {total_2025:,.2f}</div>', unsafe_allow_html=True)
with col_kpi3:
    st.markdown(f'<div class="kpi-yellow">Total 2026: {total_2026:,.2f}</div>', unsafe_allow_html=True)
with col_kpi4:
    st.markdown(f'<div class="kpi-green">Shortfall to Target: {shortfall:,.2f}</div>', unsafe_allow_html=True)

# Comparison table
st.header("Comparison Table (2026 vs 2025 vs Target)")
st.dataframe(comparison_df_table, use_container_width=True)

# Performance chart
st.header("Performance Comparison Chart")
fig = go.Figure()
for metric in ["Target", "2025", "2026"]:
    fig.add_trace(go.Scatter(
        x=comparison_df_chart["Month"],
        y=comparison_df_chart[metric],
        name=metric,
        mode="lines+markers+text",
        text=comparison_df_chart[metric].round(2).astype(str),
        textposition="top center",
        line=dict(width=2),
        marker=dict(size=8)
    ))
fig.update_layout(
    title="Performance Comparison by Month (Aggregated)",
    xaxis_title="Month",
    yaxis_title="Amount",
    template="plotly_white",
    height=600,
    showlegend=True
)
st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# Advice
advice = ""
if total_2026 >= total_target:
    advice = "Great job💥! The 2026 performance has met or exceeded the target. Continue maintaining high performance and explore opportunities to sustain or further improve results."
else:
    advice = f"You need to do better 👎🏻!. To meet the target, an additional {shortfall:,.2f} is needed. Consider the following strategies:\n"
    advice += "- **Increase Engagement**: Enhance client outreach through targeted marketing campaigns.\n"
    advice += "- **Optimize Operations**: Streamline processes to improve efficiency and reduce costs.\n"
    advice += "- **Upsell Opportunities**: Identify cross-selling or upselling opportunities with existing clients.\n"
    advice += "- **Training**: Provide additional training to corporate users to boost productivity."

st.header("Summary Note")
st.markdown(f"""
**Total Target (2026)**: {total_target:,.2f}  
**Total 2025**: {total_2025:,.2f}  
**Total 2026**: {total_2026:,.2f}  
**Shortfall to Target**: {shortfall:,.2f}  
**Advice**:  
{advice}
""")

# Churned corporates
churned_corporates = set(data_2025_df["Corporates"]) - set(data_2026_df["Corporates"])
churned_data = []
for corp in churned_corporates:
    if corp in target_df["Corporates"].values:
        row_target = target_df[target_df["Corporates"] == corp].iloc[0]
        row_2025 = data_2025_df[data_2025_df["Corporates"] == corp].iloc[0]
        total_target_corp = row_target[["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]].sum()
        total_2025_corp = row_2025[["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]].sum()
        churned_data.append({
            "Corporate": corp,
            "Industry": row_target["industry_"],
            "Assignee": row_target["Assignee_"],
            "Target": float(total_target_corp),
            "2025 Total": float(total_2025_corp)
        })

churned_df = pd.DataFrame(churned_data)
if not churned_df.empty:
    st.header("Churned Corporates (Active in 2025, Inactive in 2026)")
    st.dataframe(churned_df, use_container_width=True)
else:
    st.info("No churned corporates found (all corporates active in 2026).")

# 2026 Weekly Data
st.header("2026 Weekly Data Trend")
if not filtered_2026_week.empty:
    def calculate_slope(row):
        weeks = [float(row[f'week {i}']) for i in range(1, 7) if pd.notna(row[f'week {i}'])]
        x = list(range(1, len(weeks) + 1))
        if np.any(weeks):
            slope, _ = np.polyfit(x, weeks, 1)
        else:
            slope = 0
        return slope

    weekly_cols = [f'week {i}' for i in range(1, 7)]
    for col in weekly_cols:
        filtered_2026_week[col] = pd.to_numeric(filtered_2026_week[col], errors='coerce').fillna(0)

    filtered_2026_week['Slope'] = filtered_2026_week.apply(calculate_slope, axis=1)
    st.dataframe(filtered_2026_week, use_container_width=True)
else:
    st.info("No weekly data available for the selected filters.")

# Weekly trend chart
st.header("2026 Weekly Trend per Corporate")
if not filtered_2026_week.empty:
    if corporate != "All" and industry == "All" and assignee == "All":
        plot_df = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]
        corporates_to_plot = [corporate]
    else:
        total_revenue = filtered_2026_week[weekly_cols].sum(axis=1)
        top_corporates = filtered_2026_week.loc[total_revenue.nlargest(5).index, "Corporates"].unique()
        plot_df = filtered_2026_week[filtered_2026_week["Corporates"].isin(top_corporates)]
        corporates_to_plot = top_corporates

    fig_weekly = go.Figure()
    weeks = [f"week {i}" for i in range(1, 7)]
    for corp in corporates_to_plot:
        corp_data = plot_df[plot_df["Corporates"] == corp].iloc[0]
        weekly_values = [float(corp_data[week]) for week in weeks]
        fig_weekly.add_trace(go.Scatter(
            x=weeks,
            y=weekly_values,
            mode="lines+markers",
            name=corp,
            line=dict(width=2),
            marker=dict(size=6)
        ))
    fig_weekly.update_layout(
        title="2026 Weekly Revenue Trend",
        xaxis_title="Week",
        yaxis_title="Revenue",
        template="plotly_white",
        height=600,
        showlegend=True
    )
    st.plotly_chart(fig_weekly, use_container_width=True, config={"responsive": True})
else:
    st.info("No weekly data available to plot.")