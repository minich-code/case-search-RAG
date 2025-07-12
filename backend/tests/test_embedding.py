import asyncio
import pytest
from backend.src.config_manager.config_manager import ConfigManager
from backend.src.components.embedding import EmbeddingService
from backend.src.components.retrieval import RetrievalService, Document
from backend.src.components.reranker import RerankerService
from backend.src.components.llm import LLMService

@pytest.mark.asyncio
async def test_llm_integration():
    try:
        # Initialize ConfigManager
        config_manager = ConfigManager()
        embedding_config = config_manager.get_embedding_config()
        retrieval_config = config_manager.get_retrieval_config()
        reranker_config = config_manager.get_reranker_config()
        llm_config = config_manager.get_llm_config()
        assert embedding_config.model_name == "voyage-law-2", "Incorrect embedding model"
        assert retrieval_config.pinecone_index_name == "legal-case-search-dense", "Incorrect index name"
        assert reranker_config.model_name == "BAAI/bge-reranker-base", "Incorrect reranker model"
        assert llm_config.providers, "No LLM providers configured"

        # Initialize services
        embedder = EmbeddingService(embedding_config)
        retriever = RetrievalService(retrieval_config)
        reranker = RerankerService(reranker_config)
        llm_service = LLMService(llm_config)

        # Get a valid model_id
        model_id = llm_config.providers[0]['model_name']

        # Test embedding
        query = "What is the standard for a preliminary objection?"
        query_embedding = await embedder.embed([query], input_type="query")
        assert len(query_embedding) == 1, "Should return one embedding"
        assert len(query_embedding[0]) == 1024, "Embedding dimension should be 1024"
        print(f"Embedding test passed (dimension: {len(query_embedding[0])}).")

        # Test retrieval
        documents = await retriever.retrieve(query_embedding[0])
        assert isinstance(documents, list), "Documents should be a list"
        for doc in documents:
            assert isinstance(doc, Document), "Each result should be a Document"
        print(f"Retrieval test passed ({len(documents)} documents retrieved).")

        # Test reranking
        reranked_docs = await reranker.rerank(query, documents)
        assert len(reranked_docs) <= reranker_config.top_n, "Should return at most top_n documents"
        for doc in reranked_docs:
            assert 'rerank_score' in doc.metadata, "Document should have rerank_score"
        print(f"Reranking test passed ({len(reranked_docs)} documents returned).")

        # Test LLM generation with max_tokens
        max_tokens = 512  # Test with smaller value to ensure truncation
        response = await llm_service.generate(query, reranked_docs, model_id, max_tokens=max_tokens)
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        # Note: Exact token count depends on tokenizer; this is a rough check
        assert len(response.split()) <= max_tokens * 2, f"Response word count exceeds expected limit for {max_tokens} tokens"
        print(f"LLM generation test passed (response length: {len(response)}, max_tokens: {max_tokens}).")

    except Exception as e:
        pytest.fail(f"LLM integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(pytest.main(["-v", __file__]))