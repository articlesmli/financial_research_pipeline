import sys
from src.agents.graph import build_financial_pipeline
from src.backtest.engine import BacktestEngine
from src.utils.logger import setup_logger
from src.utils.market_data import fetch_historical_prices

logger = setup_logger("MainPipeline")

def run_pipeline(ticker: str):
    logger.info(f"=== Starting Financial Research & Backtesting Pipeline for {ticker} ===")
    
    # 1. Initialize and run the LangGraph Multi-Agent Pipeline
    try:
        app = build_financial_pipeline()
        initial_state = {"ticker": ticker, "debate_history": []}
        
        logger.info("Invoking Multi-Agent Decision Graph (Macro -> Bull/Bear -> Risk)...")
        final_state = app.invoke(initial_state)
        
        risk_assessment = final_state.get("risk_assessment")
        if not risk_assessment or not getattr(risk_assessment, "approved", False):
            logger.warning(f"Pipeline halted: Risk Manager rejected the trade for {ticker}.")
            return

        stance = getattr(risk_assessment, "stance", None) or getattr(risk_assessment, "recommendation", "LONG")
        position_size = getattr(risk_assessment, "position_size_pct", 10.0)
        logger.info(f"Pipeline Approved! Stance: {stance} | Position Size: {position_size}%")
        
    except Exception as e:
        logger.error(f"Error executing agent pipeline: {e}")
        return

    # 2. Fetch Market Data for Backtesting
    try:
        price_data = fetch_historical_prices(ticker, period="1mo")
        logger.info(f"Loaded {len(price_data)} periods of price data for backtesting.")
    except Exception as e:
        logger.error(f"Failed to fetch price data: {e}")
        return

    # 3. Execute Event-Driven Backtest
    try:
        logger.info("Running Quantitative Backtesting Engine...")
        engine = BacktestEngine(initial_capital=100000.0)
        results = engine.run_backtest(
            stance=stance, 
            position_size_pct=position_size, 
            price_data=price_data
        )
        
        # 4. Display Results Summary
        print("\n" + "="*50)
        print(f" FINANCIAL BACKTEST PERFORMANCE REPORT: {ticker} ")
        print("="*50)
        print(f" Initial Capital      : ${results['initial_capital']:,.2f}")
        print(f" Final Portfolio Value: ${results['final_portfolio_value']:,.2f}")
        print(f" Sharpe Ratio         : {results['sharpe_ratio']:.2f}")
        print(f" Max Drawdown         : {results['max_drawdown_pct']:.2f}%")
        print(f" Hit Rate             : {results['hit_rate_pct']:.2f}%")
        print(f" Total Trading Days   : {results['total_trading_days']}")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Error executing backtest engine: {e}")

if __name__ == "__main__":
    target_ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    run_pipeline(target_ticker)