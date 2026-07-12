import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_data

st.set_page_config(
    page_title="Spending Insights | TransitLens",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Spending Insights")
st.markdown("""
Deep dive into your transit spending patterns. See where your money goes and identify potential savings.

---
""")

df = get_data()

try:
    # Key spending metrics
    st.subheader("📊 Spending Overview")
    
    total_spent = df["Amount_Clean"].sum()
    avg_per_trip = df["Amount_Clean"].mean()
    avg_per_day = df.groupby("Date_Only")["Amount_Clean"].sum().mean()
    
    # Calculate date range
    date_range = (df["Date"].max() - df["Date"].min()).days
    months_covered = max(date_range / 30, 1)
    avg_monthly = total_spent / months_covered
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total Spent", f"${total_spent:.2f}")
    col2.metric("🎫 Avg per Trip", f"${avg_per_trip:.2f}")
    col3.metric("📅 Avg per Day", f"${avg_per_day:.2f}")
    col4.metric("📆 Avg per Month", f"${avg_monthly:.2f}")

    st.markdown("---")
    
    # Monthly spending trend
    st.subheader("📈 Monthly Spending Trend")
    
    monthly_spending = df.groupby("Month")["Amount_Clean"].sum()
    
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Scatter(
        x=monthly_spending.index,
        y=monthly_spending.values,
        mode='lines+markers',
        name='Monthly Spending',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10)
    ))
    
    # Add average line
    fig_monthly.add_hline(
        y=monthly_spending.mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: ${monthly_spending.mean():.2f}"
    )
    
    fig_monthly.update_layout(
        title="Monthly Transit Spending Over Time",
        xaxis_title="Month",
        yaxis_title="Amount Spent ($)"
    )
    st.plotly_chart(fig_monthly, width="stretch")
    
    # Month with highest/lowest spending
    col1, col2 = st.columns(2)
    highest_month = monthly_spending.idxmax()
    lowest_month = monthly_spending.idxmin()
    col1.success(f"💸 Highest spending month: **{highest_month}** (${monthly_spending.max():.2f})")
    col2.info(f"💰 Lowest spending month: **{lowest_month}** (${monthly_spending.min():.2f})")

    st.markdown("---")
    
    # Spending by agency
    st.subheader("🚌 Spending by Transit Agency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        agency_spending = df.groupby("Transit Agency")["Amount_Clean"].sum().sort_values(ascending=False)
        
        fig_agency = px.pie(
            values=agency_spending.values,
            names=agency_spending.index,
            title="Spending Distribution by Agency",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_agency, width="stretch")
    
    with col2:
        # Average fare by agency
        agency_avg = df.groupby("Transit Agency")["Amount_Clean"].mean().sort_values(ascending=False)
        
        fig_avg = px.bar(
            x=agency_avg.values,
            y=agency_avg.index,
            orientation='h',
            title="Average Fare by Transit Agency",
            color=agency_avg.values,
            color_continuous_scale="Greens"
        )
        fig_avg.update_layout(
            xaxis_title="Average Fare ($)",
            yaxis_title="Transit Agency",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_avg, width="stretch")

    st.markdown("---")

    # Spending by location
    st.subheader("📍 Top Spending Locations")
    
    location_spending = df.groupby("Location")["Amount_Clean"].sum().sort_values(ascending=False).head(10)
    
    fig_loc = px.bar(
        x=location_spending.values,
        y=location_spending.index,
        orientation='h',
        title="Top 10 Locations by Total Spending",
        color=location_spending.values,
        color_continuous_scale="Reds"
    )
    fig_loc.update_layout(
        xaxis_title="Total Spent ($)",
        yaxis_title="Location",
        coloraxis_showscale=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_loc, width="stretch")

    st.markdown("---")
    
    # Cost per trip analysis
    st.subheader("🎫 Fare Analysis")

    fare_data = df[df["Amount_Clean"] > 0]["Amount_Clean"]

    # Average fare per month - shows fare increases and mode-mix shifts
    monthly_avg_fare = df.groupby("Month")["Amount_Clean"].mean()

    fig_avg_fare = px.line(
        x=monthly_avg_fare.index,
        y=monthly_avg_fare.values,
        title="Average Fare per Month",
        markers=True
    )
    fig_avg_fare.update_layout(
        xaxis_title="Month",
        yaxis_title="Average Fare ($)"
    )
    fig_avg_fare.update_traces(line_color="#9b59b6", line_width=3, marker_size=10)
    st.plotly_chart(fig_avg_fare, width="stretch")

    # Fare statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Most Common Fare", f"${fare_data.mode().iloc[0]:.2f}" if not fare_data.mode().empty else "N/A")
    col2.metric("Median Fare", f"${fare_data.median():.2f}")
    col3.metric("Max Fare", f"${fare_data.max():.2f}")

    st.markdown("---")
    
    # Cumulative spending
    st.subheader("📈 Cumulative Spending Over Time")
    
    df_sorted = df.sort_values("Date").copy()
    df_sorted["Cumulative_Spending"] = df_sorted["Amount_Clean"].cumsum()
    
    fig_cumulative = px.area(
        df_sorted,
        x="Date",
        y="Cumulative_Spending",
        title="Cumulative Transit Spending",
        color_discrete_sequence=["#27ae60"]
    )
    fig_cumulative.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative Amount ($)"
    )
    st.plotly_chart(fig_cumulative, width="stretch")
    
    # Projection
    if months_covered > 0:
        projected_annual = (total_spent / months_covered) * 12
        st.info(f"📊 Based on your current spending rate, your projected annual transit spending is **${projected_annual:.2f}**")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please make sure your data is loaded correctly from the main Dashboard page.")
