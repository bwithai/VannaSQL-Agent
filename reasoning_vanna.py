#!/usr/bin/env python3
"""
Enhanced Vanna configuration for Phi4-reasoning model
Leverages chain-of-thought capabilities for better SQL generation
"""

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

    def ask(self, question: str, **kwargs):
        """Override ask method to enable reasoning mode"""
        # Enable thinking mode if available in Ollama
        if hasattr(self, 'client') and hasattr(self.client, 'chat'):
            kwargs['think'] = True  # Enable Ollama thinking mode
        
        return super().ask(question, **kwargs)

def main():
    # Initialize reasoning-enhanced Vanna
    vn = ReasoningVanna(config={
        'model': 'phi4-mini:latest',
        'base_url': 'http://localhost:11434'  # Ollama default
    })
    
    # Connect to database
    vn.connect_to_mysql(
        host='localhost', 
        dbname='cfms', 
        user='newuser', 
        password='newpassword', 
        port=3306
    )
    
    print("🧠 Reasoning-Enhanced Vanna initialized with Phi4")
    print("Ask complex questions to see step-by-step reasoning!\n")
    
    # Example usage
    try:
        result = vn.ask("Get all active users with their complete organizational hierarchy, showing the reasoning process")
        print("🤖 Reasoning SQL Generation:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 