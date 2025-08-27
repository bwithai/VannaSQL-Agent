#!/usr/bin/env python3
"""
Script to view and analyze training data in VannaSQL-Agent
This will show you all your stored training knowledge including SQL, DDL, and documentation data.
"""

import os
import warnings
import json
from app.core.config import settings
from app.vana_agent import vn

# Disable ChromaDB telemetry to avoid warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

# Suppress ChromaDB warnings
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")



def display_training_statistics(df):
    """Display statistics about the training data"""
    print("📊 Training Data Statistics")
    print("=" * 40)
    
    if df.empty:
        print("❌ No training data found!")
        print("   Run python train.py to train your model first.")
        return
    
    # Overall statistics
    print(f"📋 Total Training Items: {len(df)}")
    print()
    
    # Statistics by type
    if 'training_data_type' in df.columns:
        type_counts = df['training_data_type'].value_counts()
        print("📈 By Training Data Type:")
        for data_type, count in type_counts.items():
            icon = {"sql": "🔍", "ddl": "🏗️", "documentation": "📚"}.get(data_type, "📄")
            print(f"   {icon} {data_type.upper()}: {count} items")
    
    print()

def display_training_data(df, data_type=None, limit=None, detailed=False):
    """Display training data with optional filtering"""
    
    # Filter by type if specified
    if data_type:
        if 'training_data_type' in df.columns:
            df_filtered = df[df['training_data_type'] == data_type.lower()]
            if df_filtered.empty:
                print(f"❌ No {data_type.upper()} training data found.")
                return
        else:
            print("❌ No training data type information available.")
            return
    else:
        df_filtered = df
    
    # Apply limit if specified
    if limit and len(df_filtered) > limit:
        df_filtered = df_filtered.head(limit)
        print(f"📋 Showing first {limit} items (total: {len(df)})")
    
    print()
    print("🗂️  Training Data Content")
    print("=" * 50)
    
    for idx, row in df_filtered.iterrows():
        data_type = row.get('training_data_type', 'unknown')
        content = row.get('content', '')
        question = row.get('question', '')
        item_id = row.get('id', '')
        
        # Icon for data type
        icon = {"sql": "🔍", "ddl": "🏗️", "documentation": "📚"}.get(data_type, "📄")
        
        print(f"\n{icon} {data_type.upper()} Training Item:")
        print(f"   ID: {item_id}")
        
        if question:
            print(f"   Question: {question}")
        
        if detailed:
            print(f"   Content: {content}")
        else:
            # Show truncated content
            truncated_content = content[:200] + "..." if len(content) > 200 else content
            print(f"   Content: {truncated_content}")
        
        print("-" * 50)

def search_training_data(df, search_term):
    """Search for specific terms in training data"""
    if df.empty:
        print("❌ No training data to search.")
        return
    
    print(f"🔍 Searching for: '{search_term}'")
    print("=" * 40)
    
    # Search in content and questions
    matches = df[
        (df['content'].str.contains(search_term, case=False, na=False)) |
        (df['question'].str.contains(search_term, case=False, na=False))
    ]
    
    if matches.empty:
        print(f"❌ No matches found for '{search_term}'")
        return
    
    print(f"✅ Found {len(matches)} matches:")
    print()
    
    for idx, row in matches.iterrows():
        data_type = row.get('training_data_type', 'unknown')
        content = row.get('content', '')
        question = row.get('question', '')
        
        icon = {"sql": "🔍", "ddl": "🏗️", "documentation": "📚"}.get(data_type, "📄")
        
        print(f"{icon} {data_type.upper()}:")
        if question:
            print(f"   Question: {question}")
        
        # Highlight search term in content
        highlighted_content = content.replace(
            search_term, f"**{search_term}**"
        )
        truncated_content = highlighted_content[:300] + "..." if len(highlighted_content) > 300 else highlighted_content
        print(f"   Content: {truncated_content}")
        print()

def export_training_data(df, filename="training_data_export.json"):
    """Export training data to JSON file"""
    if df.empty:
        print("❌ No training data to export.")
        return
    
    try:
        # Convert DataFrame to JSON
        export_data = df.to_dict('records')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Training data exported to: {filename}")
        print(f"   Exported {len(df)} training items")
    except Exception as e:
        print(f"❌ Failed to export training data: {e}")

def show_menu():
    """Display the interactive menu"""
    print("\n🎛️  Training Data Viewer Options:")
    print("=" * 35)
    print("1. 📊 Show statistics")
    print("2. 🔍 View SQL training data")
    print("3. 🏗️  View DDL training data") 
    print("4. 📚 View documentation training data")
    print("5. 📋 View all training data")
    print("6. 🔍 Search training data")
    print("7. 💾 Export training data to JSON")
    print("8. 🔄 Refresh data")
    print("9. ❌ Exit")
    print()

def main():
    print("👁️  VannaSQL-Agent Training Data Viewer")
    print("=" * 45)
    print("This tool lets you explore your training knowledge.")
    print()
    
    # Use RAG-Layer directory from settings
    rag_layer_dir = settings.RAG_LAYER_DIR
    
    # Check if RAG-Layer directory exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   Run 'python train.py' to train your model first.")
        return
    
    try:
        # Connect to MySQL using settings (vn is already initialized with config)
        print(f"🔌 Connecting to VannaSQL-Agent (RAG-Layer: {os.path.abspath(rag_layer_dir)})...")
        vn.connect_to_mysql(
            host=settings.MYSQL_SERVER, 
            dbname=settings.MYSQL_DB, 
            user=settings.MYSQL_USER, 
            password=settings.MYSQL_PASSWORD,
            port=settings.MYSQL_PORT
        )
        print("✅ Connected successfully!")
        
        # Load training data
        print("📊 Loading training data...")
        df = vn.get_training_data()
        
        if df.empty:
            print("❌ No training data found!")
            print("   Run 'python train.py' to train your model first.")
            return
        
        print(f"✅ Loaded {len(df)} training items from RAG-Layer")
        
        # Interactive menu
        while True:
            show_menu()
            
            try:
                choice = input("Select an option (1-9): ").strip()
                
                if choice == '1':
                    display_training_statistics(df)
                
                elif choice == '2':
                    limit = input("Limit results (press Enter for all): ").strip()
                    limit = int(limit) if limit.isdigit() else None
                    detailed = input("Show detailed content? (y/n): ").strip().lower() == 'y'
                    display_training_data(df, 'sql', limit, detailed)
                
                elif choice == '3':
                    limit = input("Limit results (press Enter for all): ").strip()
                    limit = int(limit) if limit.isdigit() else None
                    detailed = input("Show detailed content? (y/n): ").strip().lower() == 'y'
                    display_training_data(df, 'ddl', limit, detailed)
                
                elif choice == '4':
                    limit = input("Limit results (press Enter for all): ").strip()
                    limit = int(limit) if limit.isdigit() else None
                    detailed = input("Show detailed content? (y/n): ").strip().lower() == 'y'
                    display_training_data(df, 'documentation', limit, detailed)
                
                elif choice == '5':
                    limit = input("Limit results (press Enter for all): ").strip()
                    limit = int(limit) if limit.isdigit() else None
                    detailed = input("Show detailed content? (y/n): ").strip().lower() == 'y'
                    display_training_data(df, None, limit, detailed)
                
                elif choice == '6':
                    search_term = input("Enter search term: ").strip()
                    if search_term:
                        search_training_data(df, search_term)
                
                elif choice == '7':
                    filename = input("Export filename (default: training_data_export.json): ").strip()
                    if not filename:
                        filename = "training_data_export.json"
                    export_training_data(df, filename)
                
                elif choice == '8':
                    print("🔄 Refreshing training data...")
                    df = vn.get_training_data()
                    print(f"✅ Refreshed! Now showing {len(df)} training items")
                
                elif choice == '9':
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid option. Please select 1-9.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize VannaSQL-Agent: {e}")
        print("   Make sure you have trained your model first with 'python train.py'")

if __name__ == "__main__":
    main()
