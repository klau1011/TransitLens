import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = ["Date", "Transit Agency", "Location", "Type", "Amount"]

@st.cache_data
def load_data(uploaded_csv):
    """Load and return raw dataframe from CSV"""
    return pd.read_csv(uploaded_csv)

@st.cache_data
def clean_raw_data(df):
    """Clean and preprocess the transit data"""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"TransitAgency": "Transit Agency"})

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing column(s): {', '.join(missing)}. "
            "Expected columns: Date, TransitAgency, Location, Type, Amount"
        )

    # Keep fare/pass payments only; "Epurse Load" rows are card top-ups, not trips
    df = df[df["Type"].str.contains("Payment", na=False)]
    df = df[["Date", "Location", "Amount", "Transit Agency"]].copy()

    try:
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        df["Date"] = pd.to_datetime(df["Date"])
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

    # Charges are negative in the export ("$-3.30" or "-$2.35"); flip the sign
    # so spending is positive and credits net out
    amount = df["Amount"].astype(str).str.replace("$", "", regex=False)
    df["Amount_Clean"] = -pd.to_numeric(amount)

    return df

def get_data():
    """Cleaned data from session state, loading the sample or an upload if absent"""
    if "transit_data" in st.session_state:
        return st.session_state.transit_data
    st.sidebar.header("📁 Data Upload")
    uploaded_csv = st.sidebar.file_uploader("Upload your Presto CSV:", type="csv")
    if not uploaded_csv:
        uploaded_csv = "transit_usage.csv"
    df = clean_raw_data(load_data(uploaded_csv))
    st.session_state.transit_data = df
    return df

def set_session_data(df):
    """Store cleaned data in session state"""
    st.session_state.transit_data = df
