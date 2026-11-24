from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOllama
import operator
import time

class AgentState(TypedDict):
    ticker: str
    debate_history: Annotated[List[Dict[str, str]], operator.add]
    debate_rounds: int
    risk_assessment: Any

# Note: Ensure this model string matches your active Anthropic SDK version/tier
llm = ChatOllama(model="llama3")

def extract_text(response) -> str:
    """Robust helper to extract plain text from LLM responses regardless of block structure."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)

class RiskAssessmentObject:
    def __init__(self, approved: bool, stance: str, size: float, max_drawdown_limit: float = 0.20, rationale: str = ""):
        self.approved = approved
        self.stance = stance
        self.position_size_pct = size
        self.max_drawdown_limit = max_drawdown_limit
        self.rationale = rationale

def macro_node(state: AgentState):
    print("--- [ENTER] MACRO NODE ---")
    start = time.time()
    ticker = str(state.get("ticker", "AAPL")).strip().upper()
    prompt = f"Analyze macroeconomic conditions and rate outlook for {ticker}."
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        print(f"--- [ERROR] MACRO NODE LLM FAIL: {e} ---")
        raise
    content = extract_text(response)
    print(f"--- [EXIT] MACRO NODE: {time.time() - start:.2f}s ---")
    return {"debate_history": [{"agent": "Macro Analyst", "content": content}]}

def bull_node(state: AgentState):
    print("--- [ENTER] BULL NODE ---")
    start = time.time()
    ticker = str(state.get("ticker", "AAPL")).strip().upper()
    history_str = "\n".join([f"{d['agent']}: {d['content']}" for d in state["debate_history"]])
    prompt = f"Given the macro context:\n{history_str}\n\nFormulate a strong bullish investment thesis for {ticker}."
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        print(f"--- [ERROR] BULL NODE LLM FAIL: {e} ---")
        raise
    content = extract_text(response)
    print(f"--- [EXIT] BULL NODE: {time.time() - start:.2f}s ---")
    return {"debate_history": [{"agent": "Bullish Researcher", "content": content}]}

def bear_node(state: AgentState):
    print("--- [ENTER] BEAR NODE ---")
    start = time.time()
    ticker = str(state.get("ticker", "AAPL")).strip().upper()
    history_str = "\n".join([f"{d['agent']}: {d['content']}" for d in state["debate_history"]])
    prompt = f"Given the debate so far:\n{history_str}\n\nCritique the bull thesis and present downside risks for {ticker}."
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        print(f"--- [ERROR] BEAR NODE LLM FAIL: {e} ---")
        raise
    content = extract_text(response)
    print(f"--- [EXIT] BEAR NODE: {time.time() - start:.2f}s ---")
    return {"debate_history": [{"agent": "Bearish Advocate", "content": content}]}

def risk_manager_node(state: AgentState):
    print("--- [ENTER] RISK MANAGER NODE ---")
    start = time.time()
    ticker = str(state.get("ticker", "AAPL")).strip().upper()
    history_str = "\n".join([f"{d['agent']}: {d['content']}" for d in state["debate_history"]])
    rounds = state.get("debate_rounds", 0) + 1
    
    prompt = f"""Review this investment debate for {ticker} (Round {rounds}/2):
{history_str}

Evaluate risk parameters. If the debate needs more refinement and you are under 2 rounds, output 'REVISE'. Otherwise, output 'APPROVED' with stance (LONG/SHORT) and position size percentage."""
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        print(f"--- [ERROR] RISK MANAGER NODE LLM FAIL: {e} ---")
        raise
    
    content = extract_text(response)
    content_upper = content.upper()
    
    approved = "APPROVED" in content_upper or rounds >= 2
    stance = "LONG" if "SHORT" not in content_upper else "SHORT"
    
    print(f"--- [EXIT] RISK MANAGER NODE: {time.time() - start:.2f}s (Approved: {approved}, Round: {rounds}) ---")
    return {
        "debate_rounds": rounds,
        "risk_assessment": RiskAssessmentObject(
            approved=approved, 
            stance=stance, 
            size=5.0, 
            rationale=content
        )
    }

def should_continue(state: AgentState):
    risk_assessment = state.get("risk_assessment")
    is_approved = getattr(risk_assessment, "approved", False) if risk_assessment else False
    if is_approved or state.get("debate_rounds", 0) >= 2:
        return "end"
    return "refine"

def build_financial_pipeline():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("macro", macro_node)
    workflow.add_node("bull", bull_node)
    workflow.add_node("bear", bear_node)
    workflow.add_node("risk_manager", risk_manager_node)
    
    workflow.set_entry_point("macro")
    workflow.add_edge("macro", "bull")
    workflow.add_edge("bull", "bear")
    workflow.add_edge("bear", "risk_manager")
    
    workflow.add_conditional_edges(
        "risk_manager",
        should_continue,
        {
            "refine": "bull",
            "end": END
        }
    )
    
    return workflow.compile()