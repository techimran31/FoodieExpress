"""Run the FoodieExpress API + website.

    cd backend && python run.py
    # docs: http://127.0.0.1:8000/docs
"""
import os
import sys

try:
    import uvicorn
except ModuleNotFoundError:
    sys.exit(
        "uvicorn is not installed for this Python interpreter:\n"
        f"  {sys.executable}\n\n"
        "Install the project dependencies with:\n"
        "  python -m pip install -r requirements.txt\n"
    )

# Expose the ASGI app so `uvicorn run:app --reload` also works.
from app import app  # noqa: E402


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 FoodieExpress running at http://127.0.0.1:{port}")
    print(f"   API docs: http://127.0.0.1:{port}/docs")
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=True)
