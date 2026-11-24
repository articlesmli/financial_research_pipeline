from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from src.agents.graph import build_financial_pipeline
from src.backtest.engine import BacktestEngine
from src.utils.market_data import fetch_historical_prices
from src.utils.logger import setup_logger
from src.utils.database import init_db, SessionLocal, AnalysisAuditLog
from src.utils.alerts import send_trade_alert
from src.utils.pdf_generator import generate_pdf_report
import json

logger = setup_logger("FastAPIApp")

app = FastAPI(
    title="Agentic Financial Research & Backtesting API",
    description="Enterprise multi-agent decision engine integrated with persistent audit logging, quantitative backtesting, automated PDF tearsheets, and live WebSocket streaming.",
    version="2.2.2"
)

@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized successfully.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AnalysisRequest(BaseModel):
    ticker: str
    initial_capital: float = 100000.0
    period: str = "1mo"

    @field_validator('ticker', mode='before')
    @classmethod
    def parse_ticker(cls, v):
        if isinstance(v, list):
            return str(v[0]).strip().upper() if v else "AAPL"
        return str(v).strip().upper()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def execute_analysis_workflow(request: AnalysisRequest):
    ticker = request.ticker
    
    # 1. Run LangGraph Multi-Agent Pipeline with Multi-Turn Debates
    pipeline = build_financial_pipeline()
    initial_state = {"ticker": ticker, "debate_history": []}
    config = {"configurable": {"thread_id": f"session-{ticker}"}}
    final_state = pipeline.invoke(initial_state, config=config)
    
    risk_assessment = final_state.get("risk_assessment")
    if not risk_assessment or not getattr(risk_assessment, "approved", False):
        return {
            "ticker": ticker,
            "status": "REJECTED",
            "message": "Risk Manager rejected the trade configuration."
        }

    stance = getattr(risk_assessment, "stance", "LONG")
    position_size = getattr(risk_assessment, "position_size_pct", 5.0)
    
    # 2. Fetch Market Data
    price_data = fetch_historical_prices(ticker, period=request.period)

    # 3. Execute Backtest
    engine = BacktestEngine(initial_capital=request.initial_capital)
    results = engine.run_backtest(
        stance=stance,
        position_size_pct=position_size,
        price_data=price_data
    )

    return {
        "ticker": ticker,
        "status": "APPROVED",
        "stance": stance,
        "position_size_pct": position_size,
        "backtest_performance": results
    }

@app.post("/analyze")
def analyze_stock(request: AnalysisRequest, db: Session = Depends(get_db)):
    ticker = request.ticker
    logger.info(f"API Request received for ticker: {ticker}")
    
    try:
        response_data = execute_analysis_workflow(request)
        if response_data.get("status") == "REJECTED":
            return response_data
    except Exception as e:
        logger.error(f"Analysis workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")

    results = response_data.get("backtest_performance", {})

    # Save to SQLite/PostgreSQL audit log
    try:
        audit_entry = AnalysisAuditLog(
            ticker=ticker,
            initial_capital=request.initial_capital,
            stance=response_data.get("stance"),
            position_size_pct=response_data.get("position_size_pct"),
            final_portfolio_value=results.get("final_portfolio_value"),
            sharpe_ratio=results.get("sharpe_ratio"),
            sortino_ratio=results.get("sortino_ratio"),
            calmar_ratio=results.get("calmar_ratio"),
            max_drawdown=results.get("max_drawdown"),
            var_95=results.get("var_95"),
            hit_rate=results.get("hit_rate"),
            full_payload=response_data
        )
        db.add(audit_entry)
        db.commit()
    except Exception as db_err:
        logger.error(f"Failed to write audit log: {db_err}")

    # Dispatch Webhook Alert
    send_trade_alert(
        ticker, 
        response_data.get("stance"), 
        response_data.get("position_size_pct"), 
        results.get("final_portfolio_value", request.initial_capital)
    )

    return response_data

@app.websocket("/ws/analysis/{ticker}")
async def websocket_analysis_endpoint(websocket: WebSocket, ticker: str):
    """Real-time WebSocket streaming endpoint for live agent deliberations and backtesting."""
    await manager.connect(websocket)
    clean_ticker = str(ticker).strip().upper()
    try:
        await websocket.send_text(json.dumps({"status": "STARTED", "message": f"Initialized live streaming session for {clean_ticker}"}))
        
        pipeline = build_financial_pipeline()
        initial_state = {"ticker": clean_ticker, "debate_history": []}
        
        await websocket.send_text(json.dumps({"agent": "Macro & Research Committee", "status": "Executing multi-turn adversarial debate..."}))
        final_state = pipeline.invoke(initial_state)
        
        await websocket.send_text(json.dumps({"agent": "Risk Manager", "status": "Deliberation finalized. Compiling quantitative backtest..."}))
        await websocket.send_text(json.dumps({"status": "COMPLETED", "payload": str(final_state)}))
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_text(json.dumps({"status": "ERROR", "detail": str(e)}))
        manager.disconnect(websocket)

@app.post("/download-pdf")
def download_pdf_report(request: AnalysisRequest):
    """Generates and streams an institutional PDF investment committee report (tearsheet)."""
    try:
        analysis_result = execute_analysis_workflow(request)
        clean_ticker = request.ticker
        pdf_bytes = generate_pdf_report(analysis_result)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={clean_ticker}_investment_report.pdf"}
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

@app.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AnalysisAuditLog).order_by(AnalysisAuditLog.timestamp.desc()).limit(10).all()
    return {"audit_logs": [
        {
            "id": l.id,
            "timestamp": l.timestamp,
            "ticker": l.ticker,
            "stance": l.stance,
            "final_portfolio_value": l.final_portfolio_value,
            "sharpe_ratio": l.sharpe_ratio
        } for l in logs
    ]}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "financial-research-pipeline"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Financial Research & Backtesting Pipeline API. Visit /docs for documentation."}