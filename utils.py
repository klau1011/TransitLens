import pandas as pd
import streamlit as st

@st.cache_data
def load_data(uploaded_csv):
    """Load and return raw dataframe from CSV"""
    if uploaded_csv is None:
        return pd.read_csv("transit_usage.csv")
    return pd.read_csv(uploaded_csv)

@st.cache_data
def clean_raw_data(df):
    """Clean and preprocess the transit data"""
    df = df[["Date", "Location", "Amount", "Transit Agency"]].copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y %I:%M:%S %p")
    df = df.replace(
        {
            "Zone17": "Aldershot GO",
            "Zone20": "Square One",
            "Zone27": "University of Waterloo",
        }
    )
    # Add derived columns
    df["Day_of_Week"] = df["Date"].dt.day_name()
    df["Hour"] = df["Date"].dt.hour
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Week"] = df["Date"].dt.isocalendar().week
    df["Year"] = df["Date"].dt.year
    df["Date_Only"] = df["Date"].dt.date
    
    # Clean amount column
    df["Amount_Clean"] = df["Amount"].str.replace("-", "").str.replace("$", "").astype(float)
    
    return df

def get_session_data():
    """Get data from session state or return None"""
    if "transit_data" in st.session_state:
        return st.session_state.transit_data
    return None

def set_session_data(df):
    """Store cleaned data in session state"""
    st.session_state.transit_data = df

def setup_page(title, icon):
    """Common page setup"""
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide"
    )
