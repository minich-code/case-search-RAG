from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from typing import List, Optional
import os
from dotenv import load_dotenv
from backend.src.pipeline.rag_pipeline import EmbeddingRetrievalPipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='backend.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
API_KEY = os.getenv("API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, API_KEY]):
    raise ValueError("Missing required environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize FastAPI app
app = FastAPI(title="Legal Research API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = EmbeddingRetrievalPipeline()


class QueryRequest(BaseModel):
    query: str
    user_id: str


class QueryResponse(BaseModel):
    final_answer: str
    citations: List[str]
    error: Optional[str] = None


def verify_api_key(api_key: str = Depends(lambda x: x.headers.get("X-API-Key"))):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


async def verify_user(user_id: str):
    try:
        response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error verifying user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, api_key: str = Depends(verify_api_key)):
    """
    Processes a legal query using the RAG pipeline and stores chat history in Supabase.

    Args:
        request (QueryRequest): Query and user ID.
        api_key (str): API key for authentication.

    Returns:
        QueryResponse: Final answer, citations, and optional error.
    """
    try:
        # Verify user
        await verify_user(request.user_id)

        logger.info(f"Processing query: {request.query} for user: {request.user_id}")

        # Run pipeline
        result = await pipeline.run(request.query)

        # Extract final answer and citations
        final_answer = result.get("final_answer", "No answer generated")
        citations = result.get("citations", [])

        # Store chat history in Supabase
        chat_data = {
            "user_id": request.user_id,
            "query": request.query,
            "response": final_answer,
            "citations": citations,
            "tags": [],
            "timestamp": "now()"
        }
        supabase.table("chat_history").insert(chat_data).execute()

        logger.info(f"Query processed successfully for user: {request.user_id}")
        return QueryResponse(
            final_answer=final_answer,
            citations=citations,
            error=None
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return QueryResponse(
            final_answer="",
            citations=[],
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)