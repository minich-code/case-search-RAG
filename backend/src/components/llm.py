# import os
# import asyncio
# import random
# import logging
# from typing import List, Dict, Any
# from groq import Groq, GroqError
# from together import Together
# from openai import AsyncOpenAI, OpenAIError
# from anthropic import AsyncAnthropic, AnthropicError
# from tenacity import retry, stop_after_attempt, wait_exponential
# from backend.src.config_params.config_params import LLMConfig
# from backend.src.components.retrieval import Document
#
# # Configure logging
# logging.basicConfig(level=logging.DEBUG, filename='llm_service.log', format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# class LLMService:
#     """
#     Manages requests to multiple LLM providers with fallback for response generation.
#     Designed for async pipeline integration.
#     """
#
#     def __init__(self, config: LLMConfig):
#         """
#         Initializes the LLM service with the provided configuration.
#
#         Args:
#             config (LLMConfig): Configuration for LLM providers.
#
#         Raises:
#             ValueError: If no valid providers are configured.
#         """
#         if not isinstance(config, LLMConfig):
#             raise ValueError("Config must be an instance of LLMConfig.")
#         self.providers = []
#         self.clients = {}
#         self._initialize_clients(config.providers)
#         logger.info("LLMService initialized with providers: %s", [p['model_name'] for p in self.providers])
#
#     def _initialize_clients(self, providers: List[Dict[str, str]]):
#         """
#         Initializes clients for configured LLM providers.
#
#         Args:
#             providers (List[Dict[str, str]]): List of provider configurations.
#
#         Raises:
#             ValueError: If no valid providers are initialized.
#         """
#         for provider_config in providers:
#             model_name = provider_config.get('model_name')
#             provider = provider_config.get('provider')
#             api_key = os.getenv(f"{provider.upper()}_API_KEY")
#
#             if not api_key:
#                 print(f"Skipping {provider} ({model_name}) due to missing {provider.upper()}_API_KEY")
#                 logger.warning(f"Skipping {provider} ({model_name}) due to missing API key")
#                 continue
#
#             try:
#                 if provider == "groq":
#                     self.clients[provider] = Groq(api_key=api_key)
#                 elif provider == "together":
#                     self.clients[provider] = Together(api_key=api_key)
#                 elif provider == "openai":
#                     self.clients[provider] = AsyncOpenAI(api_key=api_key)
#                 elif provider == "anthropic":
#                     self.clients[provider] = AsyncAnthropic(api_key=api_key)
#                 else:
#                     print(f"Unsupported provider: {provider}")
#                     logger.warning(f"Unsupported provider: {provider}")
#                     continue
#                 self.providers.append({"model_name": model_name, "provider": provider})
#                 print(f"Initialized {provider} with model: {model_name}")
#                 logger.info(f"Initialized {provider} with model: {model_name}")
#             except Exception as e:
#                 print(f"Error initializing {provider} ({model_name}): {e}")
#                 logger.error(f"Error initializing {provider} ({model_name}): {e}")
#
#         if not self.providers:
#             logger.error("No valid LLM providers configured")
#             raise ValueError("No valid LLM providers configured. Check .env and config.yaml.")
#
#     @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
#     async def generate(self, query: str, documents: List[Document], model_id: str, max_tokens: int = 2048) -> str:
#         """
#         Generates a response using the specified LLM model, incorporating retrieved documents.
#
#         Args:
#             query (str): The input query.
#             documents (List[Document]): List of reranked documents.
#             model_id (str): The model name to use (e.g., 'deepseek-ai/DeepSeek-V3').
#             max_tokens (int): Maximum number of tokens for the response. Defaults to 2048.
#
#         Returns:
#             str: The generated response.
#
#         Raises:
#             ValueError: If inputs are invalid or no provider matches the model_id.
#             RuntimeError: If all providers fail.
#         """
#         if not query or not isinstance(query, str):
#             raise ValueError("Query must be a non-empty string.")
#         if not model_id or not isinstance(model_id, str):
#             raise ValueError("Model_id must be a non-empty string.")
#         if not isinstance(max_tokens, int) or max_tokens <= 0:
#             raise ValueError("max_tokens must be a positive integer.")
#         if not any(p['model_name'] == model_id for p in self.providers):
#             logger.error(f"No provider configured for model_id '{model_id}'")
#             raise ValueError(f"No provider configured for model_id '{model_id}'.")
#
#         # Format context from documents
#         context = "\n\n".join([f"Document {i+1} (Score: {doc.metadata.get('rerank_score', 'N/A')}):\n{doc.content}" for i, doc in enumerate(documents)])
#         system_prompt = (
#             "You are a helpful assistant. Use the provided context to answer the query accurately and concisely."
#             f"\n\nContext:\n{context}"
#         )
#         user_prompt = f"Query: {query}"
#
#         # Shuffle providers for random fallback
#         providers = [p for p in self.providers if p['model_name'] == model_id]
#         if not providers:
#             logger.error(f"No provider found for model_id '{model_id}'")
#             raise ValueError(f"No provider found for model_id '{model_id}'.")
#         random.shuffle(providers)
#
#         best_response = None
#         for provider_config in providers:
#             provider = provider_config['provider']
#             model_name = provider_config['model_name']
#             print(f"Trying {provider} with model {model_name}")
#             logger.info(f"Trying {provider} with model {model_name}")
#
#             try:
#                 if provider == "groq":
#                     completion = await asyncio.get_event_loop().run_in_executor(
#                         None,
#                         lambda: self.clients[provider].chat.completions.create(
#                             model=model_name,
#                             messages=[
#                                 {"role": "system", "content": system_prompt},
#                                 {"role": "user", "content": user_prompt}
#                             ],
#                             temperature=0.1,
#                             max_tokens=max_tokens
#                         )
#                     )
#                     response = completion.choices[0].message.content
#                 elif provider == "together":
#                     completion = await asyncio.get_event_loop().run_in_executor(
#                         None,
#                         lambda: self.clients[provider].chat.completions.create(
#                             model=model_name,
#                             messages=[
#                                 {"role": "system", "content": system_prompt},
#                                 {"role": "user", "content": user_prompt}
#                             ],
#                             temperature=0.1,
#                             max_tokens=max_tokens
#                         )
#                     )
#                     response = completion.choices[0].message.content
#                 elif provider == "openai":
#                     completion = await self.clients[provider].chat.completions.create(
#                         model=model_name,
#                         messages=[
#                             {"role": "system", "content": system_prompt},
#                             {"role": "user", "content": user_prompt}
#                         ],
#                         temperature=0.1,
#                         max_tokens=max_tokens
#                     )
#                     response = completion.choices[0].message.content
#                 elif provider == "anthropic":
#                     completion = await self.clients[provider].messages.create(
#                         model=model_name,
#                         system=system_prompt,
#                         messages=[{"role": "user", "content": user_prompt}],
#                         max_tokens=max_tokens,
#                         temperature=0.1
#                     )
#                     response = completion.content[0].text
#
#                 if not response:
#                     logger.warning(f"{provider} returned empty response")
#                     print(f"Warning: {provider} returned empty response.")
#                     continue
#
#                 # Validate response format, but accept as fallback if no better response
#                 if "Final Answer:" in response:
#                     logger.debug(f"{provider} response: {response[:500]}...")
#                     print(f"✅ {provider} response: {response[:100]}...")
#                     return response
#                 else:
#                     logger.warning(f"{provider} response missing 'Final Answer:' header: {response[:500]}...")
#                     print(f"Warning: {provider} response missing 'Final Answer:' header.")
#                     best_response = response if not best_response else best_response
#
#             except (GroqError, OpenAIError, AnthropicError, Exception) as e:
#                 logger.error(f"Error with {provider} ({model_name}): {e}")
#                 print(f"Error with {provider} ({model_name}): {e}")
#                 continue
#
#         if best_response:
#             logger.info("Using fallback response without 'Final Answer:' header")
#             print("Using fallback response without 'Final Answer:' header")
#             return best_response
#
#         logger.error("All LLM providers failed")
#         raise RuntimeError("All LLM providers failed. Check API keys and configurations.")

import os
import asyncio
import random
import logging
from typing import List, Dict, Any
from groq import Groq, GroqError
from together import Together
from openai import AsyncOpenAI, OpenAIError
from anthropic import AsyncAnthropic, AnthropicError
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.src.config_params.config_params import LLMConfig
from backend.src.components.retrieval import Document

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='llm_service.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMService:
    """
    Manages requests to multiple LLM providers with fallback for response generation.
    Designed for async pipeline integration.
    """

    def __init__(self, config: LLMConfig):
        """
        Initializes the LLM service with the provided configuration.

        Args:
            config (LLMConfig): Configuration for LLM providers.

        Raises:
            ValueError: If no valid providers are configured.
        """
        if not isinstance(config, LLMConfig):
            raise ValueError("Config must be an instance of LLMConfig.")
        self.providers = []
        self.clients = {}
        self._initialize_clients(config.providers)
        logger.info("LLMService initialized with providers: %s", [p['model_name'] for p in self.providers])

    def _initialize_clients(self, providers: List[Dict[str, str]]):
        """
        Initializes clients for configured LLM providers.

        Args:
            providers (List[Dict[str, str]]): List of provider configurations.

        Raises:
            ValueError: If no valid providers are initialized.
        """
        for provider_config in providers:
            model_name = provider_config.get('model_name')
            provider = provider_config.get('provider')
            api_key = os.getenv(f"{provider.upper()}_API_KEY")

            if not api_key:
                print(f"Skipping {provider} ({model_name}) due to missing {provider.upper()}_API_KEY")
                logger.warning(f"Skipping {provider} ({model_name}) due to missing API key")
                continue

            try:
                if provider == "groq":
                    self.clients[provider] = Groq(api_key=api_key)
                elif provider == "together":
                    self.clients[provider] = Together(api_key=api_key)
                elif provider == "openai":
                    self.clients[provider] = AsyncOpenAI(api_key=api_key)
                elif provider == "anthropic":
                    self.clients[provider] = AsyncAnthropic(api_key=api_key)
                else:
                    print(f"Unsupported provider: {provider}")
                    logger.warning(f"Unsupported provider: {provider}")
                    continue
                self.providers.append({"model_name": model_name, "provider": provider})
                print(f"Initialized {provider} with model: {model_name}")
                logger.info(f"Initialized {provider} with model: {model_name}")
            except Exception as e:
                print(f"Error initializing {provider} ({model_name}): {e}")
                logger.error(f"Error initializing {provider} ({model_name}): {e}")

        if not self.providers:
            logger.error("No valid LLM providers configured")
            raise ValueError("No valid LLM providers configured. Check .env and config.yaml.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, query: str, documents: List[Document], model_id: str, max_tokens: int = 2048) -> str:
        """
        Generates a response using the specified LLM model, incorporating retrieved documents.

        Args:
            query (str): The input query.
            documents (List[Document]): List of reranked documents.
            model_id (str): The model name to use (e.g., 'deepseek-ai/DeepSeek-V3').
            max_tokens (int): Maximum number of tokens for the response. Defaults to 2048.

        Returns:
            str: The generated response.

        Raises:
            ValueError: If inputs are invalid or no provider matches the model_id.
            RuntimeError: If all providers fail.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        if not model_id or not isinstance(model_id, str):
            raise ValueError("Model_id must be a non-empty string.")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer.")
        if not any(p['model_name'] == model_id for p in self.providers):
            logger.error(f"No provider configured for model_id '{model_id}'")
            raise ValueError(f"No provider configured for model_id '{model_id}'.")

        # Format context from documents
        context = "\n\n".join([f"Document {i+1} (Score: {doc.metadata.get('rerank_score', 'N/A')}):\n{doc.content}" for i, doc in enumerate(documents)])
        system_prompt = (
            "You are a helpful assistant. Use the provided context to answer the query accurately and concisely."
            f"\n\nContext:\n{context}"
        )
        user_prompt = f"Query: {query}"

        # Shuffle providers for random fallback
        providers = [p for p in self.providers if p['model_name'] == model_id]
        if not providers:
            logger.error(f"No provider found for model_id '{model_id}'")
            raise ValueError(f"No provider found for model_id '{model_id}'.")
        random.shuffle(providers)

        best_response = None
        for provider_config in providers:
            provider = provider_config['provider']
            model_name = provider_config['model_name']
            print(f"Trying {provider} with model {model_name}")
            logger.info(f"Trying {provider} with model {model_name}")

            try:
                if provider == "groq":
                    completion = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.clients[provider].chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.1,
                            max_tokens=max_tokens
                        )
                    )
                    response = completion.choices[0].message.content
                elif provider == "together":
                    completion = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.clients[provider].chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.1,
                            max_tokens=max_tokens
                        )
                    )
                    response = completion.choices[0].message.content
                elif provider == "openai":
                    completion = await self.clients[provider].chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=max_tokens
                    )
                    response = completion.choices[0].message.content
                elif provider == "anthropic":
                    completion = await self.clients[provider].messages.create(
                        model=model_name,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                        max_tokens=max_tokens,
                        temperature=0.1
                    )
                    response = completion.content[0].text

                if not response:
                    logger.warning(f"{provider} returned empty response")
                    print(f"Warning: {provider} returned empty response.")
                    continue

                # Validate response format, but accept as fallback if no better response
                if "Final Answer:" in response:
                    logger.debug(f"{provider} response: {response[:500]}...")
                    print(f"✅ {provider} response: {response[:100]}...")
                    return response
                else:
                    logger.warning(f"{provider} response missing 'Final Answer:' header: {response[:500]}...")
                    print(f"Warning: {provider} response missing 'Final Answer:' header.")
                    best_response = response if not best_response else best_response

            except (GroqError, OpenAIError, AnthropicError, Exception) as e:
                logger.error(f"Error with {provider} ({model_name}): {e}")
                print(f"Error with {provider} ({model_name}): {e}")
                continue

        if best_response:
            logger.info("Using fallback response without 'Final Answer:' header")
            print("Using fallback response without 'Final Answer:' header")
            return best_response

        logger.error("All LLM providers failed")
        raise RuntimeError("All LLM providers failed. Check API keys and configurations.")