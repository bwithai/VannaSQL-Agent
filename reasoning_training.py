#!/usr/bin/env python3
"""
Advanced training script leveraging Phi4-reasoning capabilities
Uses chain-of-thought to generate comprehensive training data
"""

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

    def generate_comprehensive_documentation(self, schema_info):
        """Generate comprehensive documentation using reasoning"""
        doc_prompt = f"""
        <think>
        I need to analyze this database schema and create comprehensive documentation:
        
        {schema_info}
        
        Let me think through:
        1. What are the main entities and their purposes?
        2. How do tables relate to each other?
        3. What are the key business concepts?
        4. What common query patterns would be useful?
        </think>
        
        Generate comprehensive database documentation explaining the structure, relationships, and common use cases.
        """
        
        return self.generate_sql(doc_prompt)

def main():
    # Initialize reasoning trainer
    trainer = ReasoningTrainer(config={'model': 'phi4-mini:latest'})
    
    try:
        trainer.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
        print("🧠 Reasoning Trainer initialized")
        
        # Extract schema for reasoning-based documentation
        print("📊 Extracting schema...")
        df_schema = trainer.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'cfms'")
        
        # Generate reasoning-based training plan
        print("🤔 Creating reasoning-based training plan...")
        plan = trainer.get_training_plan_generic(df_schema)
        trainer.train(plan=plan)
        
        # Add reasoning-enhanced documentation
        print("📚 Generating reasoning-enhanced documentation...")
        
        # CFMS-specific reasoning training
        reasoning_docs = {
            "organizational_hierarchy": """
            <think>
            The CFMS system has a hierarchical military structure:
            - Users can belong to different levels: corps, divisions, brigades, units
            - Each user has DIRECT foreign keys to all hierarchy levels
            - This allows for flexible organizational queries
            - Active users are identified by is_active = 1
            </think>
            
            CFMS organizational structure uses direct foreign key relationships from users to all hierarchy levels (corps, divisions, brigades, units). This enables efficient queries without cascading joins.
            """,
            
            "query_patterns": """
            <think>
            Common CFMS query patterns:
            1. Active user queries: Always filter by is_active = 1
            2. Hierarchy queries: Use direct JOINs from users table
            3. Role-based queries: Role information stored directly in users table
            4. Financial tracking: Multiple tables for funds, expenses, balances
            </think>
            
            Key CFMS query patterns involve filtering active users, using direct hierarchy joins, and accessing role information from the users table.
            """
        }
        
        for topic, doc in reasoning_docs.items():
            trainer.train(documentation=doc)
            print(f"✅ Added reasoning documentation for: {topic}")
        
        # Train with reasoning for common complex queries
        complex_queries = [
            {
                "question": "Get all active users with their complete organizational hierarchy",
                "sql": """
                SELECT 
                    usr.username,
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
                ORDER BY c.name, d.name, b.name, u.name
                """
            },
            {
                "question": "Count active users by organizational level",
                "sql": """
                SELECT 
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
                GROUP BY c.id, c.name, d.id, d.name, b.id, b.name, u.id, u.name
                ORDER BY c.name, d.name, b.name, u.name
                """
            }
        ]
        
        print("🎯 Training complex queries with reasoning...")
        for query in complex_queries:
            trainer.train_with_reasoning(query["question"], query["sql"])
        
        # Test the reasoning capabilities
        print("\n🧪 Testing reasoning capabilities...")
        test_result = trainer.ask("Explain how to get active users with organizational hierarchy using step-by-step reasoning")
        print("🤖 Reasoning Test Result:")
        print(test_result)
        
        print("\n✅ Reasoning-enhanced training complete!")
        print("🚀 Your model now has advanced reasoning capabilities for SQL generation!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 