import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, time

# =====================================================================
# 1. PAGE CONFIGURATION & INLINE IN-GRID STYLES
# =====================================================================
st.set_page_config(page_title="Warrior 12-Stock Grid Command", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    
    /* Target ONLY top-level grid cards cleanly using custom container wrapper */
    .grid-card-wrapper {
        border: 1px solid #2d3139;
        padding: 14px;
        border-radius: 8px;
        background-color: #131722;
        margin-bottom: 12px;
    }
    
    /* Style for the inline grid text input boxes to make them look slick */
    .stTextInput input {
        background-color: #1c2030 !important;
        color: #ffffff !important;
        border: 1px solid #363c4e !important;
        text-align: center;
        font-weight: bold;
    }

    /* Force header components inside the grid card to align tight horizontally */
    .card-header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 8px;
    }
    .card-header-title {
        margin: 0 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffffff;
    }
    
    /* Clean custom CSS for side-by-side metrics to bypass Streamlit column bugs */
    .metrics-row {
        display: flex;
        justify-content: space-between;
        background: #1c2030;
        padding: 8px;
        border-radius: 6px;
        border: 1px solid #2d3139;
        margin-bottom: 10px;
    }
    .metric-box {
        text-align: center;
        width: 48%;
    }
    .metric-label {
        font-size: 11px;
        color: #848e9c;
        margin-bottom: 2px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ Warrior Multi-Asset Grid Command Center")
st.markdown("Tracks up to 12 simultaneous structural breakouts, volume shocks, and macro-aligned conviction signatures.")

# =====================================================================
# 2. OPTIMIZED BATCH DATA FETCHING ENGINE (CACHED)
# =====================================================================
@st.cache_data(ttl=15)
def pull_batch_clean_feed(tickers_list, interval, period="1mo"):
    if not tickers_list:
        return None
    try:
        data = yf.download(tickers_list, period=period, interval=interval, group_by='ticker')
        if data.empty: 
            return None
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data
    except Exception as e:
        return None

# =====================================================================
# 3. DETAILED ACTION VIEW MODAL (STREAMLIT DIALOG HOOK)
# =====================================================================
@st.dialog("Detailed Analysis Workspace", width="large")
def open_expanded_workspace(ticker, status_msg, theme_color, plot_df, resistance_ceiling, support_floor, narrative, pattern_name):
    st.title(f"📊 {ticker} Strategic Blueprint")
    
    if pattern_name != "None":
        st.markdown(f"### Active Structural Profile: `{pattern_name}`")
    
    st.markdown(f"""
    <div style="background-color:{theme_color}; padding:20px; border-radius:8px; border: 1px solid rgba(255,255,255,0.1); margin-bottom:20px;">
        <h3 style="margin-top:0; color:#ffffff; font-weight:700;">{status_msg}</h3>
        <p style="font-size:15px; color:#f5f5f5; margin-bottom:0; line-height:1.6;">{narrative}</p>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df.index, open=plot_df['Open'], high=plot_df['High'], low=plot_df['Low'], close=plot_df['Close'], 
        name="Price Candles"
    ))
    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df['EMA_9'], line=dict(color="#3a86ff", width=2), name="9 EMA"))
    fig.add_shape(type="line", x0=plot_df.index[0], y0=resistance_ceiling, x1=plot_df.index[-1], y1=resistance_ceiling, line=dict(color="#FF4B4B", width=2, dash="dash"))
    fig.add_shape(type="line", x0=plot_df.index[0], y0=support_floor, x1=plot_df.index[-1], y1=support_floor, line=dict(color="#2EB82E", width=2, dash="dash"))
    
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=480, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# 4. SIDEBAR GLOBAL MACRO PARAMETERS ONLY
# =====================================================================
st.sidebar.header("🕹️ Global Matrix Parameters")
exchange = st.sidebar.selectbox("Exchange Registry:", ["NSE (.NS)", "BSE (.BO)"])
trading_tf = st.sidebar.selectbox("Trading Timeframe (Execution):", ["5m", "15m", "30m"])

st.sidebar.markdown("---")
st.sidebar.subheader("🔬 Time Machine Options")
target_date = st.sidebar.date_input("Select Target Test Date:", datetime.now().date())
target_time = st.sidebar.time_input("Set Simulation Cutoff Time:", time(10, 30), step=300)
replay_cutoff = pd.Timestamp(datetime.combine(target_date, target_time))

st.sidebar.markdown("---")
boundary_mode = st.sidebar.radio(
    "Structural Range Source:", 
    ["Dynamic Trailing Window (Past 20 Candles)", "Purely Today's Session Fixed Baseline"]
)

open_buffer_mins = st.sidebar.slider("Ignore Opening Volatility (Minutes):", 0, 30, 10, step=5)
vol_sigma = st.sidebar.slider("Required Volume Shock (Z-Score Sigma):", 1.0, 3.0, 1.5, step=0.1)
proximity_buffer_pct = st.sidebar.slider("Zone Proximity Sensitivity (%):", 0.1, 1.0, 0.3, step=0.05) / 100
max_ema_extension = st.sidebar.slider("Max Allowed 9 EMA Extension (%):", 0.5, 3.0, 1.5, step=0.1) / 100

# =====================================================================
# 5. INITIALIZE STATE REGISTRY (FOOLPROOF ISOLATED PERSISTENCE ENGINE)
# =====================================================================
suffix = ".NS" if exchange == "NSE (.NS)" else ".BO"

# Master persistent storage key
if "grid_master_tickers" not in st.session_state:
    st.session_state["grid_master_tickers"] = {
        1: "SUNPHARMA",
        2: "RELIANCE",
        3: "BEL",
        4: "LICI",
        5: "", 6: "", 7: "", 8: "", 9: "", 10: "", 11: "", 12: ""
    }

# Callback handlers that directly target master storage and force structural reruns
def add_asset_callback(idx):
    input_key = f"temp_input_{idx}"
    if input_key in st.session_state and st.session_state[input_key]:
        st.session_state["grid_master_tickers"][idx] = st.session_state[input_key].strip().upper()
        st.session_state[input_key] = "" # clean input widget memory trace

def remove_asset_callback(idx):
    st.session_state["grid_master_tickers"][idx] = ""

# Map active list using master dictionary data structures
active_batch_list = []
slot_to_ticker_map = {}

for i in range(1, 13):
    raw_val = st.session_state["grid_master_tickers"][i]
    if raw_val:
        full_ticker = f"{raw_val}{suffix}"
        active_batch_list.append(full_ticker)
        slot_to_ticker_map[i] = full_ticker

global_batch_df = pull_batch_clean_feed(list(set(active_batch_list)), trading_tf, period="1mo") if active_batch_list else None

# =====================================================================
# 6. UNIFIED 4x3 INTERACTIVE MATRIX GENERATOR
# =====================================================================
for r in range(3):  
    grid_cols = st.columns(4)
    for c in range(4):
        slot_idx = r * 4 + c + 1
        
        if slot_idx > 12:
            break
            
        with grid_cols[c]:
            st.markdown('<div class="grid-card-wrapper">', unsafe_allow_html=True)
            
            # --- RENDER BLOCK: EMPTY STATE INPUT ---
            if not st.session_state["grid_master_tickers"][slot_idx]:
                st.markdown(f"<p style='color:#5c6370; font-size:11px; margin-bottom:2px; font-weight:bold;'>📟 SLOT {slot_idx} READY</p>", unsafe_allow_html=True)
                st.text_input(
                    "Deploy Asset Symbol:", 
                    key=f"temp_input_{slot_idx}", 
                    label_visibility="collapsed", 
                    placeholder="Type ticker & hit Enter...",
                    on_change=add_asset_callback,
                    args=(slot_idx,)
                )
                st.markdown("<div style='height:330px; display:flex; align-items:center; justify-content:center;'><span style='color:#2d3139; font-size:24px;'>＋</span></div>", unsafe_allow_html=True)
            
            # --- RENDER BLOCK: ACTIVE POSITION TRACKING CARD ---
            else:
                ticker_symbol = slot_to_ticker_map.get(slot_idx)
                clean_display_name = st.session_state["grid_master_tickers"][slot_idx]
                
                try:
                    if global_batch_df is None or ticker_symbol not in global_batch_df:
                        st.markdown(f"### **{clean_display_name}**")
                        st.caption("Synchronizing data stream...")
                        st.button("❌ Remove Asset", key=f"clear_slot_{slot_idx}", on_click=remove_asset_callback, args=(slot_idx,), use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        continue
                    
                    if len(set(active_batch_list)) > 1:
                        df_ticker_raw = global_batch_df[ticker_symbol].copy()
                    else:
                        df_ticker_raw = global_batch_df.copy()
                        
                    trade_df = df_ticker_raw[df_ticker_raw.index <= replay_cutoff].copy()
                    if trade_df.empty or len(trade_df) < 25:
                        st.markdown(f"### **{clean_display_name}**")
                        st.caption("⏳ Loading time history...")
                        st.button("❌ Remove Asset", key=f"clear_slot_{slot_idx}", on_click=remove_asset_callback, args=(slot_idx,), use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        continue
                    
                    # --- MATH STACK CORE FORMULAS ---
                    trade_df['EMA_9'] = trade_df['Close'].ewm(span=9, adjust=False).mean()
                    working_df = trade_df.tail(45).copy()
                    history, live_candle = working_df.iloc[:-1], working_df.iloc[-1]
                    
                    if boundary_mode == "Dynamic Trailing Window (Past 20 Candles)":
                        structural_lookback = history.tail(20)
                        resistance_ceiling = structural_lookback['High'].max()
                        support_floor = structural_lookback['Low'].min()
                    else:
                        today_history = history[history.index.date == live_candle.name.date()]
                        if not today_history.empty:
                            session_date = today_history.index[0].date()
                            market_open_dt = pd.Timestamp(datetime.combine(session_date, time(9, 15)))
                            clean_structure_start = market_open_dt + pd.Timedelta(minutes=open_buffer_mins)
                            filtered_history = today_history[today_history.index >= clean_structure_start]
                            if filtered_history.empty: filtered_history = today_history
                        else:
                            filtered_history = history
                        resistance_ceiling = filtered_history['High'].max() if not filtered_history.empty else live_candle['High']
                        support_floor = filtered_history['Low'].min() if not filtered_history.empty else live_candle['Low']
                    
                    O, H, L, C = live_candle['Open'], live_candle['High'], live_candle['Low'], live_candle['Close']
                    live_ema9 = live_candle['EMA_9']
                    prev_1 = working_df.iloc[-2] if len(working_df) >= 2 else live_candle
                    
                    vol_mean = history['Volume'].mean() if not history.empty else 1
                    vol_std = history['Volume'].std() if not history.empty else 1
                    volume_z_score = (live_candle['Volume'] - vol_mean) / vol_std if vol_std > 0 else 0
                    volume_shock_confirmed = volume_z_score >= vol_sigma
                    
                    higher_tf_is_bullish = C > trade_df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
                    ema_extension_pct = (C - live_ema9) / live_ema9 if live_ema9 > 0 else 0
                    
                    body = abs(C - O)
                    total_range = H - L if (H - L) > 0 else 0.01
                    upper_wick = H - max(O, C)
                    lower_wick = min(O, C) - L
                    is_doji = body <= (total_range * 0.1)
                    
                    detected_pattern = "None"
                    pattern_type = "Neutral"
                    pattern_weight = "Low"
                    
                    if lower_wick >= (2 * body) and upper_wick <= (0.2 * body) and body > 0:
                        if C > O: detected_pattern, pattern_type = "🔨 BULLISH HAMMER", "Bullish"
                        else: detected_pattern, pattern_type = "🚨 HANGING MAN", "Bearish"
                    elif upper_wick >= (2 * body) and lower_wick <= (0.2 * body) and body > 0:
                        if C > O: detected_pattern, pattern_type = "📐 INVERTED HAMMER", "Bullish"
                        else: detected_pattern, pattern_type = "🏹 SHOOTING STAR", "Bearish"
                    elif is_doji:
                        if lower_wick >= (2 * total_range * 0.3) and upper_wick <= (total_range * 0.1):
                            detected_pattern, pattern_type = "🐉 DRAGONFLY DOJI", "Bullish"
                        elif upper_wick >= (2 * total_range * 0.3) and lower_wick <= (total_range * 0.1):
                            detected_pattern, pattern_type = "🪦 GRAVESTONE DOJI", "Bearish"
                            
                    if len(working_df) >= 2:
                        prev_O, prev_H, prev_L, prev_C = prev_1['Open'], prev_1['High'], prev_1['Low'], prev_1['Close']
                        if abs(L - prev_L) <= (L * 0.0005) and prev_C < prev_O and C > O:
                            detected_pattern, pattern_type, pattern_weight = "🧲 TWEEZER BOTTOM", "Bullish", "Medium"
                        elif abs(H - prev_H) <= (H * 0.0005) and prev_C > prev_O and C < O:
                            detected_pattern, pattern_type, pattern_weight = "🧲 TWEEZER TOP", "Bearish", "Medium"
                            
                    buffer_amt = resistance_ceiling * proximity_buffer_pct
                    in_resistance_zone = H >= (resistance_ceiling - buffer_amt)
                    in_support_zone = L <= (support_floor + buffer_amt)
                    
                    if C > resistance_ceiling:
                        if volume_shock_confirmed:
                            if ema_extension_pct > max_ema_extension: status_msg = "⚠️ OVEREXTENDED BREAKOUT"; theme_color = "#744210"
                            else: status_msg = "🚀 PREMIUM BREAKOUT"; theme_color = "#1b4332"
                        else: status_msg = "🚧 FALSE VOL BREAKOUT"; theme_color = "#5c4314"
                        analysis_narrative = f"Price broke resistance boundaries with Z-Score of {volume_z_score:.2f} σ."
                    elif C < support_floor:
                        if volume_shock_confirmed:
                            if abs(ema_extension_pct) > max_ema_extension: status_msg = "⚠️ OVEREXTENDED BEAR WAVE"; theme_color = "#5c1e24"
                            else: status_msg = "🩸 STRUCTURAL BREAKDOWN"; theme_color = "#4a0d14"
                        else: status_msg = "🚧 BEAR TRAP RISK"; theme_color = "#3d1b20"
                        analysis_narrative = f"Asset broke structural support boundaries. Volume Z-Score: {volume_z_score:.2f} σ."
                    elif in_resistance_zone and C <= resistance_ceiling:
                        if pattern_type == "Bearish":
                            prefix = "💥 HIGH-CONVICTION" if pattern_weight in ["Medium", "High"] else "⚖️ STANDARD"
                            status_msg = f"📉 {prefix} REVERSAL"; theme_color = "#641e1e"
                        else: status_msg = "🔍 RESISTANCE PROXIMITY"; theme_color = "#3d2d2d"
                        analysis_narrative = f"Asset hovering at resistance envelope. Candlestick Profile: {detected_pattern}."
                    elif in_support_zone and C >= support_floor:
                        if pattern_type == "Bullish":
                            prefix = "💥 HIGH-CONVICTION" if pattern_weight in ["Medium", "High"] else "⚖️ STANDARD"
                            status_msg = f"🟢 {prefix} REVERSAL"; theme_color = "#0a5c36"
                        else: status_msg = "🔍 SUPPORT PROXIMITY"; theme_color = "#1d3d2a"
                        analysis_narrative = f"Price testing support bounds. Candlestick Profile: {detected_pattern}."
                    elif higher_tf_is_bullish and C >= live_ema9:
                        if abs(ema_extension_pct) <= max_ema_extension: status_msg = "🚀 9 EMA ENTRY WINDOW"; theme_color = "#123a4a"
                        else: status_msg = "📈 ACTIVE 9 EMA TREND RIDE"; theme_color = "#0f2d3a"
                        analysis_narrative = f"Bullish momentum verified above 9 EMA. Candle: {detected_pattern}."
                    elif not higher_tf_is_bullish and C <= live_ema9:
                        if abs(ema_extension_pct) <= max_ema_extension: status_msg = "📉 9 EMA ENTRY WINDOW"; theme_color = "#4a121a"
                        else: status_msg = "🩸 9 EMA SHORT CASCADE"; theme_color = "#350d13"
                        analysis_narrative = f"Bearish continuation under 9 EMA. Candle: {detected_pattern}."
                    else:
                        status_msg = "⚪ NO-MAN'S LAND"; theme_color = "#1f232a"
                        analysis_narrative = f"Asset spinning tightly inside internal trading bands. Candle: {detected_pattern}."
                    
                    # --- HEADER CONTROLS ---
                    st.markdown(f"""
                        <div class="card-header-container">
                            <span class="card-header-title">{clean_display_name}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.button("❌ Remove Asset", key=f"clear_slot_{slot_idx}", on_click=remove_asset_callback, args=(slot_idx,), use_container_width=True)
                    
                    if detected_pattern != "None":
                        st.markdown(f"<p style='text-align:center; margin-top:4px; margin-bottom:2px; font-size:12px; color:#3a86ff;'><b>Forming: {detected_pattern}</b></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='text-align:center; margin-top:4px; margin-bottom:2px; font-size:12px; color:#5c6370;'>Forming: Standard Bar</p>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style='background-color:{theme_color}; padding:8px; border-radius:4px; text-align:center; font-weight:bold; font-size:11px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.05); text-transform: uppercase;'>
                        {status_msg}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- CUSTOM CSS METRIC DISPLAY ---
                    st.markdown(f"""
                    <div class="metrics-row">
                        <div class="metric-box">
                            <div class="metric-label">Vol Z-Score</div>
                            <div class="metric-value">{volume_z_score:.1f} σ</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">9 EMA Dist</div>
                            <div class="metric-value">{ema_extension_pct*100:.2f}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- INLINE CANDLESTICK CHART INJECTION ---
                    plot_df = working_df[working_df.index.date == live_candle.name.date()].copy() if boundary_mode == "Purely Today's Session Fixed Baseline" else working_df.tail(20)
                    
                    grid_chart = go.Figure()
                    grid_chart.add_trace(go.Candlestick(
                        x=plot_df.index,
                        open=plot_df['Open'], high=plot_df['High'], low=plot_df['Low'], close=plot_df['Close'],
                        name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
                        increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
                    ))
                    grid_chart.add_trace(go.Scatter(
                        x=plot_df.index, y=plot_df['EMA_9'],
                        line=dict(color="#3a86ff", width=1.5),
                        name="9 EMA", hoverinfo='none'
                    ))
                    grid_chart.update_layout(
                        xaxis_rangeslider_visible=False,
                        xaxis=dict(visible=False, showgrid=False),
                        yaxis=dict(visible=False, showgrid=False),
                        template="plotly_dark",
                        height=160,
                        margin=dict(l=5, r=5, t=5, b=5),
                        showlegend=False
                    )
                    st.plotly_chart(grid_chart, use_container_width=True, key=f"inline_chart_{slot_idx}", config={'displayModeBar': False})
                    
                    # --- CORE ANALYSIS MODAL TRIGGER ---
                    if st.button(f"🔍 Open Workspace", key=f"workspace_btn_{slot_idx}", use_container_width=True):
                        open_expanded_workspace(clean_display_name, status_msg, theme_color, plot_df, resistance_ceiling, support_floor, analysis_narrative, detected_pattern)
                        
                except Exception as loop_err:
                    st.caption(f"⚠️ Anomaly in Slot {slot_idx}")
                    
            st.markdown('</div>', unsafe_allow_html=True)
