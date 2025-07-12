# filename: backend/experiments/step_05_rag_pipeline.py

import asyncio
import os
import sys
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List

# --- 1. Robust Path Setup ---
# This is the most critical fix. It ensures that no matter where this script
# is run from, it can find other modules and the config file.
try:
    # Get the absolute path of the current script
    script_path = Path(__file__).resolve()
    # Navigate up to the project root (e.g., 'case-search-RAG/')
    project_root = script_path.parent.parent.parent
    # Add the project root to Python's path
    sys.path.append(str(project_root))
    print(f"INFO: Project root set to: {project_root}")
except NameError:
    # Handle cases where __file__ is not defined (e.g., interactive notebooks)
    project_root = Path('.').resolve()
    print(f"WARNING: __file__ not defined. Assuming project root is current directory: {project_root}")

# --- 2. Corrected Imports (Now that the path is set) ---
from backend.experiments.step_02_retrieval import LegalRetriever
from backend.experiments.step_01_embedding import EmbeddingService, EmbeddingConfig
from backend.experiments.step_03_reranker import RerankerService, RerankerConfig
from backend.experiments.step_04_llms import LLMManager, GenerationConfig
from backend.src.prompt_template.cot_prompt_template import CoTPromptTemplate


# --- 3. Unified Configuration System ---
@dataclass
class AppConfig:
    """A single dataclass to hold all application configurations."""
    embedding_config: EmbeddingConfig
    reranker_config: RerankerConfig
    generation_config: GenerationConfig
    pinecone_index_name: str
    retrieval_top_k: int
    system_prompt: str


def load_app_config(config_path: Path) -> AppConfig:
    """Loads all configurations from a YAML file and environment variables."""
    print(f"INFO: Loading configuration from '{config_path}'")
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at the specified path: {config_path}")

    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)

    return AppConfig(
        embedding_config=EmbeddingConfig(api_key=os.getenv("VOYAGE_API_KEY"),
                                         model_name=cfg['embedding']['model_name']),
        reranker_config=RerankerConfig(model_name=cfg['reranker']['model_name'], top_n=cfg['reranker']['top_n']),
        generation_config=GenerationConfig(config_data=cfg['generation']),
        pinecone_index_name=cfg['pinecone']['index_name'],
        retrieval_top_k=cfg['retrieval']['top_k_candidates'],
        system_prompt=cfg['prompt']['system_prompt']  # Correctly loading the system prompt
    )


def parse_llm_output(llm_response: str) -> Dict[str, str]:
    """Splits the LLM's raw output into 'Reasoning' and 'Final Answer' parts."""
    reasoning_part, answer_part = "", llm_response.strip()
    if "Final Answer:" in llm_response:
        parts = llm_response.split("Final Answer:", 1)
        reasoning_part = parts[0].replace("Reasoning:", "").strip()
        answer_part = parts[1].strip()
    return {"reasoning": reasoning_part, "answer": answer_part}


# --- 4. The RAG Pipeline Orchestrator Class ---
class RAGPipeline:
    def __init__(self, config_path: Path):
        print("INFO: Initializing RAG Pipeline...")
        self.config = load_app_config(config_path)
        self.embedding_service = EmbeddingService(self.config.embedding_config)
        self.reranker_service = RerankerService(self.config.reranker_config.model_name)
        self.retriever = LegalRetriever(self.config, self.embedding_service, self.reranker_service)
        self.llm_manager = LLMManager(self.config.generation_config)
        self.prompt_template = CoTPromptTemplate()
        print("--- Legal RAG System Initialized Successfully ---")

    async def run(self, user_query: str, selected_llm: str) -> Dict[str, any]:
        """Executes the full RAG pipeline for a given query."""
        print(f"\nUser Query: {user_query}")
        print(f"Selected LLM: {selected_llm}")

        # Step A: Retrieve, Rerank, and Stitch Context
        context_packets = await self.retriever.retrieve_context_packets(user_query)
        if not context_packets:
            print("WARNING: Could not retrieve any relevant context.")
            return {"answer": "I could not find any relevant information to answer your question.",
                    "reasoning": "No context was found after the retrieval and reranking steps.", "context": {}}

        # Step B: Format the final user prompt using the CoT template
        user_prompt_with_context = self.prompt_template.format(query=user_query, context_packets=context_packets)

        # Step C: Generate the final response from the chosen LLM
        print("\n--- Generating final answer... ---")
        llm_raw_output = await self.llm_manager.generate(
            model_id=selected_llm,
            system_prompt=self.config.system_prompt,
            user_prompt=user_prompt_with_context
        )

        # Step D: Parse the structured output
        final_result = parse_llm_output(llm_raw_output)
        final_result['context'] = context_packets  # Include the context for inspection

        return final_result


# --- 5. Main Execution Block ---
async def main():
    try:
        # Define the config path using the robust project_root variable
        config_path = project_root / "backend" / "config" / "config.yaml"

        # Initialize the entire pipeline from one class
        pipeline = RAGPipeline(config_path)

        # Define user input
        user_query = "What is the exception to the rule in Foss v Harbottle?"
        selected_llm = "llama3-8b-groq"

        # Run the pipeline
        result = await pipeline.run(user_query, selected_llm)

        # Display the final, parsed results
        print("\n\n" + "=" * 50)
        print("          FINAL RESPONSE          ")
        print("=" * 50)
        print("\n>>> Final Answer:\n")
        print(result['answer'])
        print("\n\n>>> LLM's Reasoning (Chain of Thought):\n")
        print(result['reasoning'])
        print("\n" + "=" * 50)

    except FileNotFoundError as e:
        print(
            f"\nFATAL CONFIGURATION ERROR: Could not find a required file. Please check your file paths.\nDetails: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred in the RAG pipeline: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=project_root / '.env')  # Load .env from the project root
    asyncio.run(main())