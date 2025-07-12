# import os
# import asyncio
# from dataclasses import dataclass, field
# from pathlib import Path
# from typing import List, Dict, Any, Optional
# from abc import ABC, abstractmethod
# from dotenv import load_dotenv
# from box import ConfigBox
# import aiohttp
# from backend.src.utils.common import read_yaml
# from backend.src.constants import CONFIG_FILEPATH
#
# # Load .env file
# load_dotenv(dotenv_path=Path("backend/.env"))
#
# # --- LLM Config ---
# @dataclass
# class LLMConfig:
#     available_models: List[Dict[str, Any]] = field(default_factory=list)
#
# # --- Config Manager ---
# class ConfigManager:
#     """Manages loading and validation of configuration settings for the LLM service."""
#     def __init__(self, config_path: str = CONFIG_FILEPATH):
#         self.config_path = Path(config_path)
#
#     def load_config(self) -> LLMConfig:
#         try:
#             config_data = read_yaml(self.config_path)
#             if not config_data or 'generation' not in config_data:
#                 raise ValueError("Invalid configuration: 'generation' section missing in config.yaml")
#             generation_config = config_data.generation
#             return LLMConfig(
#                 available_models=generation_config.get('available_models', [])
#             )
#         except Exception as e:
#             print(f"Error loading configuration: {e}")
#             raise
#
# # --- LLM Providers ---
# class LLMProvider(ABC):
#     """Abstract base class for all LLM API providers."""
#     def __init__(self, api_key: str):
#         if not api_key:
#             raise ValueError(f"{self.__class__.__name__} requires an API key.")
#         self.api_key = api_key
#
#     @abstractmethod
#     async def generate_response(self, session: aiohttp.ClientSession, model_name: str, system_prompt: str,
#                                user_prompt: str) -> str:
#         pass
#
# class GroqProvider(LLMProvider):
#     async def generate_response(self, session: aiohttp.ClientSession, model_name: str, system_prompt: str,
#                                user_prompt: str) -> str:
#         url = "https://api.groq.com/openai/v1/chat/completions"
#         headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
#         payload = {
#             "model": model_name,
#             "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
#             "temperature": 0.1
#         }
#         print(f"Sending request to Groq API: {url} with model {model_name}")
#         async with session.post(url, json=payload, headers=headers) as response:
#             try:
#                 response.raise_for_status()
#                 data = await response.json()
#                 print(f"Groq response: {data['choices'][0]['message']['content'][:100]}...")
#                 return data['choices'][0]['message']['content']
#             except aiohttp.ClientResponseError as e:
#                 error_body = await response.text()
#                 raise ValueError(f"Groq API request failed with status {e.status}: {error_body}")
#
# class TogetherAIProvider(LLMProvider):
#     async def generate_response(self, session: aiohttp.ClientSession, model_name: str, system_prompt: str,
#                                user_prompt: str) -> str:
#         url = "https://api.together.xyz/v1/chat/completions"
#         headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
#         payload = {
#             "model": model_name,
#             "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
#             "temperature": 0.1
#         }
#         print(f"Sending request to TogetherAI API: {url} with model {model_name}")
#         async with session.post(url, json=payload, headers=headers) as response:
#             try:
#                 response.raise_for_status()
#                 data = await response.json()
#                 print(f"TogetherAI response: {data['choices'][0]['message']['content'][:100]}...")
#                 return data['choices'][0]['message']['content']
#             except aiohttp.ClientResponseError as e:
#                 error_body = await response.text()
#                 raise ValueError(f"TogetherAI API request failed with status {e.status}: {error_body}")
#
# class OpenAIProvider(LLMProvider):
#     async def generate_response(self, session: aiohttp.ClientSession, model_name: str, system_prompt: str,
#                                user_prompt: str) -> str:
#         url = "https://api.openai.com/v1/chat/completions"
#         headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
#         payload = {
#             "model": model_name,
#             "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
#         }
#         print(f"Sending request to OpenAI API: {url} with model {model_name}")
#         async with session.post(url, json=payload, headers=headers) as response:
#             try:
#                 response.raise_for_status()
#                 data = await response.json()
#                 print(f"OpenAI response: {data['choices'][0]['message']['content'][:100]}...")
#                 return data['choices'][0]['message']['content']
#             except aiohttp.ClientResponseError as e:
#                 error_body = await response.text()
#                 raise ValueError(f"OpenAI API request failed with status {e.status}: {error_body}")
#
# class AnthropicProvider(LLMProvider):
#     async def generate_response(self, session: aiohttp.ClientSession, model_name: str, system_prompt: str,
#                                user_prompt: str) -> str:
#         url = "https://api.anthropic.com/v1/messages"
#         headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
#         payload = {
#             "model": model_name,
#             "system": system_prompt,
#             "messages": [{"role": "user", "content": user_prompt}],
#             "max_tokens": 4096,
#             "temperature": 0.1
#         }
#         print(f"Sending request to Anthropic API: {url} with model {model_name}")
#         async with session.post(url, json=payload, headers=headers) as response:
#             try:
#                 response.raise_for_status()
#                 data = await response.json()
#                 print(f"Anthropic response: {data['content'][0]['text'][:100]}...")
#                 return data['content'][0]['text']
#             except aiohttp.ClientResponseError as e:
#                 error_body = await response.text()
#                 raise ValueError(f"Anthropic API request failed with status {e.status}: {error_body}")
#
# # --- LLM Service ---
# class LLMService:
#     """Manages and routes requests to the appropriate LLM provider."""
#     def __init__(self, config: LLMConfig):
#         self.providers: Dict[str, LLMProvider] = {}
#         self.model_map: Dict[str, Dict] = {}
#         self._load_from_config(config.available_models)
#
#     def _load_from_config(self, available_models: List[Dict[str, Any]]):
#         provider_classes = {
#             "groq": GroqProvider,
#             "together": TogetherAIProvider,
#             "openai": OpenAIProvider,
#             "anthropic": AnthropicProvider
#         }
#         for model_config in available_models:
#             provider_name = model_config.get('provider')
#             if provider_name not in provider_classes:
#                 print(f"Skipping unsupported provider: {provider_name}")
#                 continue
#             api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
#             if not api_key:
#                 print(f"Skipping {model_config['id']} due to missing {provider_name.upper()}_API_KEY")
#                 continue
#             try:
#                 if provider_name not in self.providers:
#                     self.providers[provider_name] = provider_classes[provider_name](api_key)
#                 self.model_map[model_config['id']] = {
#                     "provider": provider_name,
#                     "model_name": model_config['model_name']
#                 }
#             except Exception as e:
#                 print(f"Error initializing {model_config['id']}: {e}")
#         print(f"LLMService initialized. Available models: {list(self.model_map.keys())}")
#         if not self.model_map:
#             print("WARNING: No LLM providers configured. Check your .env file and config.yaml.")
#
#     async def generate(self, model_id: str, system_prompt: str, user_prompt: str) -> str:
#         if model_id not in self.model_map:
#             raise ValueError(f"Model ID '{model_id}' is not available or its API key is missing.")
#         model_info = self.model_map[model_id]
#         provider = self.providers[model_info['provider']]
#         async with aiohttp.ClientSession() as session:
#             try:
#                 response = await provider.generate_response(session, model_info['model_name'], system_prompt,
#                                                            user_prompt)
#                 return response
#             except ValueError as e:
#                 raise e
#             except Exception as e:
#                 raise ValueError(f"An unexpected error occurred with provider {model_info['provider']}: {e}")
#
# # --- Main Test Function ---
# async def main():
#     try:
#         config_manager = ConfigManager()
#         config = config_manager.load_config()
#         llm_service = LLMService(config)
#         query = "What is the capital of Kenya?"
#         system_prompt = "You are a helpful assistant."
#         model_id = "llama3-8b-groq"
#         response = await llm_service.generate(model_id, system_prompt, query)
#         print(f"\nQuery: {query}")
#         print(f"Model: {model_id}")
#         print(f"Response: {response}")
#     except Exception as e:
#         print(f"Error in LLM generation: {e}")
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
import os
import asyncio
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from groq import Groq, GroqError
from together import Together
from openai import AsyncOpenAI, OpenAIError
from anthropic import AsyncAnthropic, AnthropicError
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH

# Load .env file
load_dotenv()


# --- LLM Config ---
@dataclass
class LLMConfig:
    providers: List[Dict[str, str]] = field(default_factory=list)


# --- Config Manager ---
class ConfigManager:
    """Manages loading of configuration settings for the LLM service."""

    def __init__(self, config_path: str = CONFIG_FILEPATH):
        self.config_path = Path(config_path)

    @property
    def load_config(self) -> LLMConfig:
        try:
            config= read_yaml(self.config_path)
            if not config or 'generation' not in config:
                raise ValueError("Invalid configuration: 'generation' section missing in config.yaml")
            generation_config = config.generation
            return LLMConfig(
                providers=generation_config.get('providers', [])
            )
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise


# --- LLM Service ---
class LLMService:
    """Manages requests to multiple LLM providers with fallback."""

    def __init__(self, config: LLMConfig):
        self.providers = []
        self.clients = {}
        self._initialize_clients(config.providers)

    def _initialize_clients(self, providers: List[Dict[str, str]]):
        for provider_config in providers:
            model_name = provider_config.get('model_name')
            provider = provider_config.get('provider')
            api_key = os.getenv(f"{provider.upper()}_API_KEY")

            if not api_key:
                print(f"Skipping {provider} ({model_name}) due to missing {provider.upper()}_API_KEY")
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
                    continue
                self.providers.append({"model_name": model_name, "provider": provider})
                print(f"Initialized {provider} with model: {model_name}")
            except Exception as e:
                print(f"Error initializing {provider} ({model_name}): {e}")

        if not self.providers:
            raise ValueError("No valid LLM providers configured. Check .env and config.yaml.")

    async def generate(self, model_id: str, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
        # Shuffle providers for random fallback order
        global response
        providers = self.providers.copy()
        random.shuffle(providers)

        for provider_config in providers:
            provider = provider_config['provider']
            model_name = provider_config['model_name']
            # Only use the provider if it matches the requested model_id
            if model_name != model_id:
                continue

            print(f"Trying {provider} with model {model_name}")

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
                        max_tokens=4096,
                        temperature=0.1
                    )
                    response = completion.content[0].text

                if response is None:
                    continue
                print(f"{provider} response: {response[:100]}...")
                return response

            except (GroqError, OpenAIError, AnthropicError, Exception) as e:
                print(f"Error with {provider} ({model_name}): {str(e)}")
                continue

        raise ValueError("All LLM providers failed. Check API keys and configurations.")


# --- Main Test Function ---
async def main():
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config
        llm_service = LLMService(config)
        query = "What is the capital of Kenya?"
        system_prompt = "You are a helpful assistant."

        # Determine a valid model_id from available providers.  This is critical.
        if llm_service.providers:
            model_id = llm_service.providers[0]['model_name']  # Take the first available model
        else:
            raise ValueError("No LLM providers are configured.")


        response = await llm_service.generate(model_id, system_prompt, query)  # Pass model_id
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in LLM generation: {e}")


if __name__ == "__main__":
    asyncio.run(main())