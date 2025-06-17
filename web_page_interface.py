# --- Imports ---
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from password_utils import get_decrypted_password
import plotly.express as px
import plotly.graph_objects as go  # New for enhanced map
from io import BytesIO
from connec_web_to_db import db_connect

# --- DB Connection ---
engine = db_connect()

# --- Sidebar Filters ---
st.sidebar.title("🔍 Filter Flights")

def load_filter_options():
    cities = pd.read_sql("SELECT DISTINCT from_city FROM all_data", engine)['from_city'].dropna().sort_values().tolist()
    to_cities = pd.read_sql("SELECT DISTINCT to_city FROM all_data", engine)['to_city'].dropna().sort_values().tolist()
    classes = pd.read_sql("SELECT DISTINCT class FROM all_data", engine)['class'].dropna().sort_values().tolist()
    stops_list = pd.read_sql("SELECT DISTINCT stops FROM all_data", engine)['stops'].dropna().sort_values().tolist()
    airlines = pd.read_sql("SELECT DISTINCT airline FROM all_data", engine)['airline'].dropna().sort_values().tolist()
    return cities, to_cities, classes, stops_list, airlines

cities, to_cities, classes, stops_list, airlines = load_filter_options()

from_city = st.sidebar.selectbox("From City", cities)
to_city = st.sidebar.selectbox("To City", to_cities)
flight_class = st.sidebar.selectbox("Class", classes)
stops = st.sidebar.selectbox("Stops", stops_list)
airline_options = ['All'] + airlines
airline = st.sidebar.selectbox("Airline", airline_options)

min_date, max_date = pd.read_sql("SELECT MIN(flight_date), MAX(flight_date) FROM all_data", engine).iloc[0]
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

month = pd.to_datetime(date_range[0]).strftime('%B')
submit = st.sidebar.button("Submit")

# --- Metro Cities and Coordinates ---
city_coords = {
    "Bangalore": {"lat": 13.199379, "lon": 77.710136},
    "Chennai": {"lat": 12.9940, "lon": 80.1707},
    "Delhi": {"lat": 28.556160, "lon": 77.1000},
    "Hyderabad": {"lat": 17.2403, "lon": 78.4294    },
    "Kolkata": {"lat": 22.6536, "lon": 88.4451},
    "Mumbai": {"lat": 19.0902, "lon": 72.8628}
}
metro_cities = list(city_coords.keys())

# --- Main Visual Function ---
def visual():
    if submit:
        # Build SQL query
        sql = """
        SELECT * FROM all_data
        WHERE from_city = :from_city
          AND to_city = :to_city
          AND class = :flight_class
          AND stops = :stops
          AND flight_date BETWEEN :start_date AND :end_date
        """
        params = {
            "from_city": from_city,
            "to_city": to_city,
            "flight_class": flight_class,
            "stops": stops,
            "start_date": date_range[0],
            "end_date": date_range[1]
        }

        if airline != "All":
            sql += " AND airline = :airline"
            params["airline"] = airline

        try:
            df = pd.read_sql_query(text(sql), con=engine, params=params)
        except Exception as e:
            st.error(f"Error retrieving data: {e}")
            st.stop()

        if df.empty:
            st.warning("No data available for the selected filters.")
            return

        # Clean data
        df['flight_date'] = pd.to_datetime(df['flight_date'], errors='coerce')
        df.dropna(subset=['flight_date'], inplace=True)
        df['month'] = df['flight_date'].dt.strftime('%B')
        df['price'] = df['price'].astype(str).str.replace('[\$,]', '', regex=True).str.replace(',', '').astype(float)

        # --- Dashboard Starts ---
        st.title("✈️ Flight Data Dashboard")
        st.subheader(f"Flights from {from_city} to {to_city} in {month}")

        # Map Integration (only for metro cities)
        if from_city in metro_cities and to_city in metro_cities and from_city != to_city:
            st.subheader("🗺️ Flight Path (Metro Cities Only)")

            fig_map = go.Figure()

            fig_map.add_trace(go.Scattergeo(
                locationmode='country names',
                lon=[city_coords[from_city]["lon"], city_coords[to_city]["lon"]],
                lat=[city_coords[from_city]["lat"], city_coords[to_city]["lat"]],
                mode='lines+markers',
                line=dict(width=3, color='crimson'),
                marker=dict(size=8, color='blue'),
                name=f'{from_city} to {to_city}'
            ))

            fig_map.update_layout(
                title=f"{from_city} → {to_city} Flight Path",
                geo=dict(
                    scope='asia',  # Zooms to Asia region (India visible)
                    projection_type='natural earth',
                    showland=True,
                    landcolor='rgb(0, 229, 229)',
                    countrycolor='black',
                    showcoastlines=True,
                    coastlinecolor='blue',
                    lonaxis=dict(range=[68, 98]),  # Longitude bounds for India
                    lataxis=dict(range=[6, 38])    # Latitude bounds for India
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )

            st.plotly_chart(fig_map, use_container_width=True)

        # Show Data Table
        st.dataframe(df)

        # Average Price
        avg_price = df['price'].mean()
        st.metric(label="💰 Average Price", value=f"₹{avg_price:,.2f}")

        # Interactive Chart
        if airline == "All":
            st.subheader("📈 Average Price by Airline (Interactive)")
            avg_by_airline = df.groupby('airline')['price'].mean().reset_index().sort_values(by='price')
            fig = px.line(avg_by_airline, x='airline', y='price', markers=True,
                          title='Average Price per Airline',
                          labels={'price': 'Price (₹)', 'airline': 'Airline'})
            fig.update_traces(line=dict(dash='dot', color='indigo'))
            st.plotly_chart(fig)
        else:
            st.info("Interactive chart only appears when 'All' airlines are selected.")

        # Top 5 Cheapest Flights
        st.subheader("🪙 Top 5 Cheapest Flights")
        top5 = df.sort_values(by='price').head(5)
        st.table(top5[['flight_date', 'airline', 'flight_num', 'price', 'duration', 'stops']])

        # Download Button
        st.subheader("📥 Download Filtered Data")
        csv = top5.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='filtered_flights.csv',
            mime='text/csv'
        )

# --- Run Main ---
if __name__ == "__main__":
    visual()
