#!/usr/bin/env python3
"""
Test script to verify the plotly endpoint fix.
"""

import requests
import json


def test_plotly_endpoint():
    """Test the plotly figure generation endpoint."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Plotly Endpoint Fix")
    print("=" * 40)
    
    try:
        # Step 1: Generate SQL
        print("📝 Step 1: Generating SQL...")
        question = "What are the different types of punishments in discipline data?"
        
        gen_response = requests.get(
            f"{base_url}/api/v0/generate_sql",
            params={"question": question},
            timeout=30
        )
        
        if gen_response.status_code != 200:
            print(f"❌ Failed to generate SQL: {gen_response.status_code}")
            print(f"Response: {gen_response.text}")
            return
            
        gen_data = gen_response.json()
        query_id = gen_data.get("id")
        generated_sql = gen_data.get("text")
        
        print(f"✅ Generated SQL: {generated_sql}")
        print(f"🆔 Query ID: {query_id}")
        
        # Step 2: Execute SQL
        print("\n🔄 Step 2: Executing SQL...")
        exec_response = requests.get(
            f"{base_url}/api/v0/run_sql",
            params={"id": query_id},
            timeout=60
        )
        
        if exec_response.status_code != 200:
            print(f"❌ Failed to execute SQL: {exec_response.status_code}")
            print(f"Response: {exec_response.text}")
            return
            
        exec_data = exec_response.json()
        
        if exec_data.get("type") != "df":
            print(f"❌ SQL execution failed: {exec_data.get('error', 'Unknown error')}")
            return
            
        print("✅ SQL executed successfully!")
        print(f"📊 Should generate chart: {exec_data.get('should_generate_chart')}")
        
        # Step 3: Generate Plotly Figure (this was failing with 422 before)
        print("\n📈 Step 3: Generating Plotly figure...")
        plotly_response = requests.get(
            f"{base_url}/api/v0/generate_plotly_figure",
            params={"id": query_id},
            timeout=60
        )
        
        print(f"📋 Plotly response status: {plotly_response.status_code}")
        
        if plotly_response.status_code == 200:
            plotly_data = plotly_response.json()
            print("✅ Plotly figure generated successfully!")
            print(f"📊 Response type: {plotly_data.get('type')}")
            
            # Check if we got a valid figure
            if plotly_data.get("fig"):
                fig_data = json.loads(plotly_data["fig"])
                print(f"📈 Figure has {len(fig_data.get('data', []))} data series")
                print(f"🎨 Chart type: {fig_data.get('data', [{}])[0].get('type', 'unknown') if fig_data.get('data') else 'none'}")
            else:
                print("⚠️ No figure data in response")
                
        elif plotly_response.status_code == 422:
            print("❌ Still getting 422 Unprocessable Entity error!")
            print(f"Response: {plotly_response.text}")
            
            # Try to get more details about the error
            try:
                error_detail = plotly_response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print("Could not parse error response as JSON")
                
        else:
            print(f"❌ Unexpected status code: {plotly_response.status_code}")
            print(f"Response: {plotly_response.text}")
        
        # Step 4: Test other endpoints that were fixed
        print("\n🔍 Step 4: Testing other fixed endpoints...")
        
        # Test download CSV
        print("📄 Testing CSV download...")
        csv_response = requests.get(
            f"{base_url}/api/v0/download_csv",
            params={"id": query_id},
            timeout=30
        )
        print(f"📋 CSV download status: {csv_response.status_code}")
        
        # Test followup questions
        print("❓ Testing followup questions...")
        followup_response = requests.get(
            f"{base_url}/api/v0/generate_followup_questions",
            params={"id": query_id},
            timeout=30
        )
        print(f"📋 Followup questions status: {followup_response.status_code}")
        
        # Test summary generation
        print("📝 Testing summary generation...")
        summary_response = requests.get(
            f"{base_url}/api/v0/generate_summary",
            params={"id": query_id},
            timeout=30
        )
        print(f"📋 Summary generation status: {summary_response.status_code}")
        
        print("\n🎉 All endpoint tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_plotly_endpoint()
