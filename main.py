import uvicorn
import os
import sys

# Ensure src is in path for imports
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("Starting Simple SP (Sentence Prediction)...")
    print("Loading data from ./data/")
    print("Interface available at http://127.0.0.1:8000")
    
    # Run the API server
    # We use the string import to allow for auto-reload if the user wants to enable it later
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["src", "data"])
