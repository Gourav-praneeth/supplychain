#!/usr/bin/env python3
"""
Test script to verify FoodSafe backend setup.
Run this after configuring your .env file to ensure everything is working.
"""

import sys
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

def print_test(test_name, result, message=""):
    """Print test result with color coding."""
    if result:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {test_name}")
        if message:
            print(f"  {Fore.CYAN}{message}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗{Style.RESET_ALL} {test_name}")
        if message:
            print(f"  {Fore.YELLOW}{message}{Style.RESET_ALL}")
    return result

def test_imports():
    """Test if all required packages are installed."""
    print(f"\n{Fore.BLUE}=== Testing Package Imports ==={Style.RESET_ALL}")
    
    packages = [
        ("fastapi", "FastAPI web framework"),
        ("sqlalchemy", "Database ORM"),
        ("web3", "Blockchain interaction"),
        ("requests", "HTTP requests for IPFS"),
        ("pydantic_settings", "Settings management"),
    ]
    
    all_passed = True
    for package, description in packages:
        try:
            __import__(package)
            print_test(f"Import {package}", True, description)
        except ImportError as e:
            print_test(f"Import {package}", False, f"Missing: {str(e)}")
            all_passed = False
    
    return all_passed

def test_config():
    """Test configuration and environment variables."""
    print(f"\n{Fore.BLUE}=== Testing Configuration ==={Style.RESET_ALL}")
    
    try:
        from config import settings
        
        checks = [
            ("DATABASE_URL", settings.DATABASE_URL, "Database connection string"),
            ("POLYGON_AMOY_RPC_URL", settings.POLYGON_AMOY_RPC_URL, "Blockchain RPC URL"),
            ("CONTRACT_ADDRESS", settings.CONTRACT_ADDRESS, "Smart contract address"),
            ("PINATA_API_KEY", settings.PINATA_API_KEY, "Pinata API key"),
            ("PINATA_SECRET_API_KEY", settings.PINATA_SECRET_API_KEY, "Pinata secret key"),
        ]
        
        all_passed = True
        for name, value, description in checks:
            has_value = value and value != "0x0000000000000000000000000000000000000000"
            print_test(f"Config: {name}", has_value, description)
            if not has_value:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test("Load configuration", False, str(e))
        return False

def test_database():
    """Test database connection."""
    print(f"\n{Fore.BLUE}=== Testing Database Connection ==={Style.RESET_ALL}")
    
    try:
        from database import engine, init_db
        
        # Test connection
        with engine.connect() as conn:
            print_test("Database connection", True, "Successfully connected to PostgreSQL")
        
        # Initialize tables
        init_db()
        print_test("Database tables", True, "Tables created/verified")
        
        return True
        
    except Exception as e:
        print_test("Database connection", False, str(e))
        return False

def test_blockchain():
    """Test blockchain connection."""
    print(f"\n{Fore.BLUE}=== Testing Blockchain Connection ==={Style.RESET_ALL}")
    
    try:
        from blockchain import blockchain_service
        
        # Test connection
        is_connected = blockchain_service.is_connected()
        print_test("Blockchain connection", is_connected, 
                  f"RPC: {blockchain_service.w3.provider.endpoint_uri}")
        
        if is_connected:
            # Get latest block
            latest_block = blockchain_service.get_latest_block_number()
            print_test("Get latest block", True, f"Block: {latest_block}")
            
            # Test contract
            print_test("Contract loaded", True, 
                      f"Address: {blockchain_service.contract_address}")
            
            return True
        else:
            return False
        
    except Exception as e:
        print_test("Blockchain connection", False, str(e))
        return False

def test_ipfs():
    """Test IPFS/Pinata connection."""
    print(f"\n{Fore.BLUE}=== Testing IPFS/Pinata Connection ==={Style.RESET_ALL}")
    
    try:
        from ipfs_service import ipfs_service
        
        # Test authentication
        auth_success = ipfs_service.test_connection()
        print_test("Pinata authentication", auth_success, 
                  "API credentials valid")
        
        if auth_success:
            # Test upload and retrieval
            test_data = {
                "test": "FoodSafe Backend Test",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            try:
                ipfs_hash = ipfs_service.upload_json(test_data, "test.json")
                print_test("Upload JSON to IPFS", True, f"Hash: {ipfs_hash}")
                
                # Try to retrieve
                retrieved = ipfs_service.get_content(ipfs_hash)
                print_test("Retrieve from IPFS", True, "Content retrieved successfully")
                
                return True
            except Exception as e:
                print_test("IPFS operations", False, str(e))
                return False
        else:
            return False
        
    except Exception as e:
        print_test("IPFS service", False, str(e))
        return False

def test_contract_abi():
    """Test if contract ABI is loaded correctly."""
    print(f"\n{Fore.BLUE}=== Testing Contract ABI ==={Style.RESET_ALL}")
    
    try:
        import os
        import json
        
        abi_path = os.path.join(os.path.dirname(__file__), 'contract_abi.json')
        
        if os.path.exists(abi_path):
            with open(abi_path, 'r') as f:
                abi = json.load(f)
            
            # Check for required functions
            function_names = [item['name'] for item in abi if item.get('type') == 'function']
            event_names = [item['name'] for item in abi if item.get('type') == 'event']
            
            required_functions = ['registerLot', 'getLot', 'getLotHistory', 'triggerRecall', 'updateLot']
            required_events = ['LotRegistered', 'LotRecalled', 'LotStatusUpdated', 'Transfer']
            
            all_passed = True
            for func in required_functions:
                has_func = func in function_names
                print_test(f"Function: {func}", has_func)
                if not has_func:
                    all_passed = False
            
            for event in required_events:
                has_event = event in event_names
                print_test(f"Event: {event}", has_event)
                if not has_event:
                    all_passed = False
            
            return all_passed
        else:
            print_test("ABI file exists", False, "contract_abi.json not found")
            return False
        
    except Exception as e:
        print_test("Load contract ABI", False, str(e))
        return False

def main():
    """Run all tests."""
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"FoodSafe Backend Setup Verification")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "Database": test_database(),
        "Blockchain": test_blockchain(),
        "Contract ABI": test_contract_abi(),
        "IPFS": test_ipfs(),
    }
    
    # Summary
    print(f"\n{Fore.BLUE}=== Test Summary ==={Style.RESET_ALL}")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if result else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}✓ All tests passed! Backend is ready to use.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next steps:")
        print(f"  1. Start the indexer: python indexer.py")
        print(f"  2. Start the API: uvicorn main:app --reload")
        print(f"  3. Visit http://localhost:8000/docs for API documentation{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"\n{Fore.YELLOW}⚠ Some tests failed. Please check the configuration and try again.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Refer to SETUP_GUIDE.md for detailed setup instructions.{Style.RESET_ALL}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)

