import asyncio
import pytest
from backend.src.pipeline.rag_pipeline import RAGPipeline, Document


@pytest.mark.asyncio
async def test_rag_pipeline_embedding():
    try:
        pipeline = RAGPipeline()
        query = "What is the standard for a preliminary objection?"

        # Test embedding step
        embedding = await pipeline.run_embedding(query)
        assert isinstance(embedding, list)
        assert len(embedding) == 1024  # voyage-law-2 dimension
        print(f"Embedding test passed (dimension: {len(embedding)}).")

        # Test full pipeline (expect placeholders for other steps)
        result = await pipeline.run(query)
        assert isinstance(result, dict)
        assert result["query"] == query
        assert result["response"] == "Placeholder response"
        assert isinstance(result["documents"], list)
        print("Full pipeline test passed (with placeholders).")

    except Exception as e:
        pytest.fail(f"Pipeline test failed: {e}")


if __name__ == "__main__":
    asyncio.run(pytest.main(["-v", __file__]))