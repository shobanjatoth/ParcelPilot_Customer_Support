import os
import pandas as pd
from ragas import evaluate
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from evaluation.ragas.dataset import load_evaluation_dataset
from evaluation.ragas.metrics import get_evaluation_metrics
from app.config import get_settings

def run_ragas_evaluation() -> pd.DataFrame:
    """
    Runs the Ragas evaluation suite utilizing Gemini as the LLM judge 
    via its OpenAI-compatible interface.
    """
    settings = get_settings()
    
    # Enforce Gemini credentials for the Ragas judge
    gemini_api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing or empty!")

    # Configure ChatOpenAI to point directly to Google's Gemini OpenAI-compatible endpoint
    eval_llm = ChatOpenAI(
        model=settings.llm_model,  # Uses "gemini-3.6-flash" from settings
        temperature=0.0,
        max_tokens=2048,
        base_url=settings.gemini_base_url,  # https://generativelanguage.googleapis.com/v1beta/openai
        api_key=gemini_api_key,
    )

    # Local sentence-transformers embeddings for Ragas context evaluation
    eval_embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    dataset = load_evaluation_dataset()
    metrics = get_evaluation_metrics()

    print(f"Executing Ragas evaluation with Gemini Judge ({settings.llm_model})...")

    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=eval_llm,
        embeddings=eval_embeddings,
    )

    return results.to_pandas()