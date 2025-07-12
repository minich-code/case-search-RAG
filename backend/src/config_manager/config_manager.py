import os
from pathlib import Path
from box import ConfigBox
from dotenv import load_dotenv
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH
from backend.src.config_params.config_params import EmbeddingConfig, RetrievalConfig, RerankerConfig, LLMConfig, ResponseConfig

class ConfigManager:
    """
    A configuration manager that reads the config file and provides validated
    configurations for embedding, retrieval, reranking, LLM, and response components.
    """

    def __init__(self, config_filepath: str = CONFIG_FILEPATH):
        """
        Initializes the ConfigManager by loading environment variables and the
        configuration file.

        Args:
            config_filepath (str): Path to the configuration YAML file.

        Raises:
            ValueError: If the configuration file is empty, invalid, or missing required sections.
        """
        load_dotenv()
        self.config_filepath = Path(config_filepath)
        self.config = self._load_config()

    def _load_config(self) -> ConfigBox:
        """
        Loads and validates the configuration from the YAML file.

        Returns:
            ConfigBox: Loaded configuration object.

        Raises:
            ValueError: If the configuration file is empty, invalid, or missing required sections.
        """
        try:
            config = read_yaml(self.config_filepath)
            if not config:
                raise ValueError(f"Configuration file at {self.config_filepath} is empty or invalid.")
            required_sections = {'embedding', 'pinecone', 'retrieval', 'reranker', 'generation', 'response'}
            missing_sections = required_sections - set(config.keys())
            if missing_sections:
                raise ValueError(f"Missing required config sections: {missing_sections}")
            return config
        except Exception as e:
            raise ValueError(f"Failed to load or parse configuration file: {e}")

    @staticmethod
    def _get_required_env_var(var_name: str) -> str:
        """
        Retrieves a required environment variable or raises an error.

        Args:
            var_name (str): Name of the environment variable.

        Returns:
            str: Value of the environment variable.

        Raises:
            ValueError: If the environment variable is not set.
        """
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Required environment variable '{var_name}' is not set.")
        return value

    def get_embedding_config(self) -> EmbeddingConfig:
        """
        Extracts and validates the embedding configuration from the YAML file.

        Returns:
            EmbeddingConfig: Validated embedding configuration object.

        Raises:
            ValueError: If the 'embedding' section or required fields are missing/invalid.
        """
        try:
            embedding_config = self.config.embedding
            if not hasattr(embedding_config, 'model_name'):
                raise ValueError("Missing 'model_name' in 'embedding' configuration.")
            api_key = self._get_required_env_var("VOYAGE_API_KEY")
            return EmbeddingConfig(
                api_key=api_key,
                model_name=embedding_config.model_name
            )
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid 'embedding' configuration: {e}")

    def get_retrieval_config(self) -> RetrievalConfig:
        """
        Extracts and validates the retrieval configuration from the YAML file.

        Returns:
            RetrievalConfig: Validated retrieval configuration object.

        Raises:
            ValueError: If the 'pinecone' or 'retrieval' sections or required fields are missing/invalid.
        """
        try:
            pinecone_config = self.config.pinecone
            retrieval_config = self.config.retrieval
            required_pinecone_fields = ['index_name', 'region', 'cloud']
            for field in required_pinecone_fields:
                if not hasattr(pinecone_config, field):
                    raise ValueError(f"Missing '{field}' in 'pinecone' configuration.")
            if not hasattr(retrieval_config, 'top_k_candidates'):
                raise ValueError("Missing 'top_k_candidates' in 'retrieval' configuration.")
            api_key = self._get_required_env_var("PINECONE_API_KEY")
            return RetrievalConfig(
                pinecone_api_key=api_key,
                pinecone_index_name=pinecone_config.index_name,
                pinecone_region=pinecone_config.region,
                pinecone_cloud=pinecone_config.cloud,
                retrieval_top_k=retrieval_config.top_k_candidates
            )
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid 'pinecone' or 'retrieval' configuration: {e}")

    def get_reranker_config(self) -> RerankerConfig:
        """
        Extracts and validates the reranker configuration from the YAML file.

        Returns:
            RerankerConfig: Validated reranker configuration object.

        Raises:
            ValueError: If the 'reranker' section or required fields are missing/invalid.
        """
        try:
            reranker_config = self.config.reranker
            if not hasattr(reranker_config, 'model_name') or not hasattr(reranker_config, 'top_n'):
                raise ValueError("Missing 'model_name' or 'top_n' in 'reranker' configuration.")
            return RerankerConfig(
                model_name=reranker_config.model_name,
                top_n=reranker_config.top_n
            )
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid 'reranker' configuration: {e}")

    def get_llm_config(self) -> LLMConfig:
        """
        Extracts and validates the LLM configuration from the YAML file.

        Returns:
            LLMConfig: Validated LLM configuration object.

        Raises:
            ValueError: If the 'generation' section or required fields are missing/invalid.
        """
        try:
            generation_config = self.config.generation
            if not hasattr(generation_config, 'providers') or not generation_config.providers:
                raise ValueError("Missing or empty 'providers' in 'generation' configuration.")
            for provider in generation_config.providers:
                if not all(key in provider for key in ['model_name', 'provider']):
                    raise ValueError("Each provider in 'generation' must have 'model_name' and 'provider'.")
            return LLMConfig(
                providers=generation_config.providers
            )
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid 'generation' configuration: {e}")

    def get_response_config(self) -> ResponseConfig:
        """
        Extracts and validates the response configuration from the YAML file.

        Returns:
            ResponseConfig: Validated response configuration object.

        Raises:
            ValueError: If the 'response' section or required fields are missing/invalid.
        """
        try:
            response_config = self.config.response
            if not hasattr(response_config, 'max_citations'):
                raise ValueError("Missing 'max_citations' in 'response' configuration.")
            return ResponseConfig(
                max_citations=response_config.max_citations
            )
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid 'response' configuration: {e}")