import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, clean_raw_data, get_session_data

st.set_page_config(
    page_title="Travel Patterns | TransitLens",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Travel Patterns Analysis")
st.markdown("""
Discover when you travel most frequently! Analyze your transit usage by day of week and time of day.

---
""")

# Try to get data from session state or load fresh
df = get_session_data()
if df is None:
    st.sidebar.header("📁 Data Upload")
    uploaded_csv = st.sidebar.file_uploader("Upload your Presto CSV:", type="csv")
    if not uploaded_csv:
        uploaded_csv = "transit_usage.csv"
    df = load_data(uploaded_csv)
    df = clean_raw_data(df)

try:
    # Day of Week Analysis
    st.subheader("📊 Trips by Day of Week")
    
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = df["Day_of_Week"].value_counts().reindex(day_order).fillna(0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_day = px.bar(
            x=day_counts.index,
            y=day_counts.values,
            title="Trip Distribution by Day of Week",
            color=day_counts.values,
            color_continuous_scale="Blues"
        )
        fig_day.update_layout(
            xaxis_title="Day of Week",
            yaxis_title="Number of Trips",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_day, use_container_width=True)
        
        # Find busiest day
        busiest_day = day_counts.idxmax()
        st.info(f"🏆 Your busiest travel day is **{busiest_day}** with {int(day_counts.max())} trips!")
    
    with col2:
        # Weekday vs Weekend
        weekday_mask = df["Day_of_Week"].isin(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        weekday_trips = weekday_mask.sum()
        weekend_trips = len(df) - weekday_trips
        
        fig_pie = px.pie(
            values=[weekday_trips, weekend_trips],
            names=["Weekday", "Weekend"],
            title="Weekday vs Weekend Travel",
            color_discrete_sequence=["#3498db", "#e74c3c"]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    # Hourly Analysis
    st.subheader("⏰ Trips by Hour of Day")
    
    hour_counts = df["Hour"].value_counts().sort_index()
    # Fill missing hours with 0
    all_hours = pd.Series(index=range(24), data=0)
    all_hours.update(hour_counts)
    
    fig_hour = px.bar(
        x=all_hours.index,
        y=all_hours.values,
        title="Trip Distribution by Hour",
        color=all_hours.values,
        color_continuous_scale="Oranges"
    )
    fig_hour.update_layout(
        xaxis_title="Hour of Day (24h)",
        yaxis_title="Number of Trips",
        coloraxis_showscale=False,
        xaxis=dict(tickmode='linear', dtick=1)
    )
    st.plotly_chart(fig_hour, use_container_width=True)
    
    # Peak hours analysis
    col1, col2, col3 = st.columns(3)
    peak_hour = all_hours.idxmax()
    
    morning_rush = all_hours[6:10].sum()
    evening_rush = all_hours[16:20].sum()
    off_peak = all_hours.sum() - morning_rush - evening_rush
    
    col1.metric("🌅 Morning Rush (6-10AM)", f"{int(morning_rush)} trips")
    col2.metric("🌆 Evening Rush (4-8PM)", f"{int(evening_rush)} trips")
    col3.metric("🌙 Off-Peak Hours", f"{int(off_peak)} trips")

    st.markdown("---")
    
    # Heatmap: Day vs Hour
    st.subheader("🔥 Travel Heatmap: Day × Hour")
    
    heatmap_data = df.groupby(["Day_of_Week", "Hour"]).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(day_order)
    
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Hour of Day", y="Day of Week", color="Trips"),
        title="When Do You Travel Most?",
        color_continuous_scale="YlOrRd",
        aspect="auto"
    )
    fig_heatmap.update_layout(
        xaxis=dict(tickmode='linear', dtick=2)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Monthly trends
    st.subheader("📈 Monthly Travel Trends")
    
    monthly_trips = df.groupby("Month").size()
    
    fig_monthly = px.line(
        x=monthly_trips.index,
        y=monthly_trips.values,
        title="Trips Over Time by Month",
        markers=True
    )
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Trips"
    )
    fig_monthly.update_traces(line_color="#3498db", line_width=3, marker_size=10)
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Calculate average trips per month
    avg_monthly = monthly_trips.mean()
    st.info(f"📊 On average, you take **{avg_monthly:.1f} trips per month**")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please make sure your data is loaded correctly from the main Dashboard page.")
