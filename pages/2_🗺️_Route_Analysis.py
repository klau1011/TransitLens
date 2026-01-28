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
    page_title="Route Analysis",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Route & Location Analysis")
st.markdown("""
Explore your most visited locations and identify your common travel routes and patterns.

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
    # Location frequency analysis
    st.subheader("📍 Top Locations")
    
    n_locations = st.slider("Number of locations to show:", 5, 20, 10)
    
    location_counts = df["Location"].value_counts().head(n_locations)
    
    fig_locations = px.bar(
        x=location_counts.values,
        y=location_counts.index,
        orientation='h',
        title=f"Top {n_locations} Most Visited Locations",
        color=location_counts.values,
        color_continuous_scale="Viridis"
    )
    fig_locations.update_layout(
        xaxis_title="Number of Visits",
        yaxis_title="Location",
        coloraxis_showscale=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_locations, use_container_width=True)

    st.markdown("---")
    
    # Station vs Stop analysis
    st.subheader("🚉 Station Types")
    
    df_copy = df.copy()
    
    # Identify location types
    def categorize_location(loc):
        loc_upper = str(loc).upper()
        if "STATION" in loc_upper:
            return "Subway/Train Station"
        elif " AT " in loc_upper:
            return "Bus Stop"
        elif "GO" in loc_upper:
            return "GO Transit"
        else:
            return "Other"
    
    df_copy["Location_Type"] = df_copy["Location"].apply(categorize_location)
    
    type_counts = df_copy["Location_Type"].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_type_pie = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Travel by Location Type",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_type_pie, use_container_width=True)
    
    with col2:
        fig_type_bar = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title="Trip Count by Location Type",
            color=type_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_type_bar.update_layout(
            xaxis_title="Location Type",
            yaxis_title="Number of Trips",
            showlegend=False
        )
        st.plotly_chart(fig_type_bar, use_container_width=True)

    st.markdown("---")
    
    # Trip sequences (potential routes)
    st.subheader("🔄 Common Trip Sequences")
    st.markdown("These are consecutive trips that might indicate common routes:")
    
    # Sort by date and create sequences
    df_sorted = df.sort_values("Date").reset_index(drop=True)
    
    # Create trip pairs (from -> to)
    trips = []
    for i in range(len(df_sorted) - 1):
        # Check if trips are on the same day
        if df_sorted.loc[i, "Date_Only"] == df_sorted.loc[i+1, "Date_Only"]:
            from_loc = df_sorted.loc[i, "Location"]
            to_loc = df_sorted.loc[i+1, "Location"]
            if from_loc != to_loc:  # Exclude same location
                trips.append(f"{from_loc} → {to_loc}")
    
    if trips:
        trip_counts = pd.Series(trips).value_counts().head(10)
        
        fig_routes = px.bar(
            x=trip_counts.values,
            y=trip_counts.index,
            orientation='h',
            title="Top 10 Trip Sequences (Same Day)",
            color=trip_counts.values,
            color_continuous_scale="Plasma"
        )
        fig_routes.update_layout(
            xaxis_title="Frequency",
            yaxis_title="Trip Sequence",
            coloraxis_showscale=False,
            yaxis={'categoryorder': 'total ascending'},
            height=500
        )
        st.plotly_chart(fig_routes, use_container_width=True)
    else:
        st.info("Not enough consecutive trips to identify common routes.")

    st.markdown("---")
    
    # Unique locations by agency
    st.subheader("🚌 Locations by Transit Agency")
    
    agency_locations = df.groupby("Transit Agency")["Location"].nunique().sort_values(ascending=True)
    
    fig_agency_loc = px.bar(
        x=agency_locations.values,
        y=agency_locations.index,
        orientation='h',
        title="Unique Locations Visited by Transit Agency",
        color=agency_locations.values,
        color_continuous_scale="Teal"
    )
    fig_agency_loc.update_layout(
        xaxis_title="Unique Locations",
        yaxis_title="Transit Agency",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_agency_loc, use_container_width=True)

    st.markdown("---")
    
    # Location first/last visit
    st.subheader("📅 Location Visit History")
    
    location_stats = df.groupby("Location").agg({
        "Date": ["min", "max", "count"]
    }).round(2)
    location_stats.columns = ["First Visit", "Last Visit", "Total Visits"]
    location_stats = location_stats.sort_values("Total Visits", ascending=False).head(15)
    location_stats["First Visit"] = pd.to_datetime(location_stats["First Visit"]).dt.strftime("%Y-%m-%d")
    location_stats["Last Visit"] = pd.to_datetime(location_stats["Last Visit"]).dt.strftime("%Y-%m-%d")
    
    st.dataframe(location_stats, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please make sure your data is loaded correctly from the main Dashboard page.")
