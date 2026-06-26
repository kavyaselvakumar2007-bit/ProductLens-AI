import os
import sys

try:
    from app import process_feedback
except Exception as e:
    print(f"Error importing app.py: {e}")
    sys.exit(1)

class MockFile:
    def __init__(self, name):
        self.name = name

# Test the generator
try:
    csv_file = MockFile("data/sample_feedback.csv")
    generator = process_feedback(csv_file, None, None)
    
    # We expect multiple yields. Let's consume them all.
    results = []
    for output in generator:
        results.append(output)
        
    final_output = results[-1]
    
    # The final output should have 7 elements:
    # kpi_html, fig_theme, fig_prio, theme_cards_html, pipeline_html, obs_summary, obs_json
    if len(final_output) == 7:
        print("SUCCESS: process_feedback executed and returned 7 UI elements.")
        print("Verification passed! No syntax errors and pipeline executes correctly.")
    else:
        print(f"FAILURE: Expected 7 elements, got {len(final_output)}")
        sys.exit(1)
        
except Exception as e:
    print(f"FAILURE during execution: {e}")
    sys.exit(1)
