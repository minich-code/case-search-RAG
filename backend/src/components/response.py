# import re
# import asyncio
# import logging
# from typing import List, Dict, Any
# from tenacity import retry, stop_after_attempt, wait_fixed
# from backend.src.config_params.config_params import ResponseConfig
# from backend.src.components.retrieval import Document
# from backend.src.prompt_template.cot_prompt_template import CoTPromptTemplate
#
# # Configure logging
# logging.basicConfig(level=logging.DEBUG, filename='response_service.log', format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# class ResponseService:
#     """
#     Formats LLM output into a user-friendly response with citations, hiding reasoning.
#     Logs reasoning for debugging.
#     """
#
#     def __init__(self, config: ResponseConfig):
#         """
#         Initializes the response service.
#
#         Args:
#             config (ResponseConfig): Configuration for response formatting.
#
#         Raises:
#             ValueError: If config is invalid.
#         """
#         if not isinstance(config, ResponseConfig):
#             raise ValueError("Config must be an instance of ResponseConfig.")
#         self.config = config
#         self.cot_template = CoTPromptTemplate()
#         logger.info("ResponseService initialized successfully.")
#         print("ResponseService initialized successfully.")
#
#     @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
#     async def generate_response(self, query: str, llm_output: str, documents: List[Document]) -> Dict[str, Any]:
#         """
#         Formats the LLM output into a user response with citations.
#
#         Args:
#             query (str): The input query.
#             llm_output (str): Raw LLM output.
#             documents (List[Document]): Reranked documents.
#
#         Returns:
#             Dict[str, Any]: JSON-serializable response with query, final_answer, and citations.
#
#         Raises:
#             ValueError: If inputs are invalid.
#             RuntimeError: If response generation fails.
#         """
#         if not query or not isinstance(query, str):
#             raise ValueError("Query must be a non-empty string.")
#         if not llm_output or not isinstance(llm_output, str):
#             raise ValueError("LLM output must be a non-empty string.")
#         if not documents or not all(isinstance(doc, Document) for doc in documents):
#             raise ValueError("Documents must be a non-empty list of Document objects.")
#
#         try:
#             # Parse LLM output
#             reasoning, final_answer = await self._parse_llm_output(llm_output)
#             logger.debug(f"Raw LLM output for query '{query}': {llm_output[:500]}...")
#             logger.debug(f"Parsed reasoning: {reasoning[:500]}...")
#             logger.debug(f"Parsed final_answer: {final_answer}")
#             # Extract citations
#             citations = self._extract_citations(documents, llm_output)
#             # Format user response
#             formatted_response = {
#                 "query": query,
#                 "final_answer": final_answer,
#                 "citations": citations[:self.config.max_citations]
#             }
#             logger.info(f"Response formatted for query: {query[:50]}...")
#             print(f"✅ Response formatted for query: {query[:50]}...")
#             return formatted_response
#         except Exception as e:
#             logger.error(f"Error formatting response: {e}")
#             raise RuntimeError(f"Response generation failed: {e}")
#
#     async def _parse_llm_output(self, llm_output: str) -> tuple[str, str]:
#         """
#         Parses LLM output to separate reasoning and final answer.
#
#         Args:
#             llm_output (str): Raw LLM output.
#
#         Returns:
#             tuple[str, str]: Reasoning and final answer.
#
#         Raises:
#             ValueError: If parsing fails.
#         """
#         try:
#             llm_output = llm_output.replace('\r\n', '\n').strip()
#             # Try strict parsing
#             parts = re.split(r'\n\s*Final Answer:\s*\n', llm_output, maxsplit=1)
#             if len(parts) == 2:
#                 reasoning = parts[0].strip()
#                 if reasoning.startswith("Reasoning:"):
#                     reasoning = reasoning[len("Reasoning:"):].strip()
#                 final_answer = parts[1].strip()
#             else:
#                 # Fallback: Look for any content resembling a final answer
#                 final_answer_match = re.search(r'(?:Final Answer|Answer|Conclusion):?\s*\n?(.*?)(?:\n\s*$|\n\s*[^R])', llm_output, re.DOTALL | re.IGNORECASE)
#                 reasoning_match = re.search(r'(?:Reasoning|Analysis):?\s*\n?(.*?)(?=(?:Final Answer|Answer|Conclusion):|\n\s*$)', llm_output, re.DOTALL | re.IGNORECASE)
#                 reasoning = reasoning_match.group(1).strip() if reasoning_match else llm_output.strip()
#                 final_answer = final_answer_match.group(1).strip() if final_answer_match else "No conclusive answer could be extracted from the LLM output due to formatting issues."
#                 logger.warning(f"Fallback parsing used for LLM output: {llm_output[:500]}...")
#
#             # Clean markdown
#             reasoning = re.sub(r'\*{2,}', '', reasoning).strip()
#             final_answer = re.sub(r'\*{2,}', '', final_answer).strip()
#
#             return reasoning, final_answer
#         except Exception as e:
#             logger.error(f"Failed to parse LLM output: {e}")
#             raise ValueError(f"Failed to parse LLM output: {e}")
#
#     def _extract_citations(self, documents: List[Document], llm_output: str) -> List[str]:
#         """
#         Extracts and formats citations from documents, prioritizing those mentioned in LLM output.
#
#         Args:
#             documents (List[Document]): List of documents.
#             llm_output (str): Raw LLM output for citation matching.
#
#         Returns:
#             List[str]: Formatted citations.
#         """
#         citations = []
#         seen_citations = set()
#         # First, try to find citations mentioned in LLM output
#         for doc in documents:
#             metadata = doc.metadata or {}
#             case_title = metadata.get('case_title', '')
#             media_neutral = metadata.get('media_neutral_citation', '')
#             if case_title and media_neutral and media_neutral not in seen_citations:
#                 citation = f"{case_title} {media_neutral}"
#                 if citation in llm_output or case_title in llm_output:
#                     citations.append(citation)
#                     seen_citations.add(media_neutral)
#         # Fallback: Include all document citations if none found in LLM output
#         if not citations:
#             for doc in documents:
#                 metadata = doc.metadata or {}
#                 case_title = metadata.get('case_title', '')
#                 media_neutral = metadata.get('media_neutral_citation', '')
#                 if case_title and media_neutral and media_neutral not in seen_citations:
#                     citation = f"{case_title} {media_neutral}"
#                     citations.append(citation)
#                     seen_citations.add(media_neutral)
#         logger.debug(f"Extracted citations: {citations}")
#         return citations

# response.py
import re
import asyncio
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed
from backend.src.config_params.config_params import ResponseConfig
from backend.src.components.retrieval import Document
from backend.src.prompt_template.cot_prompt_template import CoTPromptTemplate

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='response_service.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResponseService:
    """
    Formats LLM output into a user-friendly response with citations, hiding reasoning.
    Logs reasoning for debugging.
    """

    def __init__(self, config: ResponseConfig):
        """
        Initializes the response service.

        Args:
            config (ResponseConfig): Configuration for response formatting.

        Raises:
            ValueError: If config is invalid.
        """
        if not isinstance(config, ResponseConfig):
            raise ValueError("Config must be an instance of ResponseConfig.")
        self.config = config
        self.cot_template = CoTPromptTemplate()
        logger.info("ResponseService initialized successfully.")
        print("ResponseService initialized successfully.")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def generate_response(self, query: str, llm_output: str, documents: List[Document]) -> Dict[str, Any]:
        """
        Formats the LLM output into a user response with citations.

        Args:
            query (str): The input query.
            llm_output (str): Raw LLM output.
            documents (List[Document]): Reranked documents.

        Returns:
            Dict[str, Any]: JSON-serializable response with query, final_answer, and citations.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If response generation fails.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        if not llm_output or not isinstance(llm_output, str):
            raise ValueError("LLM output must be a non-empty string.")
        if not documents or not all(isinstance(doc, Document) for doc in documents):
            raise ValueError("Documents must be a non-empty list of Document objects.")

        try:
            # Parse LLM output
            reasoning, final_answer = await self._parse_llm_output(llm_output)
            logger.debug(f"Raw LLM output for query '{query}': {llm_output[:500]}...")
            logger.debug(f"Parsed reasoning: {reasoning[:500]}...")
            logger.debug(f"Parsed final_answer: {final_answer}")
            # Extract citations
            citations = self._extract_citations(documents, llm_output)
            # Format user response
            formatted_response = {
                "query": query,
                "final_answer": final_answer,
                "citations": citations[:self.config.max_citations]
            }
            logger.info(f"Response formatted for query: {query[:50]}...")
            print(f"✅ Response formatted for query: {query[:50]}...")
            return formatted_response
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            raise RuntimeError(f"Response generation failed: {e}")

    async def _parse_llm_output(self, llm_output: str) -> tuple[str, str]:
        """
        Parses LLM output to separate reasoning and final answer.

        Args:
            llm_output (str): Raw LLM output.

        Returns:
            tuple[str, str]: Reasoning and final answer.

        Raises:
            ValueError: If parsing fails.
        """
        try:
            llm_output = llm_output.replace('\r\n', '\n').strip()
            # Try strict parsing
            parts = re.split(r'\n\s*Final Answer:\s*\n', llm_output, maxsplit=1)
            if len(parts) == 2:
                reasoning = parts[0].strip()
                if reasoning.startswith("Reasoning:"):
                    reasoning = reasoning[len("Reasoning:"):].strip()
                final_answer = parts[1].strip()
            else:
                # Fallback: Look for any content resembling a final answer
                final_answer_match = re.search(r'(?:Final Answer|Answer|Conclusion):?\s*\n?(.*?)(?:\n\s*$|\n\s*[^R])', llm_output, re.DOTALL | re.IGNORECASE)
                reasoning_match = re.search(r'(?:Reasoning|Analysis):?\s*\n?(.*?)(?=(?:Final Answer|Answer|Conclusion):|\n\s*$)', llm_output, re.DOTALL | re.IGNORECASE)
                reasoning = reasoning_match.group(1).strip() if reasoning_match else llm_output.strip()
                final_answer = final_answer_match.group(1).strip() if final_answer_match else "No conclusive answer could be extracted from the LLM output due to formatting issues."
                logger.warning(f"Fallback parsing used for LLM output: {llm_output[:500]}...")

            # Clean markdown
            reasoning = re.sub(r'\*{2,}', '', reasoning).strip()
            final_answer = re.sub(r'\*{2,}', '', final_answer).strip()

            return reasoning, final_answer
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {e}")
            raise ValueError(f"Failed to parse LLM output: {e}")

    def _extract_citations(self, documents: List[Document], llm_output: str) -> List[str]:
        """
        Extracts and formats citations from documents, prioritizing those mentioned in LLM output.

        Args:
            documents (List[Document]): List of documents.
            llm_output (str): Raw LLM output for citation matching.

        Returns:
            List[str]: Formatted citations.
        """
        citations = []
        seen_citations = set()
        # First, try to find citations mentioned in LLM output
        for doc in documents:
            metadata = doc.metadata or {}
            case_title = metadata.get('case_title', '')
            media_neutral = metadata.get('media_neutral_citation', '')
            if case_title and media_neutral and media_neutral not in seen_citations:
                citation = f"{case_title} {media_neutral}"
                if citation in llm_output or case_title in llm_output:
                    citations.append(citation)
                    seen_citations.add(media_neutral)
        # Fallback: Include all document citations if none found in LLM output
        if not citations:
            for doc in documents:
                metadata = doc.metadata or {}
                case_title = metadata.get('case_title', '')
                media_neutral = metadata.get('media_neutral_citation', '')
                if case_title and media_neutral and media_neutral not in seen_citations:
                    citation = f"{case_title} {media_neutral}"
                    citations.append(citation)
                    seen_citations.add(media_neutral)
        logger.debug(f"Extracted citations: {citations}")
        return citations
