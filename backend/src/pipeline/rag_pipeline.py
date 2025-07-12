import asyncio
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from backend.src.config_manager.config_manager import ConfigManager
from backend.src.components.embedding import EmbeddingService
from backend.src.components.retrieval import RetrievalService, Document
from backend.src.components.reranker import RerankerService
from backend.src.components.llm import LLMService
from backend.src.components.response import ResponseService
from backend.src.prompt_template.cot_prompt_template import CoTPromptTemplate

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='pipeline.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class EmbeddingRetrievalPipeline:
    """
    Orchestrates embedding, retrieval, reranking, LLM generation, and response formatting.
    Returns JSON-serializable output for API responses.
    """

    def __init__(self):
        """
        Initializes the pipeline with all services.

        Raises:
            ValueError: If initialization fails.
        """
        print("✅ Initializing Embedding-Retrieval-Reranking-LLM-Response Pipeline...")
        try:
            self.config_manager = ConfigManager()
            self.embedding_config = self.config_manager.get_embedding_config()
            self.retrieval_config = self.config_manager.get_retrieval_config()
            self.reranker_config = self.config_manager.get_reranker_config()
            self.llm_config = self.config_manager.get_llm_config()
            self.response_config = self.config_manager.get_response_config()
            self.embedding_service = EmbeddingService(self.embedding_config)
            self.retrieval_service = RetrievalService(self.retrieval_config)
            self.reranker_service = RerankerService(self.reranker_config)
            self.llm_service = LLMService(self.llm_config)
            self.response_service = ResponseService(self.response_config)
            self.cot_template = CoTPromptTemplate()
            self.model_id = self.llm_config.providers[0]['model_name'] if self.llm_config.providers else None
            self.max_tokens = self.config_manager.config.generation.get('max_tokens', 2048)  # Increased
            if not self.model_id:
                raise ValueError("No LLM providers configured.")
            logger.info(f"Pipeline initialized with model_id: {self.model_id}, max_tokens: {self.max_tokens}")
            print(f"✅ Pipeline initialized with model_id: {self.model_id}, max_tokens: {self.max_tokens}")
        except Exception as e:
            logger.error(f"Error initializing pipeline: {e}")
            print(f"Error initializing pipeline: {e}")
            raise ValueError(f"Pipeline initialization failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_embedding(self, query: str) -> List[float]:
        """
        Generates an embedding for the input query.

        Args:
            query (str): The query text to embed.

        Returns:
            List[float]: The query embedding vector.

        Raises:
            ValueError: If the query is invalid.
            RuntimeError: If embedding fails.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")

        print("[Step 1/5] Generating query embedding...")
        try:
            query_embedding = await self.embedding_service.embed([query], input_type="query")
            logger.info(f"Embedding generated (dimension: {len(query_embedding[0])})")
            print(f"✅ Embedding generated (dimension: {len(query_embedding[0])}).")
            return query_embedding[0]
        except Exception as e:
            logger.error(f"Error in embedding: {e}")
            print(f"Error in embedding: {e}")
            raise RuntimeError(f"Embedding failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_retrieval(self, query_embedding: List[float]) -> List[Document]:
        """
        Retrieves relevant documents using the query embedding.

        Args:
            query_embedding (List[float]): The query embedding vector.

        Returns:
            List[Document]: List of retrieved documents.

        Raises:
            ValueError: If the query embedding is invalid.
            RuntimeError: If retrieval fails.
        """
        print("[Step 2/5] Retrieving documents...")
        try:
            documents = await self.retrieval_service.retrieve(query_embedding)
            logger.info(f"Retrieved {len(documents)} documents")
            print(f"✅ Retrieved {len(documents)} documents.")
            return documents
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            print(f"Error in retrieval: {e}")
            raise RuntimeError(f"Retrieval failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_reranking(self, query: str, documents: List[Document]) -> List[Document]:
        """
        Reranks retrieved documents based on relevance to the query.

        Args:
            query (str): The original query text.
            documents (List[Document]): List of documents to rerank.

        Returns:
            List[Document]: Top-N reranked documents.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If reranking fails.
        """
        print("[Step 3/5] Reranking documents...")
        try:
            reranked_docs = await self.reranker_service.rerank(query, documents)
            logger.info(f"Reranked {len(documents)} documents, kept top {len(reranked_docs)}")
            print(f"✅ Reranked {len(documents)} documents, kept top {len(reranked_docs)}.")
            return reranked_docs
        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            print(f"Error in reranking: {e}")
            raise RuntimeError(f"Reranking failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_generation(self, query: str, documents: List[Document]) -> str:
        """
        Generates a response using the LLM with CoT prompt.

        Args:
            query (str): The original query text.
            documents (List[Document]): Reranked documents.

        Returns:
            str: The generated response.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If generation fails.
        """
        print("[Step 4/5] Generating response...")
        try:
            prompt = self.cot_template.format(query, documents)
            response = await self.llm_service.generate(prompt, documents, self.model_id, max_tokens=self.max_tokens)
            logger.debug(f"Raw LLM response: {response[:500]}...")
            print(f"✅ Generated response: {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"Error in generation: {e}")
            print(f"Error in generation: {e}")
            raise RuntimeError(f"Generation failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_response_formatting(self, query: str, llm_output: str, documents: List[Document]) -> Dict[str, Any]:
        """
        Formats the LLM output into a user-friendly response.

        Args:
            query (str): The original query text.
            llm_output (str): Raw LLM output.
            documents (List[Document]): Reranked documents.

        Returns:
            Dict[str, Any]: Formatted response with query, final_answer, and citations.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If formatting fails.
        """
        print("[Step 5/5] Formatting response...")
        try:
            formatted_response = await self.response_service.generate_response(query, llm_output, documents)
            logger.info(f"Formatted response: {formatted_response['final_answer'][:100]}...")
            print(f"✅ Response formatted: {formatted_response['final_answer'][:100]}...")
            return formatted_response
        except Exception as e:
            logger.error(f"Error in response formatting: {e}")
            print(f"Error in response formatting: {e}")
            raise RuntimeError(f"Response formatting failed: {e}")

    async def run(self, query: str) -> Dict[str, Any]:
        """
        Runs the full pipeline for a query.

        Args:
            query (str): The input query text.

        Returns:
            Dict[str, Any]: JSON-serializable result with query, embedding, documents, final_answer, and citations.

        Raises:
            ValueError: If the query is invalid.
            RuntimeError: If any pipeline step fails.
        """
        print(f"Running pipeline for query: '{query}'")
        logger.info(f"Starting pipeline for query: {query}")
        try:
            # Step 1: Embed query
            embedding = await self.run_embedding(query)

            # Step 2: Retrieve documents
            documents = await self.run_retrieval(embedding)

            # Step 3: Rerank documents
            reranked_docs = await self.run_reranking(query, documents)

            # Step 4: Generate response
            llm_output = await self.run_generation(query, reranked_docs)

            # Step 5: Format response
            formatted_response = await self.run_response_formatting(query, llm_output, reranked_docs)

            # Prepare JSON-serializable output
            result = {
                "query": formatted_response["query"],
                "embedding": embedding,
                "documents": [
                    {
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "score": doc.score
                    } for doc in reranked_docs
                ],
                "final_answer": formatted_response["final_answer"],
                "citations": formatted_response["citations"]
            }
            logger.info("Pipeline completed successfully")
            print("✅ Pipeline completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            print(f"Pipeline failed: {e}")
            raise RuntimeError(f"Pipeline failed: {e}")

async def main():
    """Example usage of the pipeline."""
    try:
        pipeline = EmbeddingRetrievalPipeline()
        query = "What is the standard for a preliminary objection?"
        result = await pipeline.run(query)
        print(
            f"Final result: query='{result['query']}', embedding_length={len(result['embedding'])}, documents={len(result['documents'])}, response_length={len(result['final_answer'])}")
        for i, doc in enumerate(result['documents'], 1):
            print(
                f"Document {i}: score={doc['score']}, rerank_score={doc['metadata'].get('rerank_score', 'N/A')}, content={doc['content'][:100]}...")
        print(f"Final Answer: {result['final_answer']}")
        print(f"Citations: {', '.join(result['citations'])}")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())