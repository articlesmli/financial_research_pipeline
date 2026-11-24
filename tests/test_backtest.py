import pytest
import pandas as pd
from src.backtest.engine import BacktestEngine

def test_backtest_long_stance():
    engine = BacktestEngine(initial_capital=100000.0)
    
    # 21 dates and 21 price points yield exactly 20 return periods after dropna()
    dates = pd.date_range(start="2026-01-01", periods=21, freq='B')
    prices = pd.Series([100 + i * 0.5 for i in range(21)], index=dates) # Upward trend
    
    results = engine.run_backtest(stance="LONG", position_size_pct=10.0, price_data=prices)
    
    assert results["initial_capital"] == 100000.0
    assert results["final_portfolio_value"] > 100000.0
    assert "sharpe_ratio" in results
    assert "max_drawdown_pct" in results
    assert "hit_rate_pct" in results
    assert results["total_trading_days"] == 20

def test_backtest_short_stance():
    engine = BacktestEngine(initial_capital=100000.0)
    
    # Declining prices should generate positive returns for a SHORT stance
    dates = pd.date_range(start="2026-01-01", periods=21, freq='B')
    prices = pd.Series([100 - i * 0.5 for i in range(21)], index=dates) # Downward trend
    
    results = engine.run_backtest(stance="SHORT", position_size_pct=10.0, price_data=prices)
    
    assert results["initial_capital"] == 100000.0
    assert results["final_portfolio_value"] > 100000.0
    assert results["total_trading_days"] == 20