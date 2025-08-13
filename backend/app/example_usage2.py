#!/usr/bin/env python3
"""
Enhanced example usage demonstrating MySQL 8.0 specific features
and improved SQL validation with the updated VannaSQL Agent
"""

import os
import requests
import pandas as pd
from app.core.config import settings
from app.vana_agent import vn


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 🚀 VannaSQL Agent v2.0                      ║
║              Enhanced MySQL 8.0 SQL Generation              ║
║         with Validation & Auto-Regeneration Features        ║
╚══════════════════════════════════════════════════════════════╝
""")


def get_user_confirmation(prompt: str) -> bool:
    """Get yes/no confirmation from user"""
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def print_mysql8_help():
    """Display MySQL 8.0 specific example questions"""
    print("""
💡 MySQL 8.0 Enhanced Example Questions for 'discipline_data' table:

📊 Basic Analytics:
- Show all records from discipline_data table
- What are the unique values in each column?
- Count total records in the discipline_data table

🔍 Window Functions (MySQL 8.0):
- Rank disciplines by a specific metric
- Show row numbers for each discipline record
- Calculate running totals or moving averages

📈 Advanced Queries:
- Group data by categories and show aggregations
- Find top N records using MySQL 8.0 window functions
- Generate statistical summaries of numeric columns

🔧 Data Exploration:
- Describe the structure of discipline_data table
- Show sample data from discipline_data
- Find null values in discipline_data columns

💡 MySQL 8.0 Features to try:
- Common Table Expressions (CTEs) with WITH clause
- JSON functions if any JSON columns exist
- Advanced date/time functions
- Window functions for analytics

Type 'demo' to run demonstration queries
Type 'test' to test SQL validation features
""")


def demonstrate_mysql8_features():
    """Demonstrate MySQL 8.0 specific features"""
    print("\n🎯 Demonstrating MySQL 8.0 Features:")
    print("=" * 60)
    
    demo_questions = [
        "Show the structure of discipline_data table",
        "Count all records in discipline_data table",
        "Show first 5 records from discipline_data table with row numbers using window functions",
        "Get unique values from the first text column in discipline_data table"
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n📝 Demo {i}: {question}")
        print("-" * 50)
        
        try:
            # Generate SQL with enhanced validation
            sql = vn.generate_sql(question)
            print(f"✅ Generated SQL:\n{sql}")
            
            # Validate the SQL
            is_valid = vn.is_sql_valid(sql)
            print(f"🔍 SQL Validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
            
            if not get_user_confirmation("Execute this query?"):
                continue
                
            # Execute the SQL
            result_df = vn.run_sql(sql)
            if result_df is not None and not result_df.empty:
                print("📊 Results:")
                print(result_df.to_string(max_rows=5, max_cols=10))
                if len(result_df) > 5:
                    print(f"... (showing 5 of {len(result_df)} rows)")
            else:
                print("⚠️ No results returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)


def test_sql_validation():
    """Test the SQL validation functionality"""
    print("\n🧪 Testing SQL Validation Features:")
    print("=" * 60)
    
    test_cases = [
        # Valid MySQL queries
        ("SELECT * FROM discipline_data LIMIT 10", "Valid MySQL query", True),
        ("SELECT COUNT(*) FROM discipline_data", "Simple count query", True),
        ("WITH cte AS (SELECT * FROM discipline_data) SELECT * FROM cte", "CTE query", True),
        
        # Invalid queries
        ("SELECT * FROM discipline_data WHERE", "Incomplete WHERE clause", False),
        ("SELECT * FROM discipline_data WHERE (id = 1", "Unbalanced parentheses", False),
        ("SELECT TOP 10 * FROM discipline_data", "SQL Server syntax", False),
        ("SELECT * FROM discipline_data LIMIT 10 OFFSET 5", "PostgreSQL style pagination", False),
        ("SELECT [column] FROM discipline_data", "SQL Server bracket notation", False),
    ]
    
    print("Testing various SQL patterns:")
    for sql, description, expected_valid in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"SQL: {sql}")
        
        is_valid = vn.is_sql_valid(sql)
        status = "✅ PASS" if (is_valid == expected_valid) else "❌ FAIL"
        validation_result = "✅ VALID" if is_valid else "❌ INVALID"
        
        print(f"Expected: {'VALID' if expected_valid else 'INVALID'}")
        print(f"Result: {validation_result} - {status}")


def check_system_requirements():
    """Check if all system requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check Ollama connection
    try:
        response = requests.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["model"] for m in response.json().get("models", [])]
            print(f"✅ Ollama connected. Available models: {models}")
            print(f"🤖 Using model: {settings.OLLAMA_MODEL}")
        else:
            print("❌ Ollama connection failed")
            return False
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False
    
    # Check RAG layer
    if not os.path.exists(settings.RAG_LAYER_DIR):
        print(f"❌ RAG-Layer not found: {os.path.abspath(settings.RAG_LAYER_DIR)}")
        print("💡 Run 'python train.py' to train your model first.")
        return False
    else:
        print(f"✅ RAG-Layer found at: {settings.RAG_LAYER_DIR}")
    
    # Check MySQL connection
    try:
        vn.connect_to_mysql(
            host=settings.MYSQL_SERVER,
            dbname=settings.MYSQL_DB,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            port=settings.MYSQL_PORT
        )
        print("✅ MySQL database connected successfully!")
        print(f"📊 Database: {settings.MYSQL_DB} on {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}")
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False
    
    # Check training data
    try:
        training_data = vn.get_training_data()
        if training_data.empty:
            print("⚠️ No training data found. Consider running train.py first.")
        else:
            print(f"✅ Found {len(training_data)} training items")
    except Exception as e:
        print(f"⚠️ Could not check training data: {e}")
    
    return True


def interactive_mode():
    """Enhanced interactive mode with MySQL 8.0 features"""
    print("\n🤖 VannaSQL Agent v2.0 is ready!")
    print("💡 Type 'help' for examples, 'demo' for demonstrations, 'test' for validation tests")
    print("🚪 Type 'quit' to exit\n")
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ("quit", "exit", "q"):
            print("👋 Goodbye!")
            break
        elif question.lower() == "help":
            print_mysql8_help()
            continue
        elif question.lower() == "demo":
            demonstrate_mysql8_features()
            continue
        elif question.lower() == "test":
            test_sql_validation()
            continue
        elif not question:
            continue
        
        print(f"\n🚀 Processing: {question}")
        print("=" * 60)
        
        try:
            # Generate SQL with enhanced MySQL 8.0 features
            print("🔍 Generating MySQL 8.0 compatible SQL...")
            sql = vn.generate_sql(question, allow_llm_to_see_data=True)
            
            if not sql.strip():
                print("❌ No SQL generated.")
                continue
                
            print("✅ Generated SQL:")
            print(f"```sql\n{sql}\n```")
            
            # Show validation result
            is_valid = vn.is_sql_valid(sql)
            print(f"🔍 SQL Validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
            
            if not is_valid:
                print("⚠️ The generated SQL failed validation checks.")
                if not get_user_confirmation("Try to execute anyway?"):
                    continue
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            continue
        
        # Execute SQL
        if not get_user_confirmation("Execute this SQL query?"):
            print("⏭️ Skipped execution.\n")
            continue
        
        print("🔍 Executing SQL...")
        try:
            result_df = vn.run_sql(sql)
            if result_df is not None and not result_df.empty:
                print("✅ Query executed successfully!")
                print("📊 Results:")
                print(result_df.to_string(max_rows=10, max_cols=8))
                if len(result_df) > 10:
                    print(f"... (showing 10 of {len(result_df)} rows)")
                    
                # Offer to save results
                if get_user_confirmation("Save results to CSV?"):
                    filename = f"query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    result_df.to_csv(filename, index=False)
                    print(f"💾 Results saved to: {filename}")
            else:
                print("⚠️ Query returned no results.")
                
        except Exception as e:
            print(f"❌ SQL Execution Error: {e}")
            continue
        
        # Generate visualization
        if len(result_df) > 0 and get_user_confirmation("Generate a visualization?"):
            print("🔍 Generating Plotly visualization code...")
            try:
                plotly_code = vn.generate_plotly_code(question, sql, result_df)
                if plotly_code.strip():
                    print("✅ Plotly Code Generated:")
                    print(f"```python\n{plotly_code}\n```")
                    
                    if get_user_confirmation("Create the actual plot?"):
                        fig = vn.get_plotly_figure(plotly_code=plotly_code, df=result_df)
                        if fig:
                            plot_filename = f"plot_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html"
                            fig.write_html(plot_filename)
                            print(f"📈 Plot saved to: {plot_filename}")
                        else:
                            print("❌ Failed to generate plot.")
                else:
                    print("❌ No Plotly code generated.")
            except Exception as e:
                print(f"❌ Visualization error: {e}")
        
        print("=" * 60 + "\n")


def main():
    """Main function with enhanced MySQL 8.0 features"""
    print_banner()
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please fix the issues above.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All systems ready! Enhanced MySQL 8.0 features available:")
    print("   • Advanced SQL validation with MySQL 8.0 syntax checking")
    print("   • Automatic query regeneration on validation failures")
    print("   • Window functions and CTE support")
    print("   • Improved error handling and logging")
    print("   • Enhanced discipline_data table context")
    print("=" * 60)
    
    # Start interactive mode
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
