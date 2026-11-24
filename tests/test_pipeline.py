import pandas as pd
import pytest
from src.backtest.engine import BacktestEngine
from src.utils.portfolio_optimizer import optimize_multi_asset_portfolio

def test_backtest_engine_calculations():
    # Create synthetic price series
    dates = pd.date_range(start="2026-01-01", periods=50, freq="B")
    prices = [100.0 + i * 0.5 for i in range(50)]
    df = pd.DataFrame({"Close": prices}, index=dates)

    engine = BacktestEngine(initial_capital=100000.0)
    results = engine.run_backtest(stance="LONG", position_size_pct=10.0, price_data=df)

    assert results["initial_capital"] == 100000.0
    assert results["final_portfolio_value"] > 100000.0
    assert "sharpe_ratio" in results
    assert "cvar_95" in results

def test_portfolio_optimizer():
    weights = optimize_multi_asset_portfolio(["AAPL", "MSFT"], period="1mo")
    assert isinstance(weights, dict)
    assert sum(weights.values()) == pytest.approx(1.0, rel=1e-2)
