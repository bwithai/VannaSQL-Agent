#!/usr/bin/env python3
"""
Web interface for the Vanna SQL Agent using the built-in Flask app.
Run this after training your model with hello.py
"""

from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

def main():
    print("🚀 Starting Vanna SQL Agent Web Interface...")
    
    # Initialize with the same config as training
    vn = MyVanna(config={'model': 'phi4-mini:latest'})  # Use same model as in hello.py
    
    try:
        # Connect to the same database
        vn.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
        print("✅ Connected to database")
        
        # Check if we have training data
        training_data = vn.get_training_data()
        if training_data.empty:
            print("❌ No training data found. Please run hello.py first to train the model.")
            return
        
        print(f"📊 Found {len(training_data)} training items")
        print("🌐 Starting web interface...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Create and run the Flask app
        app = VannaFlaskApp(vn)
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 