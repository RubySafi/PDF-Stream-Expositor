import os
from src.extractor import extractor
from src.stepper import stepper
from src.remover import do_remover

def main():
    # --- Configuration ---
    # By default, this is set to the generated sample.
    # Change these values to analyze your own PDF files.
    TARGET_PDF = "sample/target.pdf"  # Path to the PDF for analysis
    PAGE_NUM = 0                      # Target page number (0-indexed)
    
    # Check if the sample file exists
    if not os.path.exists(TARGET_PDF):
        print(f"Error: {TARGET_PDF} not found.")
        print("Please run 'python sample/create_sample.py' first.")
        return

    # --- 1. Extract (Step 1) ---
    print("\n[Step 1] Extracting streams...")
    extractor(TARGET_PDF)

    # --- 2. Stepping (Step 2: Find the culprit line) ---
    print("\n[Step 2] Generating incremental snapshots...")
    # Adjust step values for your specific analysis
    stepper(TARGET_PDF, target_page=PAGE_NUM, step=10)

    # --- 3. Remove (Step 3: Reveal the truth) ---
    print("\n[Step 3] Removing operators...")
    # Change start_line/end_line based on findings from Step 2
    # For the default sample, let's assume we've identified the line.
    do_remover(TARGET_PDF, target_page=PAGE_NUM)

    print("\nAnalysis complete. Check the output files.")

if __name__ == "__main__":
    if not os.path.exists("sample"):
        os.makedirs("sample")
    main()