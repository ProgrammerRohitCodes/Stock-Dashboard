# AI-Powered Technical Stock Analysis Dashboard

A Streamlit app that performs **technical analysis** on multiple stocks and uses **Google Gemini** to generate human-readable trading insights (Buy / Hold / Sell) based on candlestick patterns and technical indicators.

---

## Features
- Fetches live stock data using **Yahoo Finance (yfinance)**  
- Visualizes candlestick charts with **Plotly**  
- Calculates multiple indicators — SMA, EMA, Bollinger Bands, VWAP  
- Uses **Gemini 2.0 Flash** to generate natural-language insights  
- Provides structured “Buy / Sell / Hold” recommendations  
- Fully interactive Streamlit dashboard  

---

## Setup & Usage

### 1. Clone this repository
```bash
git clone https://github.com/yourusername/AI-Stock-Dashboard.git
cd AI-Stock-Dashboard
```

### 2. Install dependencies
```bash
pip install streamlit yfinance pandas plotly google-generativeai pytz
```

### 3. Add your Gemini API key  
Open the Python file and replace:
```python
GOOGLE_API_KEY = "your_api_key_here"
```
with your actual Gemini API key:
```python
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
```

*(Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

### 4. Run the Streamlit app
```bash
streamlit run app.py
```

---

## ⚙️ How It Works
1. Enter one or more stock tickers (e.g., `AAPL, MSFT, GOOG`) in the sidebar.  
2. Choose the technical indicators you want to display.  
3. Click **Fetch Data** to load and visualize the stock data.  
4. The AI model analyzes the chart image and indicators, then outputs:
   - A recommended **action** (e.g., *Buy*, *Hold*, *Sell*)  
   - A **justification** explaining the reasoning behind that action  

---

## Tech Stack
- **Python**  
- **Streamlit**  
- **Plotly**  
- **Yahoo Finance (yfinance)**  
- **Google Gemini API**

---

## Example Output
| Stock | Recommendation |
|:------|:----------------|
| AAPL  | Strong Buy      |
| MSFT  | Hold            |
| GOOG  | Weak Sell       |

---

## License
This project is open-source and free to use for learning or non-commercial purposes.

---

*(Created with ❤️ by a passionate AI/ML developer.)*
