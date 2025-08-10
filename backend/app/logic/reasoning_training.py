#!/usr/bin/env python3
"""
Advanced training script leveraging Phi4-reasoning capabilities
Uses chain-of-thought to generate comprehensive training data
"""

import os
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class ReasoningTrainer(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

    def train_with_reasoning(self, question: str, expected_sql: str):
        """Train with reasoning explanation"""
        reasoning_prompt = f"""
        Analyze this SQL query and explain the reasoning behind it:
        
        Question: {question}
        SQL: {expected_sql}
        
        <think>
        Explain step-by-step:
        1. What the question is asking for
        2. Which tables are involved and why
        3. What joins are needed and why
        4. What filters/conditions are applied
        5. How the result is structured
        </think>
        
        Provide a clear explanation of this SQL solution.
        """
        
        # Generate reasoning explanation
        explanation = self.generate_sql(reasoning_prompt)
        
        # Train with both SQL and reasoning
        self.train(sql=expected_sql)
        self.train(documentation=f"Question: {question}\nReasoning: {explanation}")
        
        print(f"✅ Trained with reasoning for: {question[:50]}...")

    def generate_advanced_training_data(self):
        """Generate reasoning-enhanced training data"""
        print("🧠 Generating advanced reasoning-based training data...")
        
        # Complex organizational hierarchy queries with reasoning
        complex_queries = [
            {
                "question": "Show me all active users with their complete organizational hierarchy",
                "sql": """SELECT 
                    usr.username,
                    usr.name as user_name,
                    usr.role,
                    c.name as corps_name,
                    d.name as division_name,
                    b.name as brigade_name,
                    u.name as unit_name
                FROM users usr
                LEFT JOIN corps c ON usr.corp_id = c.id
                LEFT JOIN divs d ON usr.div_id = d.id
                LEFT JOIN brigades b ON usr.brigade_id = b.id
                LEFT JOIN units u ON usr.unit_id = u.id
                WHERE usr.is_active = 1
                ORDER BY c.name, d.name, b.name, u.name"""
            },
            {
                "question": "Find users count by each organizational level",
                "sql": """SELECT 
                    c.name as corps_name,
                    d.name as division_name,
                    b.name as brigade_name,
                    u.name as unit_name,
                    COUNT(usr.id) as user_count
                FROM users usr
                LEFT JOIN corps c ON usr.corp_id = c.id
                LEFT JOIN divs d ON usr.div_id = d.id
                LEFT JOIN brigades b ON usr.brigade_id = b.id
                LEFT JOIN units u ON usr.unit_id = u.id
                WHERE usr.is_active = 1
                GROUP BY c.id, d.id, b.id, u.id
                ORDER BY user_count DESC"""
            }
        ]
        
        for query_data in complex_queries:
            self.train_with_reasoning(query_data["question"], query_data["sql"])

def main():
    # RAG-Layer directory setup
    rag_layer_dir = "RAG-Layer"
    if not os.path.exists(rag_layer_dir):
        os.makedirs(rag_layer_dir)
        print(f"📁 Created directory: {rag_layer_dir}")

    # Initialize reasoning trainer with RAG-Layer directory
    trainer = ReasoningTrainer(config={
        'model': 'phi4-mini:latest',
        'path': rag_layer_dir  # Use RAG-Layer directory
    })
    
    print(f"📊 Using RAG-Layer directory: {os.path.abspath(rag_layer_dir)}")
    
    try:
        # Connect to database
        trainer.connect_to_mysql(
            host='localhost', 
            dbname='cfms', 
            user='newuser', 
            password='newpassword', 
            port=3306
        )
        print("✅ Connected to MySQL database")
        
        # Extract and train on database schema (like in hello.py)
        print("📊 Extracting database schema...")
        df_information_schema = trainer.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
        plan = trainer.get_training_plan_generic(df_information_schema)
        trainer.train(plan=plan)
        
        # Generate advanced reasoning-based training data
        trainer.generate_advanced_training_data()
        
        # Add reasoning-enhanced documentation
        trainer.train(documentation="""
        Reasoning Approach for CFMS Queries:
        
        When answering questions about organizational hierarchy:
        1. First identify if the question requires user data
        2. Determine which hierarchy levels are needed (corps, divs, brigades, units)
        3. Use DIRECT foreign keys from users table (not cascading joins)
        4. Apply appropriate filters (usually is_active = 1 for users)
        5. Order results logically by hierarchy levels
        
        Key insight: Users table has direct foreign keys to all hierarchy levels:
        corp_id, div_id, brigade_id, unit_id
        """)
        
        # Check final training data count
        training_data = trainer.get_training_data()
        print(f"\n✅ Reasoning-enhanced training completed!")
        print(f"📊 Total training items: {len(training_data)}")
        print(f"📁 All training data stored in: {os.path.abspath(rag_layer_dir)}")
        
        print("\n🧠 Your model now has reasoning-enhanced training!")
        print("💡 Test with: python reasoning_vanna.py")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")

if __name__ == "__main__":
    main() 