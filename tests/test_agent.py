import pytest
import pandas as pd
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


def test_macro_node():
    initial_state: AgentState = {"ticker": "AAPL", "debate_history": [], "debate_rounds": 0, "risk_assessment": None}
    updated_state = macro_node(initial_state)
    
    assert "debate_history" in updated_state
    assert len(updated_state["debate_history"]) == 1
    assert updated_state["debate_history"][0]["agent"] == "Macro Analyst"

def test_bull_node():
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

def test_bear_node():
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

def test_risk_manager_node():
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

def test_full_pipeline_execution():
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