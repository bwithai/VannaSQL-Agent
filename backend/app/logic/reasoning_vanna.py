#!/usr/bin/env python3
"""
Enhanced Vanna configuration for Phi4-reasoning model
Leverages chain-of-thought capabilities for better SQL generation
"""

import os
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class ReasoningVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)
        
        # Set reasoning-optimized system prompt
        self.system_message = """You are an expert SQL assistant with advanced reasoning capabilities. 
        
Your role involves thoroughly exploring SQL questions through systematic thinking before providing precise solutions.

Please structure your response into two main sections:
1. <think> {Your reasoning process} </think> - Detail your step-by-step analysis
2. {Final SQL solution} - Provide the final SQL query

In the thinking section:
- Analyze the question and identify key requirements
- Consider table relationships and data structure  
- Plan the query approach step by step
- Verify the logic before generating the final SQL

Generate only valid, executable SQL without explanations outside the thinking section."""

    def generate_sql(self, question: str, **kwargs) -> str:
        """Enhanced SQL generation with reasoning"""
        # Add reasoning instruction to the prompt
        enhanced_question = f"""
{self.system_message}

Database Question: {question}

Please think through this step-by-step before generating the SQL query.
"""
        
        # Configure parameters for reasoning
        reasoning_config = {
            'temperature': 0.1,  # Lower temperature for more focused reasoning
            'top_p': 0.95,
            'num_predict': 4096,  # Allow longer responses for reasoning
            **kwargs
        }
        
        return super().generate_sql(enhanced_question, **reasoning_config)

def main():
    """Interactive reasoning-enhanced Vanna session"""
    # RAG-Layer directory path
    rag_layer_dir = "RAG-Layer"
    
    # Check if RAG-Layer directory exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   Run 'python hello.py' to train your model first.")
        return
    
    # Initialize reasoning-enhanced Vanna
    vn = ReasoningVanna(config={
        'model': 'phi4-mini:latest',
        'path': rag_layer_dir,  # Use RAG-Layer directory
        # Reasoning-optimized Ollama settings
        'base_url': 'http://localhost:11434'  # Ollama default
    })
    
    try:
        # Connect to database
        vn.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
        print("✅ Connected to MySQL database")
        
        # Check training data
        training_data = vn.get_training_data()
        if training_data.empty:
            print("❌ No training data found. Please run hello.py first to train the model.")
            return
        
        print(f"📊 Found {len(training_data)} training items in RAG-Layer")
        print(f"📁 Using RAG-Layer directory: {os.path.abspath(rag_layer_dir)}")
        print("\n🧠 Reasoning-Enhanced Vanna SQL Agent is ready!")
        print("This version uses chain-of-thought reasoning for better SQL generation.")
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
                
                print(f"\n🤔 Reasoning about: {question}")
                
                # Generate and execute SQL with reasoning
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
    print("\n📖 Example questions for reasoning-enhanced mode:")
    print("- 'Show me the complete organizational hierarchy with active users'")
    print("- 'Find all users and their financial data summary'")
    print("- 'What are the top 5 formations by expense amount?'")
    print("- 'Show me asset allocation across different corps'")
    print("- 'Find all users who have made transfers this month'")
    print("- 'Display liability trends by formation type'")
    print("\n💡 The reasoning mode will show step-by-step thinking before generating SQL.")
    print()

if __name__ == "__main__":
    main() 