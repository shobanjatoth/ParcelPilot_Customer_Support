from ragas.metrics import (
    faithfulness,
    answer_relevancy,  # Changed from answer_relevance to answer_relevancy
    context_precision,
    context_recall,
)

def get_evaluation_metrics():
    """Returns core Ragas metrics for ParcelPilot RAG validation."""
    return [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]