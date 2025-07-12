import asyncio
from typing import List
import voyageai
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.src.config_params.config_params import EmbeddingConfig

class EmbeddingService:
    """Service for creating embeddings using Voyage AI."""

    def __init__(self, config: EmbeddingConfig):
        """
        Initializes the embedding service with the provided configuration.

        Args:
            config (EmbeddingConfig): Configuration for the embedding service.

        Raises:
            ValueError: If the configuration is invalid or client initialization fails.
        """
        if not isinstance(config, EmbeddingConfig):
            raise ValueError("Config must be an instance of EmbeddingConfig.")
        self.config = config
        try:
            self.client = voyageai.Client(api_key=self.config.api_key)
            print(f"EmbeddingService initialized with model '{self.config.model_name}'.")
        except Exception as e:
            raise ValueError(f"Failed to initialize Voyage AI client: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed(self, texts: List[str], input_type: str) -> List[List[float]]:
        """
        Embeds a list of texts for either queries or documents.

        Args:
            texts (List[str]): A list of non-empty strings to embed.
            input_type (str): Either "query" or "document".

        Returns:
            List[List[float]]: List of embedding vectors (1024-dimensional for voyage-law-2).

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If embedding fails after retries.
        """
        if not texts or not isinstance(texts, list) or not all(isinstance(t, str) and t.strip() for t in texts):
            raise ValueError("Input 'texts' must be a non-empty list of non-empty strings.")
        if input_type not in ["query", "document"]:
            raise ValueError("Input 'input_type' must be either 'query' or 'document'.")

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
            print(f"Error during embedding with Voyage AI: {e}")
            raise RuntimeError(f"Embedding failed: {e}")