import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from uuid import uuid4

# Set page configuration
st.set_page_config(page_title="Little Retention", page_icon="https://res.cloudinary.com/dnq8ne9lx/image/upload/v1753860594/infograph_ewfmm6.ico", layout="wide")

# Function to load data
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

# Load data
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

# Ensure we have data to display
if filtered_target.empty or filtered_2025.empty or filtered_2026.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Prepare data for comparison table with corporate names
months_2026 = ["Jan"]
comparison_data = []

# Merge DataFrames to ensure consistent corporates
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
        # Calculate percentage comparisons
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

# Convert to DataFrame for table
comparison_df_table = pd.DataFrame(comparison_data)

# Function to format percentage with emoji
def format_percentage(val):
    if val > 0:
        return f"{val:.2f}% 😍"
    elif val < 0:
        return f"{val:.2f}% 🤬"
    else:
        return f"{val:.2f}% 😐"

# Apply percentage formatting to the DataFrame
comparison_df_table["% Comparison to 2025"] = comparison_df_table["% Comparison to 2025"].apply(format_percentage)
comparison_df_table["% Comparison to Target"] = comparison_df_table["% Comparison to Target"].apply(format_percentage)

# Prepare aggregated data for chart
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

# KPI Metrics with custom colors
st.header("Key Performance Indicators")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
total_target = comparison_df_chart["Target"].sum()
total_2025 = comparison_df_chart["2025"].sum()
total_2026 = comparison_df_chart["2026"].sum()
shortfall = total_target - total_2026

# Custom CSS for colored KPIs
st.markdown(
    """
    <style>
    .kpi-red { background-color: #FF0000; color: white; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    .kpi-blue { background-color: #0000FF; color: white; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    .kpi-yellow { background-color: #FFFF00; color: black; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    .kpi-green { background-color: #00FF00; color: black; padding: 20px; font-size: 24px; font-style: italic; border-radius: 5px; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True
)

with col_kpi1:
    st.markdown(f'<div class="kpi-red">Total Target (2026): {total_target:,.2f}</div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="kpi-blue">Total 2025: {total_2025:,.2f}</div>', unsafe_allow_html=True)
with col_kpi3:
    st.markdown(f'<div class="kpi-yellow">Total 2026: {total_2026:,.2f}</div>', unsafe_allow_html=True)
with col_kpi4:
    st.markdown(f'<div class="kpi-green">Shortfall to Target: {shortfall:,.2f}</div>', unsafe_allow_html=True)

# Display comparison table
st.header("Comparison Table (2026 vs 2025 vs Target)")
st.dataframe(comparison_df_table, use_container_width=True)

# Plot comparison using Plotly (Line Chart with aggregated data)
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

# Advice based on performance
advice = ""
if total_2026 >= total_target:
    advice = "Great job💥! The 2026 performance has met or exceeded the target. Continue maintaining high performance and explore opportunities to sustain or further improve results."
else:
    advice = f"You need to do better 👎🏻!. To meet the target, an additional {shortfall:,.2f} is needed. Consider the following strategies:\n"
    advice += "- **Increase Engagement**: Enhance client outreach through targeted marketing campaigns.\n"
    advice += "- **Optimize Operations**: Streamline processes to improve efficiency and reduce costs.\n"
    advice += "- **Upsell Opportunities**: Identify cross-selling or upselling opportunities with existing clients.\n"
    advice += "- **Training**: Provide additional training to corporate users to boost productivity."

# Display summary note
st.header("Summary Note")
st.markdown(f"""
**Total Target (2026)**: {total_target:,.2f}  
**Total 2025**: {total_2025:,.2f}  
**Total 2026**: {total_2026:,.2f}  
**Shortfall to Target**: {shortfall:,.2f}  

**Advice**:  
{advice}
""")

# Prepare data for churned corporates table
churned_corporates = set(data_2025_df["Corporates"]) - set(data_2026_df["Corporates"])
churned_data = []

for corp in churned_corporates:
    if corp in target_df["Corporates"].values:  # Ensure the corporate exists in Target sheet
        row_target = target_df[target_df["Corporates"] == corp].iloc[0]
        row_2025 = data_2025_df[data_2025_df["Corporates"] == corp].iloc[0]
        total_target = row_target[["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]].sum()
        total_2025 = row_2025[["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]].sum()
        churned_data.append({
            "Corporate": corp,
            "Industry": row_target["industry_"],
            "Assignee": row_target["Assignee_"],
            "Target": float(total_target),
            "2025 Total": float(total_2025)
        })

# Convert to DataFrame for churned corporates table
churned_df = pd.DataFrame(churned_data)

# Display churned corporates table
if not churned_df.empty:
    st.header("Churned Corporates (Active in 2025, Inactive in 2026)")
    st.dataframe(churned_df, use_container_width=True)
else:
    st.info("No churned corporates found (all corporates active in 2026).")

# Display 2026 Weekly Data Trend Table
st.header("2026 Weekly Data Trend")
if not filtered_2026_week.empty:
    def calculate_slope(row):
        weeks = [float(row[f'week {i}']) for i in range(1, 5) if pd.notna(row[f'week {i}'])]
        x = list(range(1, len(weeks) + 1))
        if np.any(weeks):  # Avoid all zeros
            slope, _ = np.polyfit(x, weeks, 1)
        else:
            slope = 0
        return slope

    # Convert weekly columns to numeric, coercing errors to NaN
    weekly_cols = [f'week {i}' for i in range(1, 5)]
    for col in weekly_cols:
        filtered_2026_week[col] = pd.to_numeric(filtered_2026_week[col], errors='coerce').fillna(0)

    filtered_2026_week['Slope'] = filtered_2026_week.apply(calculate_slope, axis=1)
    st.dataframe(filtered_2026_week, use_container_width=True)
else:
    st.info("No weekly data available for the selected filters.")

# Plot 2025 Weekly Trend Line Graph
st.header("2026 Weekly Trend per Corporate")
if not filtered_2026_week.empty:
    # Determine which corporates to plot
    if corporate != "All" and industry == "All" and assignee == "All":
        # Show trend for the selected corporate
        plot_df = filtered_2026_week[filtered_2026_week["Corporates"] == corporate]
        corporates_to_plot = [corporate]
    else:
        # Show top 5 corporates by total revenue when no corporate filter or other filters are applied
        total_revenue = filtered_2026_week[weekly_cols].sum(axis=1)
        top_corporates = filtered_2026_week.loc[total_revenue.nlargest(5).index, "Corporates"].unique()
        plot_df = filtered_2026_week[filtered_2026_week["Corporates"].isin(top_corporates)]
        corporates_to_plot = top_corporates

    fig_weekly = go.Figure()
    weeks = [f"week {i}" for i in range(1, 5)]
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
        title="2025 Weekly Revenue Trend",
        xaxis_title="Week",
        yaxis_title="Revenue",
        template="plotly_white",
        height=600,
        showlegend=True
    )
    st.plotly_chart(fig_weekly, use_container_width=True, config={"responsive": True})
else:
    st.info("No weekly data available to plot.")