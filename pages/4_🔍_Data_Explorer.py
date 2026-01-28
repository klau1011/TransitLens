import pandas as pd
import plotly.express as px
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, clean_raw_data, get_session_data

st.set_page_config(
    page_title="Data Explorer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Data Explorer")
st.markdown("""
Explore and filter your raw transit data. Search for specific trips, filter by date range, agency, and more.

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
    st.subheader("🎛️ Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date range filter
        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()
        date_range = st.date_input(
            "Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        # Agency filter
        agencies = ["All"] + list(df["Transit Agency"].unique())
        selected_agency = st.selectbox("Transit Agency:", agencies)
    
    with col3:
        # Location search
        location_search = st.text_input("Search Location:", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_date) & 
            (filtered_df["Date"].dt.date <= end_date)
        ]
    
    if selected_agency != "All":
        filtered_df = filtered_df[filtered_df["Transit Agency"] == selected_agency]
    
    if location_search:
        filtered_df = filtered_df[
            filtered_df["Location"].str.contains(location_search, case=False, na=False)
        ]
    
    # Display stats for filtered data
    st.markdown("---")
    st.subheader("📊 Filtered Data Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trips", len(filtered_df))
    col2.metric("Unique Locations", filtered_df["Location"].nunique())
    col3.metric("Total Spent", f"${filtered_df['Amount_Clean'].sum():.2f}")
    col4.metric("Date Range", f"{len(filtered_df['Date_Only'].unique())} days")
    
    st.markdown("---")
    
    # Display mode selection
    display_mode = st.radio(
        "Display Mode:",
        ["Table View", "Timeline View", "Summary View"],
        horizontal=True
    )
    
    if display_mode == "Table View":
        st.subheader("📋 Trip Data")
        
        # Prepare display dataframe
        display_df = filtered_df[["Date", "Location", "Transit Agency", "Amount"]].copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d %H:%M")
        display_df = display_df.sort_values("Date", ascending=False)
        
        st.dataframe(display_df, use_container_width=True, height=500)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_transit_data.csv",
            mime="text/csv"
        )
    
    elif display_mode == "Timeline View":
        st.subheader("📅 Trip Timeline")
        
        # Daily trip counts
        daily_counts = filtered_df.groupby("Date_Only").size().reset_index(name="Trips")
        daily_counts["Date_Only"] = pd.to_datetime(daily_counts["Date_Only"])
        
        fig = px.scatter(
            daily_counts,
            x="Date_Only",
            y="Trips",
            size="Trips",
            title="Daily Trip Activity",
            color="Trips",
            color_continuous_scale="Blues"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Trips"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calendar heatmap-style view by week
        st.subheader("📆 Weekly Activity")
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy["Week_Start"] = filtered_df_copy["Date"].dt.to_period("W").apply(lambda x: x.start_time)
        weekly_counts = filtered_df_copy.groupby("Week_Start").size().reset_index(name="Trips")
        
        fig_weekly = px.bar(
            weekly_counts,
            x="Week_Start",
            y="Trips",
            title="Trips per Week",
            color="Trips",
            color_continuous_scale="Greens"
        )
        fig_weekly.update_layout(
            xaxis_title="Week Starting",
            yaxis_title="Number of Trips",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    else:  # Summary View
        st.subheader("📈 Data Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top locations
            top_locations = filtered_df["Location"].value_counts().head(5)
            st.markdown("**🏆 Top 5 Locations:**")
            for i, (loc, count) in enumerate(top_locations.items(), 1):
                st.write(f"{i}. {loc} ({count} trips)")
        
        with col2:
            # Agency breakdown
            st.markdown("**🚌 Trips by Agency:**")
            agency_counts = filtered_df["Transit Agency"].value_counts()
            for agency, count in agency_counts.items():
                pct = (count / len(filtered_df)) * 100
                st.write(f"• {agency}: {count} trips ({pct:.1f}%)")
        
        st.markdown("---")
        
        # Time analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⏰ Busiest Hours:**")
            hour_counts = filtered_df["Hour"].value_counts().head(5).sort_index()
            for hour, count in hour_counts.items():
                period = "AM" if hour < 12 else "PM"
                display_hour = hour if hour <= 12 else hour - 12
                if display_hour == 0:
                    display_hour = 12
                st.write(f"• {display_hour}:00 {period} - {count} trips")
        
        with col2:
            st.markdown("**📅 Busiest Days:**")
            day_counts = filtered_df["Day_of_Week"].value_counts().head(5)
            for day, count in day_counts.items():
                st.write(f"• {day}: {count} trips")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please make sure your data is loaded correctly from the main Dashboard page.")
