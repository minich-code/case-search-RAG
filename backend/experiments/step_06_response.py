import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from box import ConfigBox
from backend.src.utils.common import read_yaml
from backend.src.constants import CONFIG_FILEPATH
from backend.src.prompt_template.cot_prompt_template import CoTPromptTemplate

# Load .env file
load_dotenv(dotenv_path=Path("backend/.env"))


# --- Response Config ---
@dataclass
class ResponseConfig:
    """Holds configuration for the response service."""
    cot_template: CoTPromptTemplate = field(default_factory=CoTPromptTemplate)


# --- Config Manager ---
class ConfigManager:
    """Manages loading and validation of configuration settings for the response service."""

    def __init__(self, config_path: str = CONFIG_FILEPATH):
        self.config_path = Path(config_path)

    def load_config(self) -> ResponseConfig:
        """Loads response configuration."""
        try:
            config_data = read_yaml(self.config_path)
            if not config_data:
                raise ValueError("Invalid configuration: config.yaml is empty")
            return ResponseConfig()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise


# --- Response Service ---
class ResponseService:
    """Formats LLM output with CoT reasoning and citations for the end user."""

    def __init__(self, config: ResponseConfig):
        self.config = config
        self.cot_template = config.cot_template
        print("ResponseService initialized with CoT prompt template.")

    async def format_response(self, query: str, llm_output: str, context_packets: Dict[str, List[Dict]]) -> Dict[
        str, Any]:
        """Formats the LLM output into a structured response with reasoning, answer, and citations."""
        try:
            # Parse LLM output into Reasoning and Final Answer
            reasoning, final_answer = self._parse_llm_output(llm_output)

            # Extract citations from context packets
            citations = self._extract_citations(context_packets)

            # Format the response
            formatted_response = {
                "query": query,
                "reasoning": reasoning,
                "final_answer": final_answer,
                "citations": citations
            }
            print("Response formatted successfully.")
            return formatted_response
        except Exception as e:
            print(f"Error formatting response: {e}")
            raise

    def _parse_llm_output(self, llm_output: str) -> tuple[str, str]:
        """Parses LLM output into Reasoning and Final Answer sections."""
        try:
            # Split based on headers
            parts = llm_output.split("Final Answer:")
            if len(parts) != 2:
                raise ValueError("LLM output missing 'Final Answer' section")
            reasoning = parts[0].replace("Reasoning:", "").strip()
            final_answer = parts[1].strip()
            return reasoning, final_answer
        except Exception as e:
            print(f"Error parsing LLM output: {e}")
            raise

    def _extract_citations(self, context_packets: Dict[str, List[Dict]]) -> List[str]:
        """Extracts concise citations from context packets."""
        citations = []
        for case_citation, chunks in context_packets.items():
            for chunk in chunks:
                citation = chunk.get('media_neutral_citation', case_citation)
                if citation and citation not in citations:
                    citations.append(citation)
        return citations


# --- Main Test Function ---
async def main():
    """Test the ResponseService with mock data."""
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()

        response_service = ResponseService(config)

        # Mock data
        query = "What is the standard for a preliminary objection?"
        mock_context_packets = {
            "[2025] KEHC 4273 (KLR)": [
                {
                    "text": "A preliminary objection must be based on a pure point of law...",
                    "chunk_sequence": 1,
                    "media_neutral_citation": "[2025] KEHC 4273 (KLR)",
                    "case_title": "Gheewala v Gheewala & another"
                }
            ],
            "[2024] KEHC 1234 (KLR)": [
                {
                    "text": "The court dismissed the objection as it involved factual disputes...",
                    "chunk_sequence": 1,
                    "media_neutral_citation": "[2024] KEHC 1234 (KLR)",
                    "case_title": "Another Case"
                }
            ]
        }
        mock_llm_output = """
Reasoning:
1. The query asks for the standard for a preliminary objection.
2. From [2025] KEHC 4273 (KLR), a preliminary objection must be based on a pure point of law.
3. From [2024] KEHC 1234 (KLR), objections involving factual disputes are not valid.

Final Answer:
A preliminary objection must be based on a pure point of law, without involving factual disputes, as established in [2025] KEHC 4273 (KLR) and [2024] KEHC 1234 (KLR).
"""

        result = await response_service.format_response(query, mock_llm_output, mock_context_packets)

        print("\n=== Response Output ===")
        print(f"Query: {result['query']}")
        print(f"Reasoning:\n{result['reasoning']}")
        print(f"Final Answer:\n{result['final_answer']}")
        print(f"Citations: {', '.join(result['citations'])}")
    except Exception as e:
        print(f"Error in response generation: {e}")


# --- Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())