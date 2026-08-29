import json
import os
from datasets import Dataset

from ragas import EvaluationDataset
# or depending on your ragas version:

def load_evaluation_dataset(json_path: str = "evaluation/datasets/rag_questions.json") -> Dataset:
    """Loads and formats evaluation questions from JSON into a HuggingFace Dataset."""
    if not os.path.exists(json_path):
        # Fallback inline dataset if JSON file is missing
        data = {
            "question": ["What is the SLA policy for premium enterprise accounts regarding delayed shipments?"],
            "answer": ["For premium enterprise accounts, delayed shipments must be acknowledged within 2 hours and resolved or escalated within 4 hours."],
            "contexts": [["Enterprise SLA Addendum v2.1: Premium accounts require a 2-hour acknowledgement window."]],
            "ground_truth": ["Premium enterprise accounts have a 2-hour acknowledgement and 4-hour resolution SLA for delayed shipments."]
        }
        return Dataset.from_dict(data)
    
    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    formatted = {
        "question": [item["question"] for item in raw_data],
        "answer": [item["answer"] for item in raw_data],
        "contexts": [item["contexts"] for item in raw_data],
        "ground_truth": [item["ground_truth"] for item in raw_data],
    }
    return Dataset.from_dict(formatted)