#!/usr/bin/env python3
"""
Test script to verify RAG-layer caching implementation
"""

import os
import sys
sys.path.append('backend/app')

from vanna.chromadb import ChromaDB_VectorStore
from vanna.ollama import Ollama

class TestVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {
                'path': './test-rag-layer',
                'model': 'phi4-mini:latest',
                'ollama_host': 'http://localhost:11434'
            }
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

def test_caching():
    print("🧪 Testing RAG-layer caching implementation...")
    
    # Initialize test instance
    vn = TestVanna()
    
    # Test 1: Add a question-SQL pair
    test_question = "What are the top 5 customers by sales?"
    test_sql = "SELECT customer_name, SUM(sales_amount) as total_sales FROM sales GROUP BY customer_name ORDER BY total_sales DESC LIMIT 5;"
    
    print(f"📝 Adding test question-SQL pair to RAG layer...")
    vn.add_question_sql(test_question, test_sql)
    
    # Test 2: Check exact match retrieval
    print(f"🔍 Testing exact question matching...")
    cached_sql = vn.get_exact_question_sql(test_question)
    
    if cached_sql:
        print(f"✅ Found cached SQL: {cached_sql[:50]}...")
        if cached_sql.strip() == test_sql.strip():
            print("✅ Cached SQL matches original!")
        else:
            print("❌ Cached SQL doesn't match original")
    else:
        print("❌ No cached SQL found")
    
    # Test 3: Check case insensitive matching
    print(f"🔍 Testing case insensitive matching...")
    cached_sql_case = vn.get_exact_question_sql(test_question.upper())
    
    if cached_sql_case:
        print("✅ Case insensitive matching works!")
    else:
        print("❌ Case insensitive matching failed")
    
    # Test 4: Test similar question retrieval (should still work)
    print(f"🔍 Testing similar question retrieval...")
    similar_questions = vn.get_similar_question_sql(test_question)
    print(f"📊 Found {len(similar_questions)} similar questions")
    
    # Test 5: Test generate_sql with caching
    print(f"🔄 Testing generate_sql with caching...")
    try:
        # This should use cached SQL
        generated_sql = vn.generate_sql(test_question)
        if generated_sql == test_sql:
            print("✅ generate_sql returned cached SQL!")
        else:
            print(f"⚠️ generate_sql returned different SQL: {generated_sql[:50]}...")
    except Exception as e:
        print(f"⚠️ generate_sql failed (expected if no LLM available): {e}")
    
    print("🎉 RAG-layer caching test completed!")

if __name__ == "__main__":
    test_caching()
