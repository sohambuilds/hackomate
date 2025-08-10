#!/usr/bin/env python3
"""
Main entry point for the Hackathon Twin application.

This allows running the app with: uv run main.py
"""

import os
import sys


def main():
    """Main entry point for the application."""
    # Add the project root to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run uvicorn
    import uvicorn
    from backend.main import app
    
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )


if __name__ == "__main__":
    main()