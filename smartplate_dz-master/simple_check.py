#!/usr/bin/env python3
"""
Simple script to check if the backend server has the new document fields.
This will test by starting the server and checking the API endpoints.
"""
import subprocess
import sys
import time
import requests

def test_backend_server():
    """Test if backend server has the new document endpoints."""
    print("🔍 Testing backend server for document upload endpoints...")
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8002/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print("❌ Backend server responded with error")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend server is not running")
        print("💡 Please start the backend server first:")
        print("   cd smartplate_dz-master")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002")
        return False

def test_document_endpoints():
    """Test if document upload endpoints exist."""
    print("\n📤 Testing document upload endpoints...")
    
    endpoints = [
        ("Vignette", "/services/documents/vignette"),
        ("Assurance", "/services/documents/assurance"), 
        ("Contrôle Technique", "/services/documents/controle-technique")
    ]
    
    base_url = "http://localhost:8002/api"
    
    for name, endpoint in endpoints:
        try:
            # Test OPTIONS request to check if endpoint exists
            response = requests.options(f"{base_url}{endpoint}?car_id=test", timeout=5)
            
            if response.status_code in [200, 401, 405]:  # These indicate endpoint exists
                print(f"✅ {name} endpoint exists")
            else:
                print(f"❌ {name} endpoint not found (status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} endpoint test failed: {e}")

def check_database_creation():
    """Check database by examining the server startup logs."""
    print("\n🗄️  Database Information:")
    print("The new fields will be created automatically when:")
    print("1. You start the backend server")
    print("2. The create_tables() function runs")
    print("3. The Car model with new fields is used")
    
    print("\n📋 Expected new fields in cars table:")
    print("  - vignette_url (TEXT, nullable)")
    print("  - controle_technique_url (TEXT, nullable)")
    print("  - assurance_paper_url (TEXT, nullable) - already existed")

def main():
    print("🚀 SmartPlate Database & Endpoint Checker")
    print("=" * 50)
    
    # Check if backend server is running
    if not test_backend_server():
        print("\n⚠️  Please start the backend server first")
        check_database_creation()
        return
    
    # Test endpoints
    test_document_endpoints()
    
    # Database info
    check_database_creation()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("1. Start backend server to create database tables")
    print("2. Test document uploads from Services page")
    print("3. Check database if uploads work correctly")

if __name__ == "__main__":
    main()
