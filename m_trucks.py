import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Initialize SQLite database
conn = sqlite3.connect('fuel_data.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS fuel_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id TEXT,
    real_km FLOAT,
    fuel_quantity FLOAT,
    station_location TEXT,
    date TEXT
)
''')
conn.commit()

# Sidebar menu
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Enter Data", "View History", "Charts"])

# Dropdown to select truck
c.execute('SELECT DISTINCT truck_id FROM fuel_data')
trucks = [row[0] for row in c.fetchall()]
selected_truck = st.sidebar.selectbox("Select Truck", trucks + ["Add New Truck"])

if selected_truck == "Add New Truck":
    new_truck = st.sidebar.text_input("Enter New Truck ID")
    if st.sidebar.button("Add Truck"):
        c.execute('INSERT INTO fuel_data (truck_id) VALUES (?)', (new_truck,))
        conn.commit()
        st.sidebar.success("Truck added!")
        st.experimental_rerun()
else:
    if menu == "Enter Data":
        st.title("Enter Fuel Data")

        real_km = st.number_input("Enter Real Kilometer", min_value=0.0, step=0.1)
        fuel_quantity = st.number_input("Enter Fuel Quantity", min_value=0.0, step=0.1)
        station_location = st.text_input("Enter Station Location")
        date = st.date_input("Enter Date")

        if st.button("Submit"):
            c.execute('''
            INSERT INTO fuel_data (truck_id, real_km, fuel_quantity, station_location, date)
            VALUES (?, ?, ?, ?, ?)
            ''', (selected_truck, real_km, fuel_quantity, station_location, date))
            conn.commit()
            st.success("Data successfully added!")

    elif menu == "View History":
        st.title("View Fuel Data History")

        df = pd.read_sql('SELECT * FROM fuel_data WHERE truck_id = ?', conn, params=(selected_truck,))
        if not df.empty:
            df['previous_km'] = df['real_km'].shift(1)
            df['Liter_per_100Km'] = (100*df['fuel_quantity'])/(df['real_km'] - df['previous_km']) 
            df = df.drop(columns=['previous_km'])
            st.dataframe(df)

    elif menu == "Charts":
        st.title("Fuel Data Analysis")

        df = pd.read_sql('SELECT * FROM fuel_data WHERE truck_id = ?', conn, params=(selected_truck,))
        if not df.empty:
            df['previous_km'] = df['real_km'].shift(1)
            df['Liter_per_100Km'] = (100*df['fuel_quantity'])/(df['real_km'] - df['previous_km']) 

            st.subheader("Kilometers per 100 Liters Over Time")
            fig = px.line(df, x='date', y='Liter_per_100Km', title=f'Kilometers per 100 Liters for Truck {selected_truck}')
            st.plotly_chart(fig)
        else:
            st.write("No data available to plot.")

# Close database connection
conn.close()
