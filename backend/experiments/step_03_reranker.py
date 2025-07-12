# # filename: step_03_reranker.py
#
# import asyncio
# import os
# import yaml
# import torch
# from pathlib import Path
# from dataclasses import dataclass
# from typing import List, Dict, Any
#
# # --- Required Libraries ---
# # pip install voyageai pinecone-client python-dotenv pyyaml tenacity sentence-transformers torch
# from dotenv import load_dotenv
# from pinecone import Pinecone
# import voyageai
# from sentence_transformers import CrossEncoder
#
#
# # --- Unified Configuration System ---
# @dataclass
# class EmbeddingConfig:
#     api_key: str
#     model_name: str
#
#
# @dataclass
# class RerankerConfig:
#     model_name: str
#     top_n: int
#
#
# @dataclass
# class AppConfig:
#     embedding_config: EmbeddingConfig
#     reranker_config: RerankerConfig
#     pinecone_index_name: str
#     retrieval_top_k: int
#
#
# def load_app_config(config_path: Path) -> AppConfig:
#     """Loads all configurations from a YAML file and environment variables."""
#     if not config_path.is_file():
#         raise FileNotFoundError(f"Config file not found: {config_path}")
#
#     with open(config_path, 'r') as f:
#         cfg = yaml.safe_load(f)
#
#     return AppConfig(
#         embedding_config=EmbeddingConfig(
#             api_key=os.getenv("VOYAGE_API_KEY"),
#             model_name=cfg['embedding']['model_name']
#         ),
#         reranker_config=RerankerConfig(
#             model_name=cfg['reranker']['model_name'],
#             top_n=cfg['reranker']['top_n']
#         ),
#         pinecone_index_name=cfg['pinecone']['index_name'],
#         retrieval_top_k=cfg['retrieval']['top_k_candidates']
#     )
#
#
# # --- Service Classes ---
#
# class EmbeddingService:
#     """A focused service for creating embeddings using Voyage AI."""
#
#     def __init__(self, config: EmbeddingConfig):
#         self.client = voyageai.Client(api_key=config.api_key)
#         self.model_name = config.model_name
#
#     async def embed(self, texts: List[str], input_type: str) -> List[List[float]]:
#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(None, lambda: self.client.embed(
#             texts=texts, model=self.model_name, input_type=input_type, truncation=True
#         ))
#         return result.embeddings
#
#
# class RerankerService:
#     """A service for reranking search results using a Cross-Encoder model."""
#
#     def __init__(self, model_name: str):
#         # Automatically use GPU if available, otherwise CPU
#         self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
#         print(f"INFO: Initializing RerankerService on device: '{self.device}'")
#         self.model = CrossEncoder(model_name, device=self.device)
#         print(f"INFO: Cross-Encoder model '{model_name}' loaded successfully.")
#
#     def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
#         """Reranks a list of documents based on their relevance to a query."""
#         if not documents:
#             return []
#
#         # The cross-encoder expects pairs of (query, document_text)
#         pairs = [[query, doc['text']] for doc in documents]
#
#         # model.predict returns a list of scores
#         scores = self.model.predict(pairs, show_progress_bar=False)
#
#         # Add the score to each original document object
#         for doc, score in zip(documents, scores):
#             doc['rerank_score'] = score
#
#         # Sort the documents by the new rerank_score in descending order
#         reranked_docs = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
#
#         return reranked_docs
#
#
# class LegalRetriever:
#     """Performs retrieval, reranking, and context stitching."""
#
#     def __init__(self, config: AppConfig, embedding_service: EmbeddingService, reranker_service: RerankerService):
#         self.config = config
#         self.embedding_service = embedding_service
#         self.reranker_service = reranker_service
#
#         pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
#         self.index = pc.Index(self.config.pinecone_index_name)
#         print(f"INFO: Retriever initialized for Pinecone index '{self.config.pinecone_index_name}'.")
#
#     async def retrieve_context_packets(self, query: str) -> Dict[str, List[Dict]]:
#         """The full retrieve -> rerank -> stitch pipeline."""
#         # 1. Embed Query
#         query_embedding = (await self.embedding_service.embed([query], input_type="query"))[0]
#
#         # 2. Retrieve Initial Candidates (Recall)
#         print(f"INFO: Retrieving top {self.config.retrieval_top_k} candidates from Pinecone...")
#         query_response = self.index.query(
#             vector=query_embedding, top_k=self.config.retrieval_top_k, include_metadata=True
#         )
#         candidate_chunks = [match.metadata for match in query_response.matches]
#         if not candidate_chunks: return {}
#
#         # 3. Rerank the Candidates (Precision)
#         print(f"INFO: Reranking {len(candidate_chunks)} candidates...")
#         reranked_chunks = self.reranker_service.rerank(query, candidate_chunks)
#
#         # Keep only the top N results after reranking
#         top_reranked_chunks = reranked_chunks[:self.config.reranker_config.top_n]
#         print(f"INFO: Kept top {len(top_reranked_chunks)} results after reranking.")
#
#         # 4. Stitch Context for the BEST results
#         ids_to_fetch = set()
#         for chunk in top_reranked_chunks:
#             ids_to_fetch.add(chunk['id'])
#             base_id, current_seq = chunk['citation'], chunk['chunk_sequence']
#             if current_seq > 1: ids_to_fetch.add(f"{base_id}::chunk_{current_seq - 1}")
#             ids_to_fetch.add(f"{base_id}::chunk_{current_seq + 1}")
#
#         # 5. Fetch and Finalize Packets
#         print(f"INFO: Fetching final context for {len(ids_to_fetch)} unique chunks...")
#         fetch_response = self.index.fetch(ids=list(ids_to_fetch))
#         all_retrieved_chunks = [vec['metadata'] for vec in fetch_response.vectors.values()]
#
#         stitched_results = {}
#         for chunk in all_retrieved_chunks:
#             case_citation = chunk['citation']
#             if case_citation not in stitched_results: stitched_results[case_citation] = []
#             stitched_results[case_citation].append(chunk)
#
#         for case_citation in stitched_results:
#             stitched_results[case_citation].sort(key=lambda c: c['chunk_sequence'])
#
#         return stitched_results
#
#
# # --- Main Execution Block ---
# async def main():
#     """Demonstrates the full pipeline."""
#     load_dotenv()
#     try:
#         # Define and load config path robustly
#         script_path = Path(__file__).resolve()
#         project_root = script_path.parent.parent  # Adjust if structure differs
#         config_path = project_root / "config" / "config.yaml"
#
#         app_config = load_app_config(config_path)
#
#         # Initialize all services
#         embedding_service = EmbeddingService(app_config.embedding_config)
#         reranker_service = RerankerService(app_config.reranker_config.model_name)
#         retriever = LegalRetriever(app_config, embedding_service, reranker_service)
#
#         # Run a test query
#         query = "What is the exception to the rule in Foss v Harbottle?"
#         print(f"\n--- Running retrieval for query: '{query}' ---")
#
#         final_context = await retriever.retrieve_context_packets(query)
#
#         if not final_context:
#             print("No relevant context packets found.")
#             return
#
#         print("\n--- Stitched Context Packets Retrieved ---")
#         for case_citation, chunks in final_context.items():
#             print(f"\nCase: {case_citation}")
#             print("-" * 30)
#             for chunk in chunks:
#                 rerank_score = f"(rerank_score: {chunk.get('rerank_score', 'N/A'):.4f})" if 'rerank_score' in chunk else ""
#                 print(f"  [Chunk {chunk['chunk_sequence']}] {rerank_score} - Text: {chunk['text'][:150]}...")
#             print("-" * 30)
#
#     except FileNotFoundError as e:
#         print(f"\nCONFIGURATION ERROR: Could not find a required file. {e}")
#     except Exception as e:
#         print(f"\nAn unexpected error occurred: {e}")
#
#
# if __name__ == "__main__":
#     # Add this before running asyncio to install dependencies
#     # !pip install -q sentence-transformers torch
#     asyncio.run(main())



# filename: backend/experiments/retriever.py

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from box import ConfigBox
import torch
from sentence_transformers import CrossEncoder
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH

# Load .env file from the backend folder
load_dotenv(dotenv_path=Path("backend/.env"))


# --- Reranker Config ---
@dataclass
class RerankerConfig:
    model_name: str
    top_n: int


# --- Config Manager ---
class ConfigManager:
    """Manages loading and validation of configuration settings for the reranker service."""

    def __init__(self, config_path: str = CONFIG_FILEPATH):
        self.config_path = Path(config_path)

    def load_config(self) -> RerankerConfig:
        """Loads reranker configuration from the YAML file using read_yaml."""
        try:
            config = read_yaml(self.config_path)

            if not config or 'reranker' not in config:
                raise ValueError("Invalid configuration: 'reranker' section missing in config.yaml")

            reranker_config = config.reranker

            return RerankerConfig(
                model_name=reranker_config.get('model_name', 'BAAI/bge-reranker-base'),
                top_n=reranker_config.get('top_n', 5)
            )
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise


# --- Reranker Service ---
class RerankerService:
    """Service for reranking documents using a Cross-Encoder model."""

    def __init__(self, config: RerankerConfig):
        self.config = config
        # Automatically use GPU if available, otherwise CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"RerankerService initializing on device: '{self.device}'")
        self.model = CrossEncoder(self.config.model_name, device=self.device)
        print(f"Cross-Encoder model '{self.config.model_name}' loaded successfully.")

    async def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reranks a list of documents based on relevance to a query."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        if not documents:
            print("No documents provided for reranking.")
            return []

        try:
            # Run reranking in an executor to avoid blocking the async event loop
            loop = asyncio.get_event_loop()
            pairs = [[query, doc['text']] for doc in documents]

            def predict_scores():
                return self.model.predict(pairs, show_progress_bar=False)

            scores = await loop.run_in_executor(None, predict_scores)

            # Add scores to documents
            for doc, score in zip(documents, scores):
                doc['rerank_score'] = float(score)  # Ensure score is JSON-serializable

            # Sort by rerank_score in descending order and take top_n
            reranked_docs = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
            top_reranked_docs = reranked_docs[:self.config.top_n]

            print(f"Reranked {len(documents)} documents, kept top {len(top_reranked_docs)}.")
            return top_reranked_docs
        except Exception as e:
            print(f"Error during reranking: {e}")
            raise


# --- Main Test Function ---
async def main():
    """Test the reranker setup with dummy documents."""
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()

        # Initialize reranker service
        reranker = RerankerService(config)

        # Test query and dummy documents
        query = "What is the exception to the rule in Foss v Harbottle?"
        dummy_documents = [
            {"id": "doc1",
             "text": "The rule in Foss v Harbottle limits minority shareholder actions, but exceptions exist for ultra vires acts.",
             "citation": "Case1", "chunk_sequence": 1},
            {"id": "doc2", "text": "Foss v Harbottle does not apply when the company acts illegally or fraudulently.",
             "citation": "Case2", "chunk_sequence": 1},
            {"id": "doc3", "text": "Unrelated legal principle about contract law.", "citation": "Case3",
             "chunk_sequence": 1},
            {"id": "doc4",
             "text": "Another exception to Foss v Harbottle is when personal rights of shareholders are infringed.",
             "citation": "Case4", "chunk_sequence": 1}
        ]

        # Run reranking
        reranked_docs = await reranker.rerank(query, dummy_documents)

        if not reranked_docs:
            print("No reranked documents returned.")
            return

        print("\nReranked Documents:")
        for i, doc in enumerate(reranked_docs, 1):
            print(f"\nDocument {i}:")
            print(f"Citation: {doc.get('citation', 'N/A')}")
            print(f"Text: {doc.get('text', 'N/A')[:150]}...")
            print(f"Rerank Score: {doc.get('rerank_score', 'N/A'):.4f}")
            print(f"Chunk Sequence: {doc.get('chunk_sequence', 'N/A')}")

    except Exception as e:
        print(f"Error in reranking process: {e}")


# --- Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())