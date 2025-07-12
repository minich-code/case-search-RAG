import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.src.config_params.config_params import RetrievalConfig

@dataclass
class Document:
    content: str
    metadata: Dict[str, Any] = None
    score: Optional[float] = None

class RetrievalService:
    """
    Service for retrieving relevant documents from a Pinecone vector index.
    Designed for async pipeline integration.
    """

    def __init__(self, config: RetrievalConfig):
        """
        Initializes the retrieval service with the provided configuration.

        Args:
            config (RetrievalConfig): Configuration for Pinecone and retrieval.

        Raises:
            ValueError: If the configuration is invalid.
            ConnectionError: If Pinecone initialization fails.
        """
        if not isinstance(config, RetrievalConfig):
            raise ValueError("Config must be an instance of RetrievalConfig.")
        self.config = config
        self.index = None
        self._initialize_pinecone()

    def _initialize_pinecone(self):
        """
        Initializes the Pinecone client and connects to the specified index.

        Raises:
            ConnectionError: If Pinecone initialization or index connection fails.
        """
        try:
            print("Initializing Pinecone connection...")
            pc = Pinecone(api_key=self.config.pinecone_api_key)
            available_indexes = pc.list_indexes().names()
            if self.config.pinecone_index_name not in available_indexes:
                raise ValueError(
                    f"Index '{self.config.pinecone_index_name}' not found. "
                    f"Available indexes: {', '.join(available_indexes)}"
                )
            self.index = pc.Index(self.config.pinecone_index_name)
            print(f"✅ Successfully connected to Pinecone index: '{self.config.pinecone_index_name}'")
        except Exception as e:
            raise ConnectionError(f"Pinecone initialization failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def retrieve(self, query_embedding: List[float]) -> List[Document]:
        """
        Retrieves top-k candidates from Pinecone using the query embedding.

        Args:
            query_embedding (List[float]): The query embedding vector.

        Returns:
            List[Document]: List of retrieved documents with content, metadata, and scores.

        Raises:
            ValueError: If the query embedding is invalid.
            RuntimeError: If the retrieval operation fails.
        """
        if not query_embedding or not isinstance(query_embedding, list) or not all(isinstance(x, (int, float)) for x in query_embedding):
            raise ValueError("query_embedding must be a non-empty list of numbers.")

        try:
            loop = asyncio.get_event_loop()
            query_response = await loop.run_in_executor(
                None,
                lambda: self.index.query(
                    vector=query_embedding,
                    top_k=self.config.retrieval_top_k,
                    include_metadata=True
                )
            )
            candidates = [
                Document(
                    content=match.metadata.get('text', ''),
                    metadata=match.metadata,
                    score=match.score
                ) for match in query_response.matches if match.metadata
            ]
            if not candidates:
                print("⚠️ No candidates found for the given query.")
            else:
                print(f"✅ Retrieved {len(candidates)} documents.")
            return candidates
        except Exception as e:
            print(f"Error during retrieval: {e}")
            raise RuntimeError(f"Retrieval failed: {e}")