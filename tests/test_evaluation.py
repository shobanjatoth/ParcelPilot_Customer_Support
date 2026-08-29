import json
import os
from evaluation.ragas.dataset import load_evaluation_dataset
from evaluation.ragas.evaluator import run_ragas_evaluation

def test_ragas_pipeline():
    # 1. Verify dataset file exists and loads properly
    dataset_path = os.path.join("evaluation", "datasets", "rag_questions.json")
    assert os.path.exists(dataset_path), f"Dataset not found at {dataset_path}"
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items from {dataset_path}")
    assert len(data) > 0, "Dataset is empty."

    # 2. Run a smoke test evaluation
    print("Running evaluation smoke test with Groq...")
    try:
        results = run_ragas_evaluation()
        print("Evaluation completed successfully!")
        print("Results:\n", results)
    except Exception as e:
        raise AssertionError(f"Evaluation failed with error: {e}")

if __name__ == "__main__":
    test_ragas_pipeline()