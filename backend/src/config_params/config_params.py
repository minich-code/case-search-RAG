from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class EmbeddingConfig:
    api_key: str
    model_name: str

@dataclass
class RetrievalConfig:
    pinecone_api_key: str
    pinecone_index_name: str
    pinecone_region: str
    pinecone_cloud: str
    retrieval_top_k: int

@dataclass
class RerankerConfig:
    model_name: str
    top_n: int

@dataclass
class LLMConfig:
    providers: List[Dict[str, str]]

@dataclass
class ResponseConfig:
    max_citations: int