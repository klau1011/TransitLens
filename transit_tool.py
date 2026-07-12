import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import datetime
from utils import load_data, clean_raw_data, set_session_data

# Streamlit Config and Headers
st.set_page_config(
    page_title="TransitLens",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 TransitLens")
st.markdown("""
Welcome to **TransitLens**! Upload your Presto card CSV data 
to visualize your transit patterns, spending, and travel habits.

> Navigate through the pages in the sidebar for detailed insights.

---
""")

@st.cache_data
def map_frequent_stops(df):
    location_counts = df["Location"].value_counts().nlargest(10)
    fig = px.bar(
        location_counts, 
        title="Top 10 Most Visited Stops",
        color=location_counts.values,
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        xaxis_title="Location", 
        yaxis_title="Visit Count", 
        showlegend=False,
        coloraxis_showscale=False
    )
    number_unique_stops = len(df["Location"].unique())
    return fig, number_unique_stops

@st.cache_data
def get_spendings_data(df):
    out = df.groupby("Month")["Amount_Clean"].sum()
    num_amount_spent = df["Amount_Clean"].sum()
    return out, num_amount_spent

@st.cache_data
def get_tap_data(df):
    unique_days_travelled = df["Date_Only"].nunique()
    fig2 = px.bar(df.groupby("Month").size(), title="Monthly Tap Frequency")
    return fig2, unique_days_travelled

# Sidebar for file upload
st.sidebar.header("📁 Data Upload")
uploaded_csv = st.sidebar.file_uploader("Upload your Presto CSV:", type="csv")

if not uploaded_csv:
    st.sidebar.info("Using sample data. Upload your own CSV for personalized insights!")
    uploaded_csv = "transit_usage.csv"

try:
    df = load_data(uploaded_csv)
    df = clean_raw_data(df)
    set_session_data(df)  # Store for other pages
    
    # Key Metrics Row
    st.subheader("📊 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    total_trips = len(df)
    unique_stops = len(df["Location"].unique())
    total_spent = df["Amount_Clean"].sum()
    unique_days = df["Date_Only"].nunique()
    
    col1.metric("Total Trips", f"{total_trips}")
    col2.metric("Unique Stops", f"{unique_stops}")
    col3.metric("Total Spent", f"${total_spent:.2f}")
    col4.metric("Days Travelled", f"{unique_days}")

    st.markdown("---")

    # Main visualizations - Most Visited Stops
    st.subheader("🗺️ Most Visited Stops")
    fig, number_unique_stops = map_frequent_stops(df)
    st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Spending section
    left_col2, right_col2 = st.columns(2)
    
    with left_col2:
        out, num_amount_spent = get_spendings_data(df)
        amountFig = px.bar(out, title="Monthly Transit Spending")
        amountFig.update_layout(
            xaxis_title="Month", 
            yaxis_title="Amount Spent ($)", 
            showlegend=False
        )
        st.plotly_chart(amountFig, width="stretch")
    
    with right_col2:
        fig2, unique_days_travelled = get_tap_data(df)
        fig2.update_layout(
            xaxis_title="Month", 
            yaxis_title="Tap Count", 
            showlegend=False
        )
        st.plotly_chart(fig2, width="stretch")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please make sure your CSV file has the correct format with columns: Date, TransitAgency, Location, Type, Amount")