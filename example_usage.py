#!/usr/bin/env python3
"""
Example usage script for the trained Vanna model.
Run this after training your model with hello.py
"""

import os
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

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
    
    # Initialize with the same config as training (using RAG-Layer directory)
    vn = MyVanna(config={
        'model': 'phi4-mini:latest',  # Use same model as in hello.py
        'path': rag_layer_dir  # Use RAG-Layer directory
    })
    
    try:
        # Connect to the same database
        vn.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
        print("✅ Connected to database")
        
        # Check if we have training data
        training_data = vn.get_training_data()
        if training_data.empty:
            print("❌ No training data found. Please run hello.py first to train the model.")
            return
        
        print(f"📊 Found {len(training_data)} training items in RAG-Layer")
        print(f"📁 Using RAG-Layer directory: {os.path.abspath(rag_layer_dir)}")
        print("\n🤖 Vanna SQL Agent is ready!")
        print("Ask me questions about your database in natural language.")
        print("Type 'quit' to exit, 'help' for examples.\n")
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                    
                if question.lower() == 'help':
                    print_help()
                    continue
                    
                if not question:
                    continue
                
                print(f"\n🤔 Thinking about: {question}")
                
                # Generate and execute SQL
                result = vn.ask(question)
                if result is not None:
                    print(f"✅ Result:\n{result}\n")
                else:
                    print("❌ Query failed to execute\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def print_help():
    print("\n📖 Example questions you can ask:")
    print("- 'Show me all tables in the database'")
    print("- 'How many records are in each table?'")
    print("- 'What columns does the users table have?'")
    print("- 'Find all users created today'")
    print("- 'Show me the database schema'")
    print("- 'What is the total count of records across all tables?'")
    print()

if __name__ == "__main__":
    main() 