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
    page_title="Route Analysis | TransitLens",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Route & Location Analysis")
st.markdown("""
Explore your most visited locations and identify your common travel routes and patterns.

---
""")

df = get_data()

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
    st.plotly_chart(fig_locations, width="stretch")

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
        st.plotly_chart(fig_routes, width="stretch")
    else:
        st.info("Not enough consecutive trips to identify common routes.")

    st.markdown("---")

    # Location first/last visit
    st.subheader("📅 Location Visit History")
    
    location_stats = df.groupby("Location").agg({
        "Date": ["min", "max", "count"]
    })
    location_stats.columns = ["First Visit", "Last Visit", "Total Visits"]
    location_stats = location_stats.sort_values("Total Visits", ascending=False).head(15)
    location_stats["First Visit"] = pd.to_datetime(location_stats["First Visit"]).dt.strftime("%Y-%m-%d")
    location_stats["Last Visit"] = pd.to_datetime(location_stats["Last Visit"]).dt.strftime("%Y-%m-%d")
    
    st.dataframe(location_stats, width="stretch")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please make sure your data is loaded correctly from the main Dashboard page.")
