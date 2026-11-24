import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.utils.portfolio_optimizer import optimize_multi_asset_portfolio
from src.agents.graph import build_financial_pipeline


def test_portfolio_optimizer():
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