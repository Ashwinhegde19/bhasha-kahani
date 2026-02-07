# Vercel serverless entry point
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

# Vercel serverless handler
# This file is used as the entry point for Vercel deployment

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
