import os
import uuid
import json
from main_agent import run_pipeline

def main():
    print("=== ProductLens AI Demo ===")
    
    csv_path = "data/sample_feedback.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return
        
    session_id = str(uuid.uuid4())
    print(f"Starting run with Session ID: {session_id}")
    
    # Run the pipeline
    # The pipeline ingester handles filepath if passed as data
    print("Running pipeline...")
    result = run_pipeline(source_type="csv", data=csv_path, session_id=session_id)
    
    print("\n" + "="*50 + "\n")
    print(result["report_md"])
    print("\n" + "="*50 + "\n")
    
    print("Run Summary:")
    print(json.dumps(result["run_summary"], indent=2))
    
    print("\nDone!")

if __name__ == "__main__":
    main()
