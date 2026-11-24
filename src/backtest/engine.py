import numpy as np
import pandas as pd

class BacktestEngine:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital

    def run_backtest(self, stance: str, position_size_pct: float, price_data) -> dict:
        if price_data is None or (isinstance(price_data, pd.DataFrame) and price_data.empty) or (isinstance(price_data, pd.Series) and price_data.empty):
            raise ValueError("Price data is empty. Cannot run backtest.")

        # Robustly handle whether price_data is a DataFrame or a Series
        if isinstance(price_data, pd.DataFrame):
            if "Close" in price_data.columns:
                prices = price_data["Close"]
            else:
                prices = price_data.iloc[:, 0]
        else:
            prices = price_data

        # If prices is still a DataFrame (e.g. multi-index columns), grab the first column
        if isinstance(prices, pd.DataFrame):
            prices = prices.iloc[:, 0]

        daily_returns = prices.pct_change().dropna()
        allocation_weight = (position_size_pct / 100.0)
        
        strat_returns = (-daily_returns if stance == "SHORT" else daily_returns) * allocation_weight
        portfolio_curve = self.initial_capital * (1 + strat_returns).cumprod()
        final_val = float(portfolio_curve.iloc[-1]) if not portfolio_curve.empty else self.initial_capital

        total_return = (final_val - self.initial_capital) / self.initial_capital
        mean_daily = strat_returns.mean()
        std_daily = strat_returns.std()
        
        rf_daily = 0.04 / 252
        sharpe = float(((mean_daily - rf_daily) / (std_daily + 1e-9)) * np.sqrt(252))
        
        negative_returns = strat_returns[strat_returns < 0]
        downside_std = negative_returns.std()
        sortino = float(((mean_daily - rf_daily) / (downside_std + 1e-9)) * np.sqrt(252))
        
        rolling_max = portfolio_curve.cummax()
        drawdowns = (portfolio_curve - rolling_max) / rolling_max
        max_dd = float(drawdowns.min() * 100)
        calmar = float((total_return / abs(max_dd / 100)) if max_dd != 0 else 0.0)
        
        var_95 = float(np.percentile(strat_returns, 5) * self.initial_capital)
        cvar_95 = float(strat_returns[strat_returns <= np.percentile(strat_returns, 5)].mean() * self.initial_capital)
        
        winning_days = (strat_returns > 0).sum()
        total_days = len(strat_returns)
        hit_rate = float((winning_days / total_days) * 100) if total_days > 0 else 0.0

        return {
            "initial_capital": self.initial_capital,
            "final_portfolio_value": round(final_val, 2),
            "total_return_pct": round(total_return * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "calmar_ratio": round(calmar, 2),
            "max_drawdown": round(max_dd, 2),
            "var_95": round(var_95, 2),
            "cvar_95": round(cvar_95, 2),
            "hit_rate": round(hit_rate, 2)
        }