from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class MacroData(BaseModel):
    timestamp: str
    interest_rate: float
    inflation_rate: float
    gdp_growth: float
    sentiment_score: float = Field(..., description="Normalized market sentiment score between -1.0 and 1.0")
    key_drivers: List[str]

class Thesis(BaseModel):
    ticker: str
    stance: Literal["LONG", "SHORT", "NEUTRAL"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str
    catalysts: List[str]

class DebateRound(BaseModel):
    bullish_argument: str
    bearish_rebuttal: str
    risk_flags: List[str]

class RiskAssessment(BaseModel):
    approved: bool
    position_size_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of portfolio allocated")
    max_drawdown_limit: float
    rationale: str

class AgentState(TypedDict):
    ticker: str
    macro_data: Optional[MacroData]
    bullish_thesis: Optional[Thesis]
    bearish_thesis: Optional[Thesis]
    debate_history: List[DebateRound]
    risk_assessment: Optional[RiskAssessment]
    execution_status: str

# Alias so graph.py imports succeed seamlessly
FinancialState = AgentState