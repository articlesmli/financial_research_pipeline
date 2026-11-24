import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.agents.graph import (
    macro_node,
    bull_node,
    bear_node,
    risk_manager_node,
    build_financial_pipeline,
    AgentState,
    RiskAssessmentObject
)
from src.backtest.engine import BacktestEngine


@patch("src.agents.graph.llm")
def test_macro_node(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Rates are stable and inflation is cooling."
    mock_llm.invoke.return_value = mock_response
    
    initial_state: AgentState = {"ticker": "AAPL", "debate_history": [], "debate_rounds": 0, "risk_assessment": None}
    updated_state = macro_node(initial_state)
    
    assert "debate_history" in updated_state
    assert len(updated_state["debate_history"]) == 1
    assert updated_state["debate_history"][0]["agent"] == "Macro Analyst"

@patch("src.agents.graph.llm")
def test_bull_node(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Strong balance sheet and high consumer demand."
    mock_llm.invoke.return_value = mock_response
    
    initial_state: AgentState = {
        "ticker": "AAPL", 
        "debate_history": [{"agent": "Macro Analyst", "content": "Rates are stable."}], 
        "debate_rounds": 0, 
        "risk_assessment": None
    }
    updated_state = bull_node(initial_state)
    
    assert "debate_history" in updated_state
    assert len(updated_state["debate_history"]) == 1
    assert updated_state["debate_history"][0]["agent"] == "Bullish Researcher"

@patch("src.agents.graph.llm")
def test_bear_node(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Valuation is stretched and supply chain risks remain."
    mock_llm.invoke.return_value = mock_response
    
    initial_state: AgentState = {
        "ticker": "AAPL", 
        "debate_history": [{"agent": "Macro Analyst", "content": "Rates are stable."}], 
        "debate_rounds": 0, 
        "risk_assessment": None
    }
    updated_state = bear_node(initial_state)
    
    assert "debate_history" in updated_state
    assert len(updated_state["debate_history"]) == 1
    assert updated_state["debate_history"][0]["agent"] == "Bearish Advocate"

@patch("src.agents.graph.llm")
def test_risk_manager_node(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Risk is balanced. Position sizing approved."
    mock_llm.invoke.return_value = mock_response
    
    initial_state: AgentState = {
        "ticker": "AAPL",
        "debate_history": [{"agent": "Macro Analyst", "content": "Rates are stable."}],
        "debate_rounds": 0,
        "risk_assessment": None
    }
    updated_state = risk_manager_node(initial_state)
    
    assert "debate_rounds" in updated_state
    assert updated_state["risk_assessment"] is not None
    assert isinstance(updated_state["risk_assessment"], RiskAssessmentObject)

@patch("src.agents.graph.llm")
def test_full_pipeline_execution(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Simulated market research and analysis conclusion."
    mock_llm.invoke.return_value = mock_response
    
    app = build_financial_pipeline()
    initial_state = {"ticker": "MSFT", "debate_history": [], "debate_rounds": 0, "risk_assessment": None}
    final_state = app.invoke(initial_state)
    
    assert final_state["debate_rounds"] > 0
    assert final_state["risk_assessment"] is not None
    assert len(final_state["debate_history"]) > 0

def test_backtest_engine():
    engine = BacktestEngine(initial_capital=100000.0)
    
    dates = pd.date_range(start="2026-01-01", periods=21, freq='B')
    prices = pd.Series([100 + i * 0.5 for i in range(21)], index=dates)
    
    results = engine.run_backtest(stance="LONG", position_size_pct=10.0, price_data=prices)
    
    assert results["initial_capital"] == 100000.0
    assert results["final_portfolio_value"] > 100000.0
    assert "sharpe_ratio" in results
    assert "total_return_pct" in results