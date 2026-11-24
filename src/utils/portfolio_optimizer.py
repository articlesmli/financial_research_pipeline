import numpy as np
import pandas as pd
import cvxpy as cp
import yfinance as yf

def optimize_multi_asset_portfolio(tickers: list[str], period: str = "1yr") -> dict:
    data = yf.download(tickers, period=period, progress=False)['Close']
    if isinstance(data, pd.Series):
        data = data.to_frame()
        data.columns = tickers

    returns = data.pct_change().dropna()
    mean_returns = returns.mean().values * 252  # Annualized
    cov_matrix = returns.cov().values * 252     # Annualized

    n = len(tickers)
    w = cp.Variable(n)
    
    portfolio_return = cp.sum(cp.multiply(mean_returns, w))
    portfolio_risk = cp.quad_form(w, cov_matrix)
    
    # Minimize Risk for Target Return (Mean-Variance Optimization)
    objective = cp.Minimize(portfolio_risk)
    constraints = [
        cp.sum(w) == 1.0,
        w >= 0.0  # Long-only constraint
    ]
    
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS)

    weights = w.value if w.value is not None else np.ones(n) / n
    weights = np.clip(weights, 0, 1)
    weights /= np.sum(weights)

    return {
        "tickers": tickers,
        "optimal_weights": {tickers[i]: float(round(weights[i], 4)) for i in range(n)},
        "annualized_return": float(portfolio_return.value) if portfolio_return.value else 0.0,
        "annualized_volatility": float(np.sqrt(portfolio_risk.value)) if portfolio_risk.value else 0.0
    }