
import asyncio
from typing import List, Dict, Any
import torch
from sentence_transformers import CrossEncoder
from backend.src.components.retrieval import Document
from backend.src.config_params.config_params import RerankerConfig
from tenacity import retry, stop_after_attempt, wait_exponential

class RerankerService:
    """
    Service for reranking documents using a Cross-Encoder model.
    Designed for async pipeline integration.
    """

    def __init__(self, config: RerankerConfig):
        """
        Initializes the reranker service with the provided configuration.

        Args:
            config (RerankerConfig): Configuration for the reranker.

        Raises:
            ValueError: If the configuration is invalid.
            RuntimeError: If model initialization fails.
        """
        if not isinstance(config, RerankerConfig):
            raise ValueError("Config must be an instance of RerankerConfig.")
        self.config = config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"RerankerService initializing on device: '{self.device}'")
        try:
            self.model = CrossEncoder(self.config.model_name, device=self.device)
            print(f"Cross-Encoder model '{self.config.model_name}' loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Cross-Encoder model: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def rerank(self, query: str, documents: List[Document]) -> List[Document]:
        """
        Reranks a list of documents based on relevance to a query.

        Args:
            query (str): The query text.
            documents (List[Document]): List of documents to rerank.

        Returns:
            List[Document]: Top-N reranked documents with updated rerank_score in metadata.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If reranking fails.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        if not documents or not all(isinstance(doc, Document) for doc in documents):
            print("No valid documents provided for reranking.")
            return []

        try:
            loop = asyncio.get_event_loop()
            pairs = [[query, doc.content] for doc in documents]

            def predict_scores():
                return self.model.predict(pairs, show_progress_bar=False)

            scores = await loop.run_in_executor(None, predict_scores)

            # Update documents with rerank_score in metadata
            reranked_docs = []
            for doc, score in zip(documents, scores):
                doc.metadata = doc.metadata or {}
                doc.metadata['rerank_score'] = float(score)  # Ensure JSON-serializable
                reranked_docs.append(doc)

            # Sort by rerank_score and take top_n
            reranked_docs = sorted(reranked_docs, key=lambda x: x.metadata.get('rerank_score', 0), reverse=True)
            top_reranked_docs = reranked_docs[:self.config.top_n]

            print(f"✅ Reranked {len(documents)} documents, kept top {len(top_reranked_docs)}.")
            return top_reranked_docs
        except Exception as e:
            print(f"Error during reranking: {e}")
            raise RuntimeError(f"Reranking failed: {e}")