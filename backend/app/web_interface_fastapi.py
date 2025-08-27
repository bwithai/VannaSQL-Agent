#!/usr/bin/env python3
"""
FastAPI web interface for VannaSQL-Agent with async support.
Run this after training your model with train.py
"""

import os

from app.core.config import settings
from app.vana_agent import vn
from app.vanna.fastapi import VannaFastAPIApp


def main():
    """Main function to start the FastAPI VannaSQL interface."""
    # Use RAG-Layer directory from settings
    rag_layer_dir = settings.RAG_LAYER_DIR
    
    # Check if RAG-Layer directory exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   Run 'python train.py' to train your model first.")
        return

    try:
        # Connect to MySQL database using settings
        print("🔌 Connecting to MySQL database...")
        vn.connect_to_mysql(
            host=settings.MYSQL_SERVER,
            dbname=settings.MYSQL_DB,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            port=settings.MYSQL_PORT
        )
        print("✅ Connected to MySQL database")
        
        # Check if we have training data
        training_data = vn.get_training_data()
        if training_data.empty:
            print("❌ No training data found. Please run train.py first to train the model.")
            return
        
        print(f"📊 Found {len(training_data)} training items in RAG-Layer")
        print(f"📁 Using RAG-Layer directory: {os.path.abspath(rag_layer_dir)}")
        
        # Create FastAPI app with async support
        app = VannaFastAPIApp(vn, allow_llm_to_see_data=True, function_generation=False)
        
        print("🌐 Starting VannaSQL-Agent FastAPI Web Interface...")
        print("📱 Open your browser and go to: http://localhost:8000")
        print("📋 API documentation available at: http://localhost:8000/docs")
        print("🔍 Interactive API explorer at: http://localhost:8000/redoc")
        
        # Run the FastAPI app
        app.run(host='0.0.0.0', port=8000, reload=False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
