# streamlit_app.py - Simple dashboard to show recent data and alerts
import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Agri Data Platform", layout="wide")
st.title("Agri Data Platform — Dashboard")

col1, col2 = st.columns([2,1])

with col2:
    st.header("Controls")
    sensor_select = st.text_input("Sensor ID (e.g. field-1-sensor-A)", value="field-1-sensor-A")
    since_minutes = st.number_input("Show last (minutes)", value=1440, min_value=10, max_value=100000)
    refresh = st.button("Refresh")

with col1:
    st.header("Latest Readings")
    try:
        res = requests.get(f"{API_BASE}/api/latest?limit=20", timeout=5)
        data = res.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df_display = df.copy()
            df_display['timestamp'] = pd.to_datetime(df_display['timestamp'])
            st.dataframe(df_display.sort_values('timestamp', ascending=False))
    except Exception as e:
        st.error("Failed to fetch latest readings: " + str(e))

st.markdown("---")
st.header("Sensor timeseries & alerts")

try:
    res = requests.get(f"{API_BASE}/api/timeseries?sensor_id={sensor_select}&since_minutes={since_minutes}", timeout=5)
    ts = res.json()
    if not ts:
        st.info("No data for sensor. Run simulator or post data.")
    else:
        df_ts = pd.DataFrame(ts)
        df_ts['timestamp'] = pd.to_datetime(df_ts['timestamp'])
        df_ts = df_ts.set_index('timestamp')
        st.line_chart(df_ts[['soil_moisture','temperature','humidity']])

        # Simple alerts based on thresholds
        latest = df_ts.iloc[-1]
        alerts = []
        if latest['soil_moisture'] < 12:
            alerts.append("Low soil moisture — consider irrigating.")
        if latest['soil_moisture'] > 40:
            alerts.append("High soil moisture — check drainage.")
        try:
            ph_val = float(latest.get('ph', None))
            if ph_val < 5.5:
                alerts.append("Soil is acidic (low pH) — consider liming.")
            if ph_val > 7.8:
                alerts.append("Soil is alkaline (high pH) — check fertilizer choices.")
        except Exception:
            pass
        if latest['temperature'] > 32:
            alerts.append("High temperature — heat stress risk for crops.")
        if alerts:
            st.warning('\n'.join(alerts))
        else:
            st.success("All readings in comfortable ranges.")
except Exception as e:
    st.error("Failed to fetch timeseries: " + str(e))

st.markdown("---")
st.header("Notes & Next Steps")
st.markdown("""
- This demo uses a simple SQLite DB. For production, replace with InfluxDB or TimescaleDB for time-series.
- Add authentication for producers and farmers.
- Integrate weather API (OpenWeatherMap) to compare sensor vs forecast.
- Add irrigation scheduling (automated rules + notifications).
""")
