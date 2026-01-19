#!/usr/bin/env python3
"""
Project 8 NL2SQL Test Script
Tests the Natural Language to SQL functionality
"""

import requests
import json
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8001"
# You need to get a token first by logging in
# For testing, use: test@example.com / test123
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_schema():
    """Test 1: Get Database Schema"""
    print("\n" + "="*60)
    print("TEST 1: Get Database Schema")
    print("="*60)
    
    response = requests.get(
        f"{API_BASE}/api/nl-to-sql/schema",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Schema Retrieved Successfully")
        print("\n" + data['schema'])
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_generate_sql(question: str):
    """Test 2: Generate SQL without executing"""
    print("\n" + "="*60)
    print(f"TEST 2: Generate SQL Only")
    print("="*60)
    print(f"Question: {question}")
    
    response = requests.post(
        f"{API_BASE}/api/nl-to-sql/generate",
        headers=headers,
        json={"question": question}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ SQL Generated Successfully")
            print(f"\nGenerated SQL:")
            print(f"  {data['sql']}")
        else:
            print(f"❌ Generation Failed: {data.get('error')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return response.json() if response.status_code == 200 else None


def test_execute_nl_query(question: str):
    """Test 3: Execute Natural Language Query"""
    print("\n" + "="*60)
    print(f"TEST 3: Execute Natural Language Query")
    print("="*60)
    print(f"Question: {question}")
    
    response = requests.post(
        f"{API_BASE}/api/nl-to-sql/",
        headers=headers,
        json={"question": question}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Query Executed Successfully")
            print(f"\nGenerated SQL:")
            print(f"  {data['sql']}")
            print(f"\nResults: ({data['row_count']} rows)")
            
            if data['data']:
                # Print first 5 rows
                for i, row in enumerate(data['data'][:5], 1):
                    print(f"  Row {i}: {json.dumps(row, indent=2)}")
                
                if data['row_count'] > 5:
                    print(f"  ... and {data['row_count'] - 5} more rows")
            else:
                print("  (No results)")
        else:
            print(f"❌ Execution Failed: {data.get('error')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_validate_sql(sql: str):
    """Test 4: Validate SQL Query"""
    print("\n" + "="*60)
    print(f"TEST 4: Validate SQL Query")
    print("="*60)
    print(f"SQL: {sql}")
    
    response = requests.post(
        f"{API_BASE}/api/nl-to-sql/validate",
        headers=headers,
        params={"sql": sql}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('is_safe'):
            print("✅ Query is Safe")
            print(f"  Sanitized SQL: {data['sanitized_sql']}")
        else:
            print(f"❌ Query is Unsafe")
            print(f"  Error: {data['error']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_unsafe_query():
    """Test 5: Test Security (should be blocked)"""
    print("\n" + "="*60)
    print(f"TEST 5: Security Test (Should Block Unsafe Queries)")
    print("="*60)
    
    unsafe_questions = [
        "Delete all users from the database",
        "Drop the users table",
        "Update user email to spam@example.com"
    ]
    
    for question in unsafe_questions:
        print(f"\nTesting: {question}")
        response = requests.post(
            f"{API_BASE}/api/nl-to-sql/",
            headers=headers,
            json={"question": question}
        )
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('success'):
                print(f"  ✅ Correctly Blocked: {data.get('error')}")
            else:
                print(f"  ❌ SECURITY ISSUE: Query was allowed!")
        else:
            print(f"  ❌ Error: {response.status_code}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PROJECT 8: NL2SQL - TEST SUITE")
    print("="*60)
    
    # Test 1: Get Schema
    test_schema()
    
    # Test 2: Generate SQL
    test_generate_sql("How many users are in the database?")
    
    # Test 3: Execute queries
    test_execute_nl_query("How many users are in the database?")
    test_execute_nl_query("List all chat threads")
    test_execute_nl_query("Show users created in the last 7 days")
    test_execute_nl_query("Count documents by file type")
    
    # Test 4: Validate SQL
    test_validate_sql("SELECT * FROM users LIMIT 10")
    test_validate_sql("DELETE FROM users")  # Should fail
    
    # Test 5: Security tests
    test_unsafe_query()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    print("\nNOTE: You need to set TOKEN variable with a valid auth token")
    print("To get a token:")
    print("1. Login at http://localhost:3000/login")
    print("2. Use test@example.com / test123")
    print("3. Get token from browser localStorage or API response")
    print("\nOr use the Swagger UI: http://localhost:8001/docs")
    
    # Uncomment to run tests after setting TOKEN
    # run_all_tests()
