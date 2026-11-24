import os
import chromadb
from chromadb.utils import embedding_functions

class FinancialRAGStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="sec_filings_and_news",
            embedding_function=self.embedding_fn
        )

    def ingest_document(self, doc_id: str, text: str, metadata: dict):
        """Ingests SEC filing text or earnings transcripts into the vector store."""
        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )

    def query_context(self, query: str, ticker: str, n_results: int = 3) -> list[str]:
        """Retrieves relevant document snippets for a given ticker and query."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"ticker": ticker}
            )
            documents = results.get("documents", [[]])
            return documents[0] if documents else []
        except Exception as e:
            # Fallback if no documents match ticker metadata yet
            return [f"No custom vector documents found for {ticker}. Proceeding with general analysis. Error: {str(e)}"]
