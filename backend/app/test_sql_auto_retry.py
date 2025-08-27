#!/usr/bin/env python3
"""
Test script to demonstrate SQL auto-retry functionality.
This script shows how the FastAPI handles SQL errors and auto-correction.
"""

import asyncio
import json
import requests
import time


def test_sql_auto_retry():
    """Test the SQL auto-retry functionality with various error scenarios."""
    
    base_url = "http://localhost:8000"
    
    # Test cases with intentional errors
    test_cases = [
        {
            "name": "Wrong Table Name",
            "question": "SELECT * FROM wrong_table_name LIMIT 5",
            "expected_error_type": "table not exist"
        },
        {
            "name": "Wrong Column Name", 
            "question": "SELECT wrong_column FROM discipline_data LIMIT 5",
            "expected_error_type": "column not exist"
        },
        {
            "name": "Syntax Error",
            "question": "SELEC * FROM discipline_data WHER id = 1",
            "expected_error_type": "syntax error"
        },
        {
            "name": "Valid Query (Should Work)",
            "question": "What are the different types of punishments in the discipline data?",
            "expected_error_type": None
        }
    ]
    
    print("🧪 Testing SQL Auto-Retry Functionality")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Question: {test_case['question']}")
        
        try:
            # Step 1: Generate SQL
            print("   📝 Generating SQL...")
            gen_response = requests.get(
                f"{base_url}/api/v0/generate_sql",
                params={"question": test_case['question']},
                timeout=30
            )
            
            if gen_response.status_code != 200:
                print(f"   ❌ Failed to generate SQL: {gen_response.status_code}")
                continue
                
            gen_data = gen_response.json()
            query_id = gen_data.get("id")
            generated_sql = gen_data.get("text")
            
            print(f"   📋 Generated SQL: {generated_sql}")
            print(f"   🆔 Query ID: {query_id}")
            
            # Step 2: Execute SQL (this will trigger auto-retry if needed)
            print("   🔄 Executing SQL (with auto-retry)...")
            exec_response = requests.get(
                f"{base_url}/api/v0/run_sql",
                params={"id": query_id},
                timeout=60  # Longer timeout for retries
            )
            
            if exec_response.status_code != 200:
                print(f"   ❌ Failed to execute SQL: {exec_response.status_code}")
                continue
                
            exec_data = exec_response.json()
            
            if exec_data.get("type") == "df":
                # Success
                print("   ✅ SQL executed successfully!")
                if exec_data.get("sql_corrected"):
                    print(f"   🔧 SQL was auto-corrected ({exec_data.get('correction_attempts')} attempts)")
                else:
                    print("   📊 SQL worked on first try")
                    
                # Show sample data
                df_json = exec_data.get("df")
                if df_json:
                    df_data = json.loads(df_json)
                    print(f"   📈 Returned {len(df_data)} rows")
                    
            elif exec_data.get("type") == "sql_error":
                # Failed after retries
                print("   ❌ SQL execution failed after retries")
                print(f"   💬 Error: {exec_data.get('error')}")
                
                if exec_data.get("max_retries_reached"):
                    print("   🔄 Maximum retry attempts reached")
                    
                # Get error history
                if query_id:
                    history_response = requests.get(
                        f"{base_url}/api/v0/get_error_history",
                        params={"id": query_id}
                    )
                    
                    if history_response.status_code == 200:
                        history_data = history_response.json()
                        error_history = history_data.get("error_history", [])
                        
                        print(f"   📚 Error History ({len(error_history)} attempts):")
                        for j, error in enumerate(error_history, 1):
                            print(f"      Attempt {j}: {error.get('database_error', 'Unknown error')}")
                            if error.get('corrected_sql'):
                                print(f"      Corrected SQL: {error['corrected_sql'][:100]}...")
                            if error.get('user_explanation'):
                                print(f"      🤖 LLM Explanation: {error['user_explanation'][:200]}...")
            
            print("   " + "-" * 40)
            
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print("\n🏁 Testing completed!")


def test_single_query(question: str):
    """Test a single query and show detailed retry information."""
    
    base_url = "http://localhost:8000"
    
    print(f"🔍 Testing single query: {question}")
    print("=" * 60)
    
    try:
        # Generate SQL
        print("📝 Step 1: Generating SQL...")
        gen_response = requests.get(
            f"{base_url}/api/v0/generate_sql",
            params={"question": question},
            timeout=30
        )
        
        gen_data = gen_response.json()
        query_id = gen_data.get("id")
        generated_sql = gen_data.get("text")
        
        print(f"Generated SQL:\n{generated_sql}\n")
        
        # Execute with retry
        print("🔄 Step 2: Executing SQL (with auto-retry)...")
        exec_response = requests.get(
            f"{base_url}/api/v0/run_sql", 
            params={"id": query_id},
            timeout=60
        )
        
        exec_data = exec_response.json()
        
        print(f"Execution Result: {exec_data.get('type')}")
        
        if exec_data.get("sql_corrected"):
            print(f"✅ SQL was auto-corrected after {exec_data.get('correction_attempts')} attempts")
        
        # Always show error history if available
        history_response = requests.get(
            f"{base_url}/api/v0/get_error_history",
            params={"id": query_id}
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            error_history = history_data.get("error_history", [])
            
            if error_history:
                print(f"\n📚 Detailed Error History:")
                for i, error in enumerate(error_history, 1):
                    print(f"\nAttempt {i}:")
                    print(f"  SQL: {error.get('sql')}")
                    print(f"  Database Error: {error.get('database_error')}")
                    if error.get('corrected_sql'):
                        print(f"  LLM Correction: {error.get('corrected_sql')}")
                    if error.get('user_explanation'):
                        print(f"  🤖 LLM Explanation:\n     {error.get('user_explanation')}")
                    if error.get('llm_error'):
                        print(f"  ❌ LLM Error: {error.get('llm_error')}")
        
        # Show final result
        if exec_data.get("type") == "df":
            df_json = exec_data.get("df")
            if df_json:
                df_data = json.loads(df_json)
                print(f"\n📊 Success! Returned {len(df_data)} rows")
                if df_data:
                    print("Sample data:")
                    print(json.dumps(df_data[0], indent=2))
        else:
            print(f"\n❌ Final Error: {exec_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test a single query provided as argument
        question = " ".join(sys.argv[1:])
        test_single_query(question)
    else:
        # Run all test cases
        test_sql_auto_retry()
