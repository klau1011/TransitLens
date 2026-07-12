# TransitLens 🚆🔍

A Streamlit web app that transforms Presto card CSV data into interactive visualizations and insights for travel patterns, spending, and route analysis.

## Features
- **Dashboard** – Key metrics, top stops, spending charts, and map view
- **Travel Patterns** – Day/hour breakdowns and heatmaps
- **Route Analysis** – Frequent locations and trip sequences
- **Spending Insights** – Spending by agency, location, and time
- **Data Explorer** – Filter and search raw transit data

## Quick Start

**Get your data:** Export CSV from [Presto Transit Usage Report](https://www.prestocard.ca/en/my-products/transit-usage-report)

Expected columns: `Date, TransitAgency, Location, Type, Amount` (the older `Transit Agency` header also works). Card top-up rows (`Epurse Load`) are excluded from all trip and spending stats automatically.

**Run locally:**
```bash
pip install -r requirements.txt
streamlit run transit_tool.py
```

**Run with Docker:**
```bash
docker build -t transit-lens .
docker run -p 8501:8501 transit-lens
```

Open `http://localhost:8501`

