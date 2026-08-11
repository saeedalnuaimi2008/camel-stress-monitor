import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import serial
import serial.tools.list_ports
import time
from datetime import datetime
from modules.math_engine import calculate_thi, calculate_camel_activity_ewma
from modules.generator import generate_camel_telemetry_data

st.set_page_config(page_title="Camel Health Monitor", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("Camel Health & Heat Alert Dashboard")
st.text("Daily Camel Activity & Weather Stress Tracker")
st.divider()

# Initialize Session State Buffer for Live Hardware Streaming
if "live_buffer" not in st.session_state:
    st.session_state.live_buffer = pd.DataFrame(columns=["date", "temp_c", "humidity_pct", "activity_units"])

# Sidebar Configuration
st.sidebar.subheader("App Mode")
data_mode = st.sidebar.radio("Data Source", ["Simulated Data Mode", "Live Sensor Connection"])

if data_mode == "Simulated Data Mode":
    df_raw = generate_camel_telemetry_data(days=60)
    df_raw['thi'], df_raw['thi_status'] = zip(*df_raw.apply(lambda row: calculate_thi(row['temp_c'], row['humidity_pct']), axis=1))
    df_processed = calculate_camel_activity_ewma(df_raw)

    st.sidebar.divider()
    st.sidebar.subheader("Select Day")
    selected_day = st.sidebar.slider("Day Index", 0, len(df_processed) - 1, len(df_processed) - 1)
    latest_row = df_processed.iloc[selected_day]

    movement_percent = int(latest_row['activity_ratio'] * 100)

    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Air Temp", f"{latest_row['temp_c']} C")
    m2.metric("Humidity", f"{latest_row['humidity_pct']} %")
    m3.metric("Heat Risk Level", f"{latest_row['thi']:.1f} / 100")
    m4.metric("Camel Activity vs Normal", f"{movement_percent}%")

    st.divider()

    # Plain Language Alerts
    if latest_row['thi'] >= 79.0 and latest_row['activity_ratio'] < 0.7:
        st.error(f"HIGH RISK ALERT (Day {selected_day}): Extreme heat paired with very low movement ({movement_percent}% of normal). Check this camel immediately for water, shade, or heat sickness.")
    elif latest_row['thi'] >= 79.0:
        st.warning(f"HEAT WARNING (Day {selected_day}): High heat today ({latest_row['temp_c']} C). Ensure shade and water troughs are full.")
    elif latest_row['activity_ratio'] < 0.7:
        st.warning(f"HEALTH CHECK NEEDED (Day {selected_day}): Weather is fine, but movement dropped to {movement_percent}% of normal. Check for injury or weakness.")
    else:
        st.info(f"STATUS GOOD (Day {selected_day}): Weather is safe and camels are moving normally.")

    st.write("")

    # Dashboard Tabs
    tab1, tab2 = st.tabs(["Daily Activity & Heat Chart", "Heat vs Movement Overview"])

    with tab1:
        st.subheader("Daily Activity vs Heat History")
        
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=df_processed['date'], y=df_processed['thi'], name="Heat Stress Level", line=dict(color="#d9534f", width=2)))
        fig_ts.add_trace(go.Scatter(x=df_processed['date'], y=df_processed['acute_activity'], name="Recent Movement Level", line=dict(color="#0275d8", width=2), yaxis="y2"))
        fig_ts.add_trace(go.Scatter(x=df_processed['date'], y=df_processed['chronic_activity'], name="Normal Monthly Average Movement", line=dict(color="#777777", width=1.5, dash="dash"), yaxis="y2"))

        fig_ts.update_layout(
            xaxis=dict(title="Date"),
            yaxis=dict(title="Heat Level", side="left"),
            yaxis2=dict(title="Movement Level", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            template="plotly_white", height=480, margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with tab2:
        st.subheader("Camel Health Matrix")
        st.caption("Each dot represents a day. Bottom-right corner shows dangerous days (High Heat + Low Movement).")

        fig_scatter = px.scatter(
            df_processed, x="thi", y="activity_ratio", color="thi_status",
            hover_data=["date", "temp_c", "humidity_pct"],
            labels={"thi": "Heat Risk Level", "activity_ratio": "Movement Ratio (1.0 = Normal)", "thi_status": "Weather Condition"},
            color_discrete_map={"COMFORT": "#5cb85c", "MILD_ALERT": "#f0ad4e", "MODERATE_STRESS": "#f0ad4e", "EXTREME_HAZARD": "#d9534f"}
        )
        fig_scatter.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="Low Activity Warning (70%)")
        fig_scatter.add_vline(x=79.0, line_dash="dash", line_color="orange", annotation_text="High Heat Warning Level")
        fig_scatter.update_layout(template="plotly_white", height=480, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.sidebar.subheader("Sensor Connection Setup")
    ports = [port.device for port in serial.tools.list_ports.comports()]
    
    if not ports:
        st.warning("No sensors connected. Connect the ESP32 device via USB to stream live camel data.")
        if st.button("Load Test Line into Live Buffer"):
            new_row = pd.DataFrame([{
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temp_c": 38.5,
                "humidity_pct": 42.0,
                "activity_units": 4800
            }])
            st.session_state.live_buffer = pd.concat([st.session_state.live_buffer, new_row], ignore_index=True)
            st.success("Added simulated test record to buffer.")
    else:
        selected_port = st.sidebar.selectbox("Select Sensor Port:", ports)
        baud_rate = st.sidebar.selectbox("Connection Speed:", [115200, 9600])
        
        run_stream = st.sidebar.checkbox("Start Live Stream Ingestion")
        
        if run_stream:
            st.info(f"Reading active stream from {selected_port} at {baud_rate} baud...")
            try:
                ser = serial.Serial(selected_port, baud_rate, timeout=1)
                raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Expected format from ESP32 C++ firmware: "TEMP,HUMIDITY,ACTIVITY" (e.g. "38.2,45.0,5100")
                if raw_line and "," in raw_line:
                    parts = raw_line.split(",")
                    if len(parts) == 3:
                        t_val, h_val, a_val = float(parts[0]), float(parts[1]), float(parts[2])
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        new_data = pd.DataFrame([{
                            "date": timestamp,
                            "temp_c": t_val,
                            "humidity_pct": h_val,
                            "activity_units": a_val
                        }])
                        
                        st.session_state.live_buffer = pd.concat([st.session_state.live_buffer, new_data], ignore_index=True)
                ser.close()
            except Exception as e:
                st.error(f"Serial Communication Error: {e}")

    # Render Live Hardware Buffer Data
    st.subheader("Live Incoming Sensor Telemetry")
    if not st.session_state.live_buffer.empty:
        live_df = st.session_state.live_buffer.copy()
        live_df['thi'], live_df['thi_status'] = zip(*live_df.apply(lambda row: calculate_thi(row['temp_c'], row['humidity_pct']), axis=1))
        
        st.dataframe(live_df, use_container_width=True)
        
        latest = live_df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Live Temp", f"{latest['temp_c']} C")
        c2.metric("Live Humidity", f"{latest['humidity_pct']} %")
        c3.metric("Live Heat Risk", f"{latest['thi']:.1f}")
    else:
        st.write("Waiting for data packets from serial port...")
