import pytest
import pandas as pd
from src.agents.state import AgentState, MacroData, Thesis, DebateRound, RiskAssessment
from src.agents.graph import (
    macro_analyst_node,
    bullish_researcher_node,
    bearish_advocate_node,
    risk_manager_node,
    build_financial_pipeline
)
from src.backtest.engine import BacktestEngine

def test_macro_analyst_node():
    initial_state: AgentState = {"ticker": "AAPL", "debate_history": []}
    updated_state = macro_analyst_node(initial_state)
    
    assert updated_state["execution_status"] == "macro_analyzed"
    assert updated_state["macro_data"] is not None
    assert isinstance(updated_state["macro_data"], MacroData)
    assert updated_state["macro_data"].interest_rate > 0

def test_bullish_researcher_node():
    initial_state: AgentState = {"ticker": "AAPL", "debate_history": []}
    updated_state = bullish_researcher_node(initial_state)
    
    assert updated_state["execution_status"] == "bullish_thesis_ready"
    assert updated_state["bullish_thesis"] is not None
    assert isinstance(updated_state["bullish_thesis"], Thesis)
    assert updated_state["bullish_thesis"].stance == "LONG"

def test_bearish_advocate_node():
    initial_state: AgentState = {"ticker": "AAPL", "debate_history": []}
    updated_state = bearish_advocate_node(initial_state)
    
    assert updated_state["execution_status"] == "debated"
    assert len(updated_state["debate_history"]) == 1
    assert isinstance(updated_state["debate_history"][0], DebateRound)

def test_risk_manager_node():
    initial_state: AgentState = {"ticker": "AAPL", "debate_history": []}
    updated_state = risk_manager_node(initial_state)
    
    assert updated_state["execution_status"] == "risk_approved"
    assert updated_state["risk_assessment"] is not None
    assert isinstance(updated_state["risk_assessment"], RiskAssessment)
    assert updated_state["risk_assessment"].approved is True
    assert 0.0 <= updated_state["risk_assessment"].position_size_pct <= 100.0

def test_full_pipeline_execution():
    app = build_financial_pipeline()
    initial_state = {"ticker": "MSFT", "debate_history": []}
    final_state = app.invoke(initial_state)
    
    assert final_state["execution_status"] == "risk_approved"
    assert final_state["macro_data"] is not None
    assert final_state["bullish_thesis"] is not None
    assert len(final_state["debate_history"]) > 0
    assert final_state["risk_assessment"].approved is True

def test_backtest_engine():
    engine = BacktestEngine(initial_capital=100000.0)
    
    # 21 dates and 21 price points yield exactly 20 return periods after dropna()
    dates = pd.date_range(start="2026-01-01", periods=21, freq='B')
    prices = pd.Series([100 + i * 0.5 for i in range(21)], index=dates)
    
    results = engine.run_backtest(stance="LONG", position_size_pct=10.0, price_data=prices)
    
    assert results["initial_capital"] == 100000.0
    assert results["final_portfolio_value"] > 100000.0
    assert "sharpe_ratio" in results
    assert "max_drawdown_pct" in results
    assert "hit_rate_pct" in results
    assert results["total_trading_days"] == 20