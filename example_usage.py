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

def get_user_confirmation(prompt):
    """Get user confirmation (y/n)"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    # RAG-Layer directory path
    rag_layer_dir = "RAG-Layer"
    
    # Check if RAG-Layer directory exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   Run 'python hello.py' to train your model first.")
        return
    
    # Initialize with the same config as training
    print("🔌 Initializing VannaSQL-Agent...")
    vn = MyVanna(config={
        'model': 'phi4-mini:latest',
        'path': rag_layer_dir,
        "keep_alive": "5m"
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
        print("You'll see each step of the process: SQL generation → execution → visualization")
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
                
                print(f"\n🚀 Processing: {question}")
                print("=" * 60)
                
                # Step 1: Generate SQL
                print("🔍 Step 1: Generating SQL from your question...")
                try:
                    sql = vn.generate_sql(question)
                    if not sql or sql.strip() == "":
                        print("❌ Failed to generate SQL")
                        continue
                    
                    print("✅ SQL Generated:")
                    print("📝 Generated SQL Query:")
                    print("-" * 40)
                    print(sql)
                    print("-" * 40)
                    
                except Exception as e:
                    print(f"❌ Error generating SQL: {e}")
                    continue
                
                # Step 2: Ask user if they want to run the SQL
                if not get_user_confirmation("🚀 Do you want to execute this SQL query?"):
                    print("⏭️ Skipping query execution.\n")
                    continue
                
                # Step 3: Run SQL
                print("\n🔍 Step 2: Executing SQL query...")
                try:
                    result_df = vn.run_sql(sql)
                    if result_df is None or result_df.empty:
                        print("⚠️ Query returned no results")
                        continue
                    
                    print("✅ Query executed successfully!")
                    print(f"📊 Results: {len(result_df)} rows returned")
                    print("\n📋 Query Results:")
                    print(result_df.to_string(max_rows=10, max_cols=8))
                    if len(result_df) > 10:
                        print(f"... (showing first 10 of {len(result_df)} rows)")
                    
                except Exception as e:
                    print(f"❌ Error executing SQL: {e}")
                    continue
                
                # Step 4: Ask if user wants to generate a plot
                if not get_user_confirmation("\n📊 Do you want to generate a visualization for this data?"):
                    print("⏭️ Skipping visualization.\n")
                    print("=" * 60 + "\n")
                    continue
                
                # Step 5: Generate Plotly code
                print("\n🔍 Step 3: Generating visualization code...")
                try:
                    plotly_code = vn.generate_plotly_code(question=question, sql=sql, df=result_df)
                    if not plotly_code or plotly_code.strip() == "":
                        print("❌ Failed to generate visualization code")
                        print("=" * 60 + "\n")
                        continue
                    
                    print("✅ Plotly Code Generated:")
                    print("📝 Generated Plotly Code:")
                    print("-" * 40)
                    print(plotly_code)
                    print("-" * 40)
                    
                except Exception as e:
                    print(f"❌ Error generating plotly code: {e}")
                    print("=" * 60 + "\n")
                    continue
                
                # Step 6: Ask if user wants to create the plot
                if not get_user_confirmation("🎨 Do you want to create and display the plot?"):
                    print("⏭️ Skipping plot creation.\n")
                    print("=" * 60 + "\n")
                    continue
                
                # Step 7: Generate the actual plot
                print("\n🔍 Step 4: Creating visualization...")
                try:
                    fig = vn.get_plotly_figure(plotly_code=plotly_code, df=result_df)
                    if fig:
                        print("✅ Visualization created successfully!")
                        print("📊 Plot has been generated. In a Jupyter notebook, it would display automatically.")
                        print("💡 You can save the plot using fig.write_html('plot.html') or fig.show()")
                    else:
                        print("❌ Failed to create visualization")
                        
                except Exception as e:
                    print(f"❌ Error creating plot: {e}")
                
                print("=" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def print_help():
    print("\n📖 Example questions you can ask:")
    print("- 'Show me all active users with their hierarchy'")
    print("- 'How many users are in each corps?'")
    print("- 'List all active users and their roles'") 
    print("- 'Show the organizational structure'")
    print("- 'Get user count by role'")
    print("- 'Find all superusers'")
    print("- 'Show me expense trends over time'")
    print("- 'What is the total budget allocation by formation?'")
    print("\n💡 Process Flow:")
    print("1. 🔍 SQL Generation - AI converts your question to SQL")
    print("2. 🚀 Query Execution - Run the SQL on your database") 
    print("3. 📊 Visualization Code - Generate Plotly code for charts")
    print("4. 🎨 Plot Creation - Create the actual visualization")
    print("\n💡 Tips for better results:")
    print("- Be specific about what you want")
    print("- Use 'active users' for users where is_active = 1")
    print("- Mention 'hierarchy' for organizational structure")
    print("- Ask for 'count' or 'number' for aggregate queries")
    print("- Questions about trends work well for visualizations")
    print()

if __name__ == "__main__":
    main() 