import sys
import os

# Ensure the root project folder is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.ragas.evaluator import run_ragas_evaluation

if __name__ == "__main__":
    print("Starting ParcelPilot Ragas Evaluation Suite...")
    try:
        scores_df = run_ragas_evaluation()
        print("\n=== Evaluation Summary Table ===")
        # Ragas uses 'user_input' instead of 'question' and 'answer_relevancy' instead of 'answer_relevance'
        print(scores_df[["user_input", "faithfulness", "answer_relevancy", "context_precision", "context_recall"]])
        
        mean_faithfulness = scores_df["faithfulness"].mean()
        mean_relevance = scores_df["answer_relevancy"].mean()
        
        print(f"\nMean Faithfulness: {mean_faithfulness:.2f}")
        print(f"Mean Answer Relevance: {mean_relevance:.2f}")
        
        # Threshold enforcement for CI/CD pipelines
        if mean_faithfulness < 0.75 or mean_relevance < 0.75:
            print("\nFAIL: Evaluation scores fell below quality threshold (0.75).")
            sys.exit(1)
        else:
            print("\nSUCCESS: All Ragas evaluation criteria met successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\nERROR: Evaluation execution failed: {e}")
        sys.exit(1)