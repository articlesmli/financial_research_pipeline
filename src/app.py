import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Multi-Agent Financial Research & Backtesting Engine",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Financial Research & Backtesting Engine")
st.markdown("Enterprise-grade autonomous investment committee powered by **LangGraph**, **FastAPI**, **SQLAlchemy**, and quantitative backtesting.")

with st.sidebar:
    st.header("Analysis Parameters")
    
    # Ensure ticker input handles strings correctly and avoids list formatting
    raw_ticker = st.text_input("Stock Ticker", value="AAPL")
    if isinstance(raw_ticker, list):
        ticker = str(raw_ticker[0]).strip().upper() if raw_ticker else "AAPL"
    else:
        ticker = str(raw_ticker).strip().upper()

    initial_capital = st.number_input("Initial Capital ($)", value=100000.0, step=10000.0)
    period = st.selectbox("Historical Data Period", ["1mo", "3mo", "6mo", "1y"], index=0)
    
    run_button = st.button("🚀 Run Analysis & Backtest", type="primary")

if run_button:
    with st.spinner(f"Running multi-agent adversarial debate and quantitative backtest for {ticker}..."):
        try:
            payload = {
                "ticker": ticker,
                "initial_capital": float(initial_capital),
                "period": period
            }
            
            response = requests.post(
                "http://backend:8001/analyze",
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "REJECTED":
                    st.warning(f"Trade Rejected by Risk Manager: {data.get('message')}")
                else:
                    st.success("Analysis Completed & Audit Logged Successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Final Portfolio Value", f"${data.get('backtest_performance', {}).get('final_portfolio_value', 0):,.2f}")
                    with col2:
                        st.metric("Sharpe Ratio", f"{data.get('backtest_performance', {}).get('sharpe_ratio', 0):.2f}")
                    with col3:
                        st.metric("Stance", data.get("stance", "N/A"))
                        
                    with st.expander("📊 View Full Quantitative Backtest Performance"):
                        st.json(data.get("backtest_performance", {}))
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
                
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")