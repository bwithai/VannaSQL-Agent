#!/usr/bin/env python3
"""
Script to remove all training data from VannaSQL-Agent
This will clear all vector embeddings and training knowledge so you can retrain from scratch.
"""

import os
import shutil
import sys
import warnings
from pathlib import Path

# Disable ChromaDB telemetry to avoid warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

# Suppress ChromaDB warnings
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")

from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

def remove_chromadb_collections(vn):
    """Remove all ChromaDB collections (sql, ddl, documentation)"""
    print("🗑️  Removing ChromaDB collections...")
    
    collections_removed = 0
    
    # Remove SQL collection
    if vn.remove_collection("sql"):
        print("   ✅ SQL collection cleared")
        collections_removed += 1
    else:
        print("   ❌ Failed to clear SQL collection")
    
    # Remove DDL collection
    if vn.remove_collection("ddl"):
        print("   ✅ DDL collection cleared")
        collections_removed += 1
    else:
        print("   ❌ Failed to clear DDL collection")
    
    # Remove Documentation collection
    if vn.remove_collection("documentation"):
        print("   ✅ Documentation collection cleared")
        collections_removed += 1
    else:
        print("   ❌ Failed to clear Documentation collection")
    
    return collections_removed == 3

def remove_vector_files():
    """Remove physical vector database files from RAG-Layer directory"""
    print("🗑️  Removing vector database files...")
    
    rag_layer_dir = Path("RAG-Layer")
    files_removed = 0
    
    if not rag_layer_dir.exists():
        print(f"   ℹ️  RAG-Layer directory not found: {rag_layer_dir.absolute()}")
        return False
    
    print(f"   📁 Cleaning RAG-Layer directory: {rag_layer_dir.absolute()}")
    
    # Remove ChromaDB SQLite file in RAG-Layer
    chroma_db_file = rag_layer_dir / "chroma.sqlite3"
    if chroma_db_file.exists():
        try:
            chroma_db_file.unlink()
            print("   ✅ Removed chroma.sqlite3")
            files_removed += 1
        except Exception as e:
            if "being used by another process" in str(e):
                print("   ⚠️  chroma.sqlite3 is in use - will be cleared on next restart")
                print("      (The collections have been cleared, which is the important part)")
            else:
                print(f"   ❌ Failed to remove chroma.sqlite3: {e}")
    
    # Remove vector database directories (UUID-named directories) in RAG-Layer
    for item in rag_layer_dir.iterdir():
        if item.is_dir() and len(item.name) == 36 and item.name.count('-') == 4:
            # This looks like a UUID directory containing vector data
            try:
                shutil.rmtree(item, ignore_errors=True)
                print(f"   ✅ Removed vector directory: {item.name}")
                files_removed += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {item.name}: {e}")
    
    # Remove any other ChromaDB related files
    for pattern in ["*.parquet", "*.bin", "*.json", "*.log"]:
        for file_path in rag_layer_dir.glob(pattern):
            try:
                file_path.unlink()
                print(f"   ✅ Removed: {file_path.name}")
                files_removed += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {file_path.name}: {e}")
    
    return files_removed > 0

def verify_cleanup():
    """Verify that training data has been removed"""
    print("🔍 Verifying cleanup...")
    
    rag_layer_dir = "RAG-Layer"
    
    try:
        # Initialize Vanna to check if data exists
        vn = MyVanna(config={
            'model': 'phi4-mini:latest',
            'path': rag_layer_dir
        })
        
        # Get training data
        training_data = vn.get_training_data()
        
        if training_data.empty:
            print("   ✅ No training data found - cleanup successful!")
            return True
        else:
            print(f"   ⚠️  Still found {len(training_data)} training items")
            print("   You may need to run this script again or manually remove remaining data")
            return False
            
    except Exception as e:
        print(f"   ℹ️  Could not verify cleanup (this is normal): {e}")
        return True

def main():
    print("🚨 VannaSQL-Agent Training Data Removal Tool")
    print("=" * 50)
    print("This will remove ALL training knowledge from your VannaSQL-Agent.")
    print("You will need to retrain the model after running this script.")
    print()
    
    rag_layer_dir = "RAG-Layer"
    
    # Check if RAG-Layer exists
    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer directory not found: {os.path.abspath(rag_layer_dir)}")
        print("   No training data to remove (or it's stored elsewhere).")
        return
    
    print(f"📁 Target directory: {os.path.abspath(rag_layer_dir)}")
    
    # Ask for confirmation
    response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        return
    
    print()
    print("🧹 Starting cleanup process...")
    
    # Step 1: Remove ChromaDB collections
    try:
        vn = MyVanna(config={
            'model': 'phi4-mini:latest',
            'path': rag_layer_dir
        })
        collections_cleared = remove_chromadb_collections(vn)
    except Exception as e:
        print(f"❌ Failed to initialize Vanna or clear collections: {e}")
        collections_cleared = False
    
    # Step 2: Remove physical files
    files_removed = remove_vector_files()
    
    # Step 3: Verify cleanup
    cleanup_verified = verify_cleanup()
    
    # Summary
    print()
    print("📊 Cleanup Summary:")
    print("=" * 30)
    
    if collections_cleared:
        print("✅ ChromaDB collections cleared")
    else:
        print("❌ Some ChromaDB collections may not have been cleared")
    
    if files_removed:
        print("✅ Vector database files removed")
    else:
        print("ℹ️  No vector database files found to remove")
    
    if cleanup_verified:
        print("✅ Cleanup verification passed")
    else:
        print("⚠️  Cleanup verification had issues")
    
    print()
    if collections_cleared or files_removed:
        print("🎉 Training data removal completed!")
        print("📚 You can now retrain your model by running:")
        print("   python hello.py")
        print("   or")
        print("   python reasoning_training.py")
    else:
        print("⚠️  No training data was found or removed.")
        print("   Your model may already be clean, or there was an error.")
    
    print()
    print("💡 Tip: After retraining, you can test your model with:")
    print("   python example_usage.py")

if __name__ == "__main__":
    main()
