# -----------------------GEMINI--------------------
# embeddings.py
import os
import asyncio
from dataclasses import dataclass
from typing import List, Optional
import voyageai
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from pathlib import Path
from box import ConfigBox
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH

# --- 1. Configuration Dataclass ---
@dataclass
class EmbeddingConfig:
    api_key: str
    model_name: str


# --- 2. Configuration Manager Class ---
class ConfigManager:
    def __init__(self, config_path: str = CONFIG_FILEPATH):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> ConfigBox:
        """Loads and validates the configuration from the YAML file."""
        try:
            config = read_yaml(self.config_path)
            if not config or 'embedding' not in config:
                raise ValueError("Configuration error: 'embedding' section missing in config file")
            return config
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {str(e)}")

    def get_embedding_config(self) -> EmbeddingConfig:
        """Extracts and validates the embedding configuration."""
        try:
            embedding_config = self.config.embedding
            api_key = os.getenv("VOYAGE_API_KEY")
            if not api_key:
                raise ValueError("Environment variable 'VOYAGE_API_KEY' not found")

            if not hasattr(embedding_config, 'model_name'):
                raise ValueError("Configuration error: 'model_name' missing in embedding config")

            return EmbeddingConfig(
                api_key=api_key,
                model_name=embedding_config.model_name
            )
        except Exception as e:
            raise ValueError(f"Invalid embedding configuration: {str(e)}")


# --- 3. The Embedding Service Class ---
class EmbeddingService:
    """A focused service for creating embeddings using Voyage AI."""

    def __init__(self, config: EmbeddingConfig):
        if not isinstance(config, EmbeddingConfig):
            raise ValueError("Invalid configuration: must be an EmbeddingConfig instance")

        self.config = config
        try:
            self.client = voyageai.Client(api_key=self.config.api_key)
            print(f"EmbeddingService initialized with model '{self.config.model_name}'.")
        except Exception as e:
            raise ValueError(f"Failed to initialize Voyage AI client: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed(self, texts: List[str], input_type: str) -> List[List[float]]:
        """
        Embeds a list of texts. Can be used for queries or documents.

        Args:
            texts: A list of strings to embed (non-empty)
            input_type: Either "query" or "document"

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not texts or not isinstance(texts, list):
            raise ValueError("Input texts must be a non-empty list")

        if not all(isinstance(text, str) and text.strip() for text in texts):
            raise ValueError("All texts must be non-empty strings")

        if input_type not in ["query", "document"]:
            raise ValueError("input_type must be either 'query' or 'document'")

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.client.embed(
                    texts=texts,
                    model=self.config.model_name,
                    input_type=input_type,
                    truncation=True
                )
            )
            return result.embeddings
        except Exception as e:
            print(f"Error during embedding with Voyage AI: {str(e)}")
            raise  # Reraise the exception for tenacity to handle retries


# --- Example Usage (for testing this file directly) ---
async def main():
    load_dotenv()

    try:
        # Initialize Configuration Manager
        config_manager = ConfigManager()

        # Get Embedding Configuration
        embedding_config = config_manager.get_embedding_config()

        embedder = EmbeddingService(embedding_config)

        # Test embedding a query
        query = "What is the standard for a preliminary objection?"
        query_embedding = await embedder.embed([query], input_type="query")
        print(f"\nSuccessfully embedded a query. Vector length: {len(query_embedding[0])}")

        # Test embedding documents
        docs = ["This is the first legal document.", "This is the second legal document."]
        doc_embeddings = await embedder.embed(docs, input_type="document")
        print(f"Successfully embedded {len(doc_embeddings)} documents.")

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())