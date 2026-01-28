# Metrolinx Transit Insights Tool :train2:

### Description 

This Python web app allows you to input official Metrolinx CSV data to receive various summaries and data visualizations such as usage, stops, and money spent in seconds! 

### Features

The app includes multiple pages with different insights:

- **🚆 Dashboard** - Overview with key metrics, top stops, spending charts, and map visualization
- **📅 Travel Patterns** - Analyze when you travel by day of week, hour, and see heatmaps
- **🗺️ Route Analysis** - Discover your most visited locations and common trip sequences
- **💰 Spending Insights** - Deep dive into your spending patterns by agency, location, and time
- **🔍 Data Explorer** - Filter, search, and explore your raw transit data

### Getting your official data

To get your Metrolinx CSV data:
- Go to the [Presto Card Transit Usage Report](https://www.prestocard.ca/en/my-products/transit-usage-report)
- Select the year and transit usage settings to your preference
- **Export CSV**

### Running the application locally

#### Prerequisites
- Python 3.8+ installed

#### Steps:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run transit_tool.py
   ```
3. Open `http://localhost:8501` in your browser

### Running the application with Docker

#### Prerequisites
- Ensure you have Docker Desktop installed and open

Steps:
- In the root directory, run
    - `docker build -t transit-tool .`
    - `docker run -p 8501:8501 transit-tool`
- The app should be deployed at `http://localhost:8501`

### Contact
For any questions or concerns, reach out at kevlau82@gmail.com

