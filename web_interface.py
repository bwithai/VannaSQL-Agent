#!/usr/bin/env python3
"""
Web interface for VannaSQL-Agent using Flask.
Run this after training your model with hello.py
"""

import os
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

def main():
    # RAG-Layer directory path
    rag_layer_dir = "RAG-Layer"
    
    # Check if RAG-Layer directory exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   Run 'python hello.py' to train your model first.")
        return
    
    # Initialize Vanna with RAG-Layer directory
    vn = MyVanna(config={
        'model': 'phi4-mini:latest',
        'path': rag_layer_dir  # Use RAG-Layer directory
    })

    try:
        # Connect to MySQL database
        vn.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
        print("✅ Connected to MySQL database")
        
        # Check if we have training data
        training_data = vn.get_training_data()
        if training_data.empty:
            print("❌ No training data found. Please run hello.py first to train the model.")
            return
        
        print(f"📊 Found {len(training_data)} training items in RAG-Layer")
        print(f"📁 Using RAG-Layer directory: {os.path.abspath(rag_layer_dir)}")
        
        # Create Flask app
        app = VannaFlaskApp(vn)
        
        print("🌐 Starting VannaSQL-Agent Web Interface...")
        print("📱 Open your browser and go to: http://localhost:5000")
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 