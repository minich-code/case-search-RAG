
import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH

# Environment Loading
load_dotenv()


# --- Data Class ---
@dataclass
class RetrievalConfig:
    pinecone_index_name: str
    pinecone_api_key: str
    retrieval_top_k: int


# --- Config Manager (Local to this file for self-contained testing) ---
class ConfigManager:
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        self.config_path = Path(config_path)

    def load_config(self) -> RetrievalConfig:
        """Loads ONLY retrieval-related config with enhanced validation"""
        config = read_yaml(self.config_path)

        # Structural validation
        if not config:
            raise ValueError("Configuration file is empty or invalid")

        required_sections = {'pinecone', 'retrieval'}
        missing_sections = required_sections - set(config.keys())
        if missing_sections:
            raise ValueError(f"Missing required config sections: {missing_sections}")

        # Environment validation
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY must be set in environment variables")

        return RetrievalConfig(
            pinecone_index_name=config.pinecone['index_name'],
            pinecone_api_key=api_key,
            retrieval_top_k=config.retrieval.get('top_k_candidates', 5)
        )


# --- Retrieval Service (The robust, non-blocking hybrid version) ---
class RetrievalService:
    """
    Service for retrieving relevant documents from a Pinecone vector index.
    It is designed to be non-blocking and robust for use in an async pipeline.
    """

    def __init__(self, config: RetrievalConfig):
        if not isinstance(config, RetrievalConfig):
            raise TypeError("config must be an instance of RetrievalConfig")

        self.config = config
        self.index = None
        self._initialize_pinecone()

    def _initialize_pinecone(self):
        """Handles Pinecone connection setup with robust validation."""
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

    async def retrieve(self, query_embedding: List[float]) -> List[Dict[str, Any]]:
        """Retrieves top-k candidates from Pinecone in a non-blocking way."""
        if not query_embedding or not isinstance(query_embedding, list):
            raise ValueError("query_embedding must be a non-empty list of floats.")

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
            candidates = [match.metadata for match in query_response.matches if match.metadata]
            if not candidates:
                print("⚠️ No candidates found for the given query.")
            return candidates
        except Exception as e:
            print(f"❌ Error during retrieval operation: {e}")
            raise RuntimeError(f"Retrieval operation failed: {e}")


# --- Test Function (Uses the local ConfigManager defined above) ---
async def main():
    """Demonstrates the usage of the RetrievalService using the local ConfigManager."""
    try:
        # Step 1: Initialize the local ConfigManager.
        print("--- Loading configuration using local manager ---")
        config_manager = ConfigManager()  # Uses CONFIG_FILEPATH by default

        # Step 2: Load the retrieval-specific config.
        retrieval_config = config_manager.load_config()
        print("✅ Retrieval configuration loaded.")

        # Step 3: Initialize the service.
        retriever = RetrievalService(config=retrieval_config)

        # Step 4: Run the test.
        dummy_embedding = [0.1] * 1024
        print(f"\nRetrieving top {retrieval_config.retrieval_top_k} candidates...")
        results = await retriever.retrieve(dummy_embedding)

        print(f"\nRetrieved {len(results)} documents:")
        for i, doc in enumerate(results, 1):
            print(f"\nDocument {i}:")
            print(f"Citation: {doc.get('citation', 'N/A')}")
            print(f"Excerpt: {doc.get('text', 'N/A')[:100]}...")

    except Exception as e:
        print(f"\n💥 Retrieval test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())