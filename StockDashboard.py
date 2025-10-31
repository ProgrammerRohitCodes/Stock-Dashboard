# Libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import tempfile
import os
import json
from datetime import datetime, timedelta
import pytz

# Configure the API key 
GOOGLE_API_KEY = "your_api_key_here"
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-2.0-flash'
gen_model = genai.GenerativeModel(MODEL_NAME)

# Streamlit app setup
st.set_page_config(layout="wide")
st.title("AI-Powered Technical Stock Analysis Dashboard")
st.sidebar.header("Configuration")

# Input tickers
tickers_input = st.sidebar.text_input("Enter Stock Tickers (comma-separated):", "AAPL,MSFT,GOOG")
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

# Date range
end_date_default = datetime.today()
start_date_default = end_date_default - timedelta(days=365)
start_date = st.sidebar.date_input("Start Date", value=start_date_default)
end_date = st.sidebar.date_input("End Date", value=end_date_default)

# Technical indicators
st.sidebar.subheader("Technical Indicators")
indicators = st.sidebar.multiselect(
    "Select Indicators:",
    ["20-Day SMA", "20-Day EMA", "20-Day Bollinger Bands", "VWAP"],
    default=["20-Day SMA"]
)

# Fetch data button
if st.sidebar.button("Fetch Data"):
    stock_data = {}
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, multi_index=False)
        if not data.empty:
            # Convert index to India timezone
            data.index = data.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
            stock_data[ticker] = data
        else:
            st.warning(f"No data found for {ticker}.")
    st.session_state["stock_data"] = stock_data
    st.success("Stock data loaded successfully for: " + ", ".join(stock_data.keys()))

# Analysis
if "stock_data" in st.session_state and st.session_state["stock_data"]:

    def analyze_ticker(ticker, data):
        # Candlestick chart
        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlestick"
            )
        ])

        # Add indicators
        def add_indicator(indicator):
            if indicator == "20-Day SMA":
                sma = data['Close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(x=data.index, y=sma, mode='lines', name='SMA (20)'))
            elif indicator == "20-Day EMA":
                ema = data['Close'].ewm(span=20).mean()
                fig.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name='EMA (20)'))
            elif indicator == "20-Day Bollinger Bands":
                sma = data['Close'].rolling(window=20).mean()
                std = data['Close'].rolling(window=20).std()
                fig.add_trace(go.Scatter(x=data.index, y=sma+2*std, mode='lines', name='BB Upper'))
                fig.add_trace(go.Scatter(x=data.index, y=sma-2*std, mode='lines', name='BB Lower'))
            elif indicator == "VWAP":
                data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
                fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name='VWAP'))

        for ind in indicators:
            add_indicator(ind)

        fig.update_layout(xaxis_rangeslider_visible=False)

        # Save candlestick chart as image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.write_image(tmpfile.name)
            tmpfile_path = tmpfile.name
        with open(tmpfile_path, "rb") as f:
            image_bytes = f.read()
        os.remove(tmpfile_path)

        image_part = {"data": image_bytes, "mime_type": "image/png"}

        # Gemini prompt
        analysis_prompt = (
            f"You are a Stock Trader specializing in Technical Analysis. "
            f"Analyze the stock chart for {ticker} based on its candlestick chart and selected indicators. "
            f"Provide detailed justification and give a recommendation (Strong Buy / Buy / Weak Buy / Hold / Weak Sell / Sell / Strong Sell). "
            f"Return as JSON with keys 'action' and 'justification'."
        )

        contents = [
            {"role": "user", "parts": [analysis_prompt]},
            {"role": "user", "parts": [image_part]}
        ]

        response = gen_model.generate_content(contents=contents)

        try:
            result_text = response.text
            json_start_index = result_text.find('{')
            json_end_index = result_text.rfind('}') + 1
            if json_start_index != -1 and json_end_index > json_start_index:
                result = json.loads(result_text[json_start_index:json_end_index])
            else:
                raise ValueError("No valid JSON object found in the response")
        except Exception as e:
            result = {"action": "Error", "justification": str(e)}

        return fig, result

    tab_names = ["Overall Summary"] + list(st.session_state["stock_data"].keys())
    tabs = st.tabs(tab_names)
    overall_results = []

    for i, ticker in enumerate(st.session_state["stock_data"]):
        data = st.session_state["stock_data"][ticker]
        fig, result = analyze_ticker(ticker, data)
        overall_results.append({"Stock": ticker, "Recommendation": result.get("action", "N/A")})
        with tabs[i+1]:
            st.subheader(f"Analysis for {ticker}")
            st.plotly_chart(fig)
            st.write("**Detailed Justification:**")
            st.write(result.get("justification", "No justification provided."))

    with tabs[0]:
        st.subheader("Overall Structured Recommendations")
        df_summary = pd.DataFrame(overall_results)
        st.table(df_summary)
else:
    st.info("Please fetch stock data using the sidebar.")
