#!/usr/bin/env python3
"""
Example usage script for the trained Vanna model.
Run this after training your model with hello.py
"""

import os
import warnings
import sys
import contextlib
import time

# Set ChromaDB environment variables at the very beginning
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["CHROMA_CLIENT_AUTH_PROVIDER"] = ""
os.environ["CHROMA_SERVER_AUTH_PROVIDER"] = ""
os.environ["CHROMA_SERVER_AUTHN_PROVIDER"] = ""
os.environ["CHROMA_CLIENT_AUTHN_PROVIDER"] = ""

# Suppress all warnings
warnings.filterwarnings("ignore")

# More aggressive stderr suppression
@contextlib.contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Import ChromaDB first with complete suppression
with suppress_stdout_stderr():
    try:
        import chromadb
        from chromadb.config import Settings
        # Pre-configure ChromaDB settings
        chromadb.configure(anonymized_telemetry=False)
    except:
        pass

# Now import Vanna modules with suppression
with suppress_stdout_stderr():
    from vanna.ollama import Ollama
    from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        # Ensure telemetry is disabled in config
        if config is None:
            config = {}
        config['anonymized_telemetry'] = False
        
        with suppress_stdout_stderr():
            ChromaDB_VectorStore.__init__(self, config=config)
            Ollama.__init__(self, config=config)

    def ask_with_timeout(self, question: str, timeout_seconds: int = 30):
        """Enhanced ask method with timeout and step-by-step processing"""
        print(f"🔍 Step 1: Generating SQL for: '{question}'")
        
        try:
            # Step 1: Generate SQL with timeout
            start_time = time.time()
            sql = self.generate_sql(question)
            generation_time = time.time() - start_time
            
            if generation_time > timeout_seconds:
                print(f"⏰ SQL generation timed out after {generation_time:.1f}s")
                return None
                
            print(f"✅ SQL Generated in {generation_time:.1f}s:")
            print(f"📝 SQL: {sql}")
            
            # Step 2: Validate SQL
            if not sql or sql.strip() == "":
                print("❌ Empty SQL generated")
                return None
                
            # Step 3: Execute SQL
            print("🔍 Step 2: Executing SQL query...")
            start_time = time.time()
            
            result_df = self.run_sql(sql)
            execution_time = time.time() - start_time
            
            print(f"✅ Query executed in {execution_time:.1f}s")
            
            if result_df is None or result_df.empty:
                print("⚠️  Query returned no results")
                return None
                
            print(f"📊 Results: {len(result_df)} rows returned")
            return result_df
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            return None

def main():
    # RAG-Layer directory path
    rag_layer_dir = "RAG-Layer"
    
    # Check if RAG-Layer directory exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   Run 'python hello.py' to train your model first.")
        return
    
    # Initialize with the same config as training (using RAG-Layer directory)
    print("🔌 Initializing VannaSQL-Agent...")
    vn = MyVanna(config={
        'model': 'phi4-mini:latest',  # Use same model as in hello.py
        'path': rag_layer_dir,  # Use RAG-Layer directory
        'anonymized_telemetry': False,  # Explicitly disable telemetry
        # Ollama optimization settings
        'num_predict': 2048,  # Limit response length
        'temperature': 0.1,   # More deterministic responses
        'top_p': 0.9,        # Focus on most likely tokens
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
        print("\n🤖 Enhanced Vanna SQL Agent is ready!")
        print("This version uses step-by-step processing with timeout handling.")
        print("Ask me questions about your database in natural language.")
        print("Type 'quit' to exit, 'help' for examples, 'debug' for training data info.\n")
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                    
                if question.lower() == 'help':
                    print_help()
                    continue
                    
                if question.lower() == 'debug':
                    show_debug_info(vn)
                    continue
                    
                if not question:
                    continue
                
                print(f"\n🚀 Processing: {question}")
                print("=" * 50)
                
                # Use enhanced ask method with timeout
                result = vn.ask_with_timeout(question, timeout_seconds=45)
                
                if result is not None:
                    print("\n📋 Query Results:")
                    print(result.to_string(max_rows=10, max_cols=8))
                    if len(result) > 10:
                        print(f"... (showing first 10 of {len(result)} rows)")
                else:
                    print("\n❌ No results returned")
                
                print("=" * 50 + "\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        if "'cryptography' package is required" in str(e):
            print("💡 Fix: Install the missing package with:")
            print("   pip install cryptography")

def show_debug_info(vn):
    """Show debug information about training data"""
    print("\n🔍 Debug Information:")
    print("=" * 30)
    
    try:
        training_data = vn.get_training_data()
        
        if not training_data.empty:
            type_counts = training_data['training_data_type'].value_counts()
            print("📊 Training Data Breakdown:")
            for data_type, count in type_counts.items():
                icon = {"sql": "🔍", "ddl": "🏗️", "documentation": "📚"}.get(data_type, "📄")
                print(f"   {icon} {data_type.upper()}: {count} items")
            
            print(f"\n📝 Recent SQL Training Examples:")
            sql_data = training_data[training_data['training_data_type'] == 'sql'].head(3)
            for idx, row in sql_data.iterrows():
                content = row.get('content', '')[:100] + "..." if len(row.get('content', '')) > 100 else row.get('content', '')
                print(f"   • {content}")
        else:
            print("❌ No training data found")
            
    except Exception as e:
        print(f"❌ Error getting debug info: {e}")
    
    print("=" * 30 + "\n")

def print_help():
    print("\n📖 Example questions you can ask:")
    print("- 'Show me all active users with their hierarchy'")
    print("- 'How many users are in each corps?'")
    print("- 'List all active users and their roles'") 
    print("- 'Show the organizational structure'")
    print("- 'Get user count by role'")
    print("- 'Find all superusers'")
    print("\n💡 Tips for better results:")
    print("- Be specific about what you want")
    print("- Use 'active users' for users where is_active = 1")
    print("- Mention 'hierarchy' for organizational structure")
    print("- Ask for 'count' or 'number' for aggregate queries")
    print()

if __name__ == "__main__":
    main() 