#!/usr/bin/env python3
"""
Run this after training your model with train.py
"""

import os
import requests
from app.core.config import settings
from app.vana_agent import vn


def get_user_confirmation(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def check_ollama_connection():
    url = settings.OLLAMA_HOST
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is reachable.")
            print("Available models:", [m["model"] for m in response.json().get("models", [])])
        else:
            raise Exception("Unexpected status code")
    except Exception as e:
        print(f"❌ Failed to connect to Ollama at {url}")
        print(f"Reason: {e}")
        exit(1)


def main():
    rag_layer_dir = settings.RAG_LAYER_DIR

    if not os.path.exists(rag_layer_dir):
        print(f"❌ RAG-Layer not found: {os.path.abspath(rag_layer_dir)}")
        print("💡 Run 'python train.py' to train your model.")
        return

    check_ollama_connection()

    print("🔌 Connecting to MySQL database...")
    try:
        vn.connect_to_mysql(
            host=settings.MYSQL_SERVER,
            dbname=settings.MYSQL_DB,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            port=settings.MYSQL_PORT
        )
        print("✅ Connected to MySQL database successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to MySQL: {e}")
        return

    try:
        training_data = vn.get_training_data()
        if training_data.empty:
            print("❌ No training data found. Run train.py first.")
            return

        print(f"📊 Found {len(training_data)} training items")
        print("🤖 VannaSQL Agent is ready! Type 'help' for suggestions or 'quit' to exit.\n")

        while True:
            question = input("❓ Your question: ").strip()

            if question.lower() in ("quit", "exit", "q"):
                print("👋 Goodbye!")
                break
            if not question:
                continue

            print(f"\n🚀 Processing: {question}")
            print("=" * 60)

            try:
                print("🔍 Generating SQL...")
                sql = vn.generate_sql(question, allow_llm_to_see_data=True)
                if not sql.strip():
                    print("❌ No SQL generated.")
                    continue
                print("✅ SQL Generated:\n" + sql)

            except Exception as e:
                print(f"❌ Error generating SQL: {e}")
                continue

            if not get_user_confirmation("Execute this SQL query?"):
                print("⏭️ Skipped execution.\n")
                continue

            print("🔍 Executing SQL...")
            try:
                result_df = vn.run_sql(sql)
                if result_df.empty:
                    print("⚠️ Query returned no results.")
                    continue

                print("✅ Results returned:")
                print(result_df.to_string(max_rows=10, max_cols=8))
                if len(result_df) > 10:
                    print(f"... (showing 10 of {len(result_df)} rows)")

            except Exception as e:
                print(f"❌ SQL Execution Error: {e}")
                continue

            if not get_user_confirmation("Generate a visualization?"):
                print("⏭️ Skipping visualization.\n")
                continue

            print("🔍 Generating Plotly code...")
            try:
                plotly_code = vn.generate_plotly_code(question, sql, result_df)
                if not plotly_code.strip():
                    print("❌ No Plotly code generated.")
                    continue
                print("✅ Plotly Code:\n" + plotly_code)

            except Exception as e:
                print(f"❌ Error generating Plotly code: {e}")
                continue

            if not get_user_confirmation("Create the actual plot?"):
                print("⏭️ Skipping plot creation.\n")
                continue

            print("🔍 Creating plot...")
            try:
                fig = vn.get_plotly_figure(plotly_code=plotly_code, df=result_df)
                if fig:
                    print("✅ Plot created. Use `fig.show()` or `fig.write_html('plot.html')` to view.")
                else:
                    print("❌ Failed to generate plot.")
            except Exception as e:
                print(f"❌ Plot creation error: {e}")

            print("=" * 60 + "\n")

    except Exception as e:
        print(f"❌ Initialization Error: {e}")


if __name__ == "__main__":
    main()
