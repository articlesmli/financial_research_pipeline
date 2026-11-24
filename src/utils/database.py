import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pipeline_audit.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisAuditLog(Base):
    __tablename__ = "analysis_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ticker = Column(String, index=True)
    initial_capital = Column(Float)
    stance = Column(String)
    position_size_pct = Column(Float)
    final_portfolio_value = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    calmar_ratio = Column(Float)
    max_drawdown = Column(Float)
    var_95 = Column(Float)
    cvar_95 = Column(Float)
    hit_rate = Column(Float)
    debate_transcript = Column(Text)
    full_payload = Column(JSON)

def init_db():
    Base.metadata.create_all(bind=engine)