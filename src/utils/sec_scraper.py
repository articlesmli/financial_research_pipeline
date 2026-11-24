import requests
from src.utils.rag import FinancialRAGStore

class SECFilingIngester:
    def __init__(self):
        self.rag_store = FinancialRAGStore()

    def fetch_and_ingest_filing(self, ticker: str, cik: str = "0000320193"): # Default CIK for AAPL as example
        headers = {"User-Agent": "InstitutionalResearchBot research@fund.com"}
        url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                recent_filings = data.get("filings", {}).get("recent", {})
                forms = recent_filings.get("form", [])
                descriptions = recent_filings.get("primaryDocument", [])
                
                # Ingest latest 10-Q or Form 4 snippet
                for i, form in enumerate(forms[:5]):
                    if form in ["10-Q", "10-K", "4"]:
                        doc_id = f"{ticker}-{form}-{i}"
                        text_snippet = f"SEC Filing {form} filed by {ticker}. Primary document: {descriptions[i] if i < len(descriptions) else 'N/A'}"
                        self.rag_store.ingest_document(
                            doc_id=doc_id,
                            text=text_snippet,
                            metadata={"ticker": ticker, "form": form}
                        )
                return True
        except Exception as e:
            print(f"SEC Ingestion warning: {e}")
        return False
