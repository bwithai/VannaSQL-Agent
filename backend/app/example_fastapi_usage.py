#!/usr/bin/env python3
"""
Example usage of VannaSQL with FastAPI.
This demonstrates how to set up and use the async FastAPI interface.
"""

import asyncio
import os
import sys
from typing import Optional

from app.core.config import settings
from app.vana_agent import vn
from app.vanna.fastapi import VannaFastAPIApp, AsyncMemoryCache, AsyncNoAuth


async def setup_vanna():
    """Setup and connect Vanna to the database."""
    print("🔌 Connecting to MySQL database...")
    
    # Connect to database (this is synchronous, so we run it in executor)
    await asyncio.get_event_loop().run_in_executor(
        None,
        vn.connect_to_mysql,
        settings.MYSQL_SERVER,
        settings.MYSQL_DB, 
        settings.MYSQL_USER,
        settings.MYSQL_PASSWORD,
        settings.MYSQL_PORT
    )
    print("✅ Connected to MySQL database")


async def example_basic_api():
    """Example: Basic FastAPI app without UI."""
    from app.vanna.fastapi import VannaFastAPI
    
    await setup_vanna()
    
    # Create basic API-only app
    api = VannaFastAPI(
        vn=vn,
        allow_llm_to_see_data=True,
        chart=True
    )
    
    print("🚀 Starting basic FastAPI app...")
    print("📋 API docs: http://localhost:8001/docs")
    
    # Run on different port
    api.run(host='0.0.0.0', port=8001)


async def example_full_app():
    """Example: Full FastAPI app with UI."""
    await setup_vanna()
    
    # Create full app with UI
    app = VannaFastAPIApp(
        vn=vn,
        cache=AsyncMemoryCache(),
        auth=AsyncNoAuth(),
        allow_llm_to_see_data=True,
        title="My VannaSQL FastAPI App",
        subtitle="Powered by FastAPI and phi4-mini",
        chart=True,
        show_training_data=True,
        suggested_questions=True
    )
    
    print("🌐 Starting full VannaSQL FastAPI app...")
    print("📱 Web interface: http://localhost:8000")
    print("📋 API docs: http://localhost:8000/docs") 
    print("🔍 ReDoc: http://localhost:8000/redoc")
    
    app.run(host='0.0.0.0', port=8000)


async def example_async_operations():
    """Example: Using async operations programmatically."""
    await setup_vanna()
    
    from app.vanna.fastapi import AsyncMemoryCache
    
    # Create cache and store some data
    cache = AsyncMemoryCache()
    
    # Generate a question ID
    question_id = await cache.generate_id(question="What are the top customers?")
    
    # Store question and generated SQL
    await cache.set(question_id, "question", "What are the top customers?")
    
    # Simulate generating SQL (in real app this would be async too)
    sql = await asyncio.get_event_loop().run_in_executor(
        None, 
        vn.generate_sql, 
        "What are the top customers?"
    )
    await cache.set(question_id, "sql", sql)
    
    # Retrieve cached data
    cached_question = await cache.get(question_id, "question")
    cached_sql = await cache.get(question_id, "sql")
    
    print(f"📝 Question: {cached_question}")
    print(f"🔍 Generated SQL: {cached_sql}")
    
    # Get all cached items
    all_items = await cache.get_all(["question", "sql"])
    print(f"💾 Cache contains {len(all_items)} items")


def main():
    """Main function to run examples."""
    if len(sys.argv) < 2:
        print("Usage: python example_fastapi_usage.py [basic|full|async]")
        print("  basic - Basic API-only FastAPI app")
        print("  full  - Full FastAPI app with UI")
        print("  async - Demonstrate async operations")
        return
    
    mode = sys.argv[1]
    
    # Set up Windows event loop policy if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Check if RAG-Layer exists
    if not os.path.exists(settings.RAG_LAYER_DIR):
        print(f"❌ RAG-Layer directory not found: {settings.RAG_LAYER_DIR}")
        print("   Run 'python train.py' to train your model first.")
        return
    
    try:
        if mode == "basic":
            asyncio.run(example_basic_api())
        elif mode == "full":
            asyncio.run(example_full_app())
        elif mode == "async":
            asyncio.run(example_async_operations())
        else:
            print(f"❌ Unknown mode: {mode}")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

