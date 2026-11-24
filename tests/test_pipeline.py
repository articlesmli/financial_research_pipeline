import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.utils.portfolio_optimizer import optimize_multi_asset_portfolio
from src.agents.graph import build_financial_pipeline


@patch("src.utils.portfolio_optimizer.yf.download")
def test_portfolio_optimizer(mock_yf_download):
    # Provide synthetic price data to avoid network calls and database locks
    dates = pd.date_range(start="2026-01-01", periods=30, freq='B')
    mock_df = pd.DataFrame({
        "AAPL": [100 + i for i in range(30)],
        "MSFT": [200 + i * 0.5 for i in range(30)]
    }, index=dates)
    
    # yfinance returns a DataFrame with 'Close' column level when multiple tickers are passed
    mock_yf_download.return_value = pd.DataFrame({
        ("Close", "AAPL"): mock_df["AAPL"],
        ("Close", "MSFT"): mock_df["MSFT"]
    }, index=dates)
    
    result = optimize_multi_asset_portfolio(["AAPL", "MSFT"], period="1mo")
    assert isinstance(result, dict)
    assert "optimal_weights" in result
    
    total_weight = sum(result["optimal_weights"].values())
    assert abs(total_weight - 1.0) < 1e-3


@patch("src.agents.graph.llm")
def test_pipeline_integration(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Simulated pipeline integration output."
    mock_llm.invoke.return_value = mock_response
    
    app = build_financial_pipeline()
    initial_state = {
        "ticker": "AAPL",
        "debate_history": [],
        "debate_rounds": 0,
        "risk_assessment": None
    }
    final_state = app.invoke(initial_state)
    
    assert final_state["ticker"] == "AAPL"
    assert "debate_history" in final_state
    assert final_state["risk_assessment"] is not None