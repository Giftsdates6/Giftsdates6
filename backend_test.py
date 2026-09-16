"""
Backend API Testing for GiftsDates - Withdrawal Gating and Payout Document Flow
Tests the complete flow of user registration, payout account setup, document upload, and withdrawal attempts.
"""

import requests
import io
from PIL import Image
import json
import uuid

# Base URL from frontend/.env
BASE_URL = "https://gifts-login-store.preview.emergentagent.com/api"

# Test data
test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
test_password = "SecurePass123!"
test_user_data = {
    "email": test_email,
    "password": test_password,
    "name": "Ahmed Al-Rashid",
    "age": 30,
    "gender": "male",
    "interested_in": "female",
    "city": "Dubai",
    "country": "United Arab Emirates"
}

# Global variables to store test state
auth_token = None
user_id = None
bank_statement_path = None
proof_of_address_path = None

def create_dummy_image():
    """Create a small dummy PNG image for testing"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def print_test_result(test_name, passed, status_code=None, detail=None, response_data=None):
    """Print formatted test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if status_code:
        print(f"  HTTP Status: {status_code}")
    if detail:
        print(f"  Detail: {detail}")
    if response_data and not passed:
        print(f"  Response: {json.dumps(response_data, indent=2)}")

def test_1_register():
    """Test 1: POST /api/auth/register - User registration"""
    global auth_token, user_id
    
    print("\n" + "="*80)
    print("TEST 1: User Registration")
    print("="*80)
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                auth_token = data["token"]
                user_id = data["user"]["id"]
                print_test_result(
                    "User Registration",
                    True,
                    response.status_code,
                    f"Successfully registered user: {test_user_data['name']}"
                )
                print(f"  Token: {auth_token[:20]}...")
                print(f"  User ID: {user_id}")
                return True
            else:
                print_test_result(
                    "User Registration",
                    False,
                    response.status_code,
                    "Response missing 'token' or 'user' field",
                    data
                )
                return False
        else:
            print_test_result(
                "User Registration",
                False,
                response.status_code,
                response.json().get("detail", "Unknown error"),
                response.json()
            )
            return False
            
    except Exception as e:
        print_test_result("User Registration", False, detail=f"Exception: {str(e)}")
        return False

def test_2_payout_without_documents():
    """Test 2: POST /api/wallet/payout-account WITHOUT documents - Should fail with 400"""
    global auth_token
    
    print("\n" + "="*80)
    print("TEST 2: Payout Account Creation WITHOUT Documents")
    print("="*80)
    
    if not auth_token:
        print_test_result("Payout without documents", False, detail="No auth token available")
        return False
    
    payout_data = {
        "tax_id": "AE123456789",
        "holder_name": "Ahmed Al-Rashid",
        "recipient_street": "Sheikh Zayed Road, Building 42",
        "recipient_city": "Dubai",
        "recipient_province": "Dubai",
        "recipient_postal_code": "12345",
        "country": "United Arab Emirates",
        "recipient_email": "ahmed.rashid@example.com",
        "iban": "DE89370400440532013000",
        "swift": "COBADEFFXXX",
        "bank_name": "Emirates NBD",
        "bank_street": "Baniyas Road",
        "bank_city": "Dubai",
        "bank_province": "Dubai",
        "bank_postal_code": "12345",
        "bank_country": "United Arab Emirates"
        # Intentionally OMITTING bank_statement_path and proof_of_address_path
    }
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/wallet/payout-account", json=payout_data, headers=headers, timeout=10)
        
        if response.status_code == 400:
            detail = response.json().get("detail", "")
            if detail == "BANK_STATEMENT_REQUIRED":
                print_test_result(
                    "Payout without documents",
                    True,
                    response.status_code,
                    f"Correctly rejected with: {detail}"
                )
                return True
            else:
                print_test_result(
                    "Payout without documents",
                    False,
                    response.status_code,
                    f"Expected 'BANK_STATEMENT_REQUIRED' but got: {detail}",
                    response.json()
                )
                return False
        else:
            print_test_result(
                "Payout without documents",
                False,
                response.status_code,
                f"Expected 400 status but got {response.status_code}",
                response.json()
            )
            return False
            
    except Exception as e:
        print_test_result("Payout without documents", False, detail=f"Exception: {str(e)}")
        return False

def test_3_upload_documents():
    """Test 3: POST /api/wallet/payout-document - Upload bank statement and proof of address"""
    global auth_token, bank_statement_path, proof_of_address_path
    
    print("\n" + "="*80)
    print("TEST 3: Document Upload")
    print("="*80)
    
    if not auth_token:
        print_test_result("Document upload", False, detail="No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 3a: Upload bank statement
    print("\n--- Test 3a: Upload bank_statement ---")
    try:
        img_bytes = create_dummy_image()
        files = {'file': ('bank_statement.png', img_bytes, 'image/png')}
        response = requests.post(
            f"{BASE_URL}/wallet/payout-document?kind=bank_statement",
            files=files,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "path" in data:
                bank_statement_path = data["path"]
                print_test_result(
                    "Upload bank_statement",
                    True,
                    response.status_code,
                    f"Successfully uploaded: {bank_statement_path}"
                )
            else:
                print_test_result(
                    "Upload bank_statement",
                    False,
                    response.status_code,
                    "Response missing 'path' field",
                    data
                )
                return False
        else:
            print_test_result(
                "Upload bank_statement",
                False,
                response.status_code,
                response.json().get("detail", "Unknown error"),
                response.json()
            )
            return False
    except Exception as e:
        print_test_result("Upload bank_statement", False, detail=f"Exception: {str(e)}")
        return False
    
    # Test 3b: Upload proof of address
    print("\n--- Test 3b: Upload proof_of_address ---")
    try:
        img_bytes = create_dummy_image()
        files = {'file': ('proof_of_address.png', img_bytes, 'image/png')}
        response = requests.post(
            f"{BASE_URL}/wallet/payout-document?kind=proof_of_address",
            files=files,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "path" in data:
                proof_of_address_path = data["path"]
                print_test_result(
                    "Upload proof_of_address",
                    True,
                    response.status_code,
                    f"Successfully uploaded: {proof_of_address_path}"
                )
            else:
                print_test_result(
                    "Upload proof_of_address",
                    False,
                    response.status_code,
                    "Response missing 'path' field",
                    data
                )
                return False
        else:
            print_test_result(
                "Upload proof_of_address",
                False,
                response.status_code,
                response.json().get("detail", "Unknown error"),
                response.json()
            )
            return False
    except Exception as e:
        print_test_result("Upload proof_of_address", False, detail=f"Exception: {str(e)}")
        return False
    
    # Test 3c: Upload with invalid kind
    print("\n--- Test 3c: Upload with invalid kind (should fail) ---")
    try:
        img_bytes = create_dummy_image()
        files = {'file': ('invalid.png', img_bytes, 'image/png')}
        response = requests.post(
            f"{BASE_URL}/wallet/payout-document?kind=foo",
            files=files,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 400:
            print_test_result(
                "Upload with invalid kind",
                True,
                response.status_code,
                "Correctly rejected invalid kind"
            )
        else:
            print_test_result(
                "Upload with invalid kind",
                False,
                response.status_code,
                f"Expected 400 but got {response.status_code}",
                response.json()
            )
            return False
    except Exception as e:
        print_test_result("Upload with invalid kind", False, detail=f"Exception: {str(e)}")
        return False
    
    return bank_statement_path is not None and proof_of_address_path is not None

def test_4_payout_with_documents():
    """Test 4: POST /api/wallet/payout-account WITH documents - Should succeed"""
    global auth_token, bank_statement_path, proof_of_address_path
    
    print("\n" + "="*80)
    print("TEST 4: Payout Account Creation WITH Documents")
    print("="*80)
    
    if not auth_token:
        print_test_result("Payout with documents", False, detail="No auth token available")
        return False
    
    if not bank_statement_path or not proof_of_address_path:
        print_test_result("Payout with documents", False, detail="Documents not uploaded")
        return False
    
    payout_data = {
        "tax_id": "AE123456789",
        "holder_name": "Ahmed Al-Rashid",
        "recipient_street": "Sheikh Zayed Road, Building 42",
        "recipient_city": "Dubai",
        "recipient_province": "Dubai",
        "recipient_postal_code": "12345",
        "country": "United Arab Emirates",
        "recipient_email": "ahmed.rashid@example.com",
        "iban": "DE89370400440532013000",
        "swift": "COBADEFFXXX",
        "bank_name": "Emirates NBD",
        "bank_street": "Baniyas Road",
        "bank_city": "Dubai",
        "bank_province": "Dubai",
        "bank_postal_code": "12345",
        "bank_country": "United Arab Emirates",
        "bank_statement_path": bank_statement_path,
        "proof_of_address_path": proof_of_address_path
    }
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/wallet/payout-account", json=payout_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "pending":
                print_test_result(
                    "Payout with documents",
                    True,
                    response.status_code,
                    f"Successfully created payout account with status: {data['status']}"
                )
                print(f"  Holder: {data.get('holder_name')}")
                print(f"  Bank: {data.get('bank_name')}")
                print(f"  IBAN: {data.get('iban')}")
                return True
            else:
                print_test_result(
                    "Payout with documents",
                    False,
                    response.status_code,
                    f"Expected status 'pending' but got: {data.get('status')}",
                    data
                )
                return False
        else:
            print_test_result(
                "Payout with documents",
                False,
                response.status_code,
                response.json().get("detail", "Unknown error"),
                response.json()
            )
            return False
            
    except Exception as e:
        print_test_result("Payout with documents", False, detail=f"Exception: {str(e)}")
        return False

def test_5_withdraw_non_verified():
    """Test 5: POST /api/wallet/withdraw - Non-verified user should get IDENTITY_NOT_VERIFIED"""
    global auth_token
    
    print("\n" + "="*80)
    print("TEST 5: Withdrawal Attempt by Non-Verified User")
    print("="*80)
    
    if not auth_token:
        print_test_result("Withdraw non-verified", False, detail="No auth token available")
        return False
    
    withdraw_data = {
        "amount": 1000
    }
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/wallet/withdraw", json=withdraw_data, headers=headers, timeout=10)
        
        if response.status_code == 400:
            detail = response.json().get("detail", "")
            if detail == "IDENTITY_NOT_VERIFIED":
                print_test_result(
                    "Withdraw non-verified",
                    True,
                    response.status_code,
                    f"Correctly rejected with: {detail}"
                )
                print("  ✓ Identity verification check happens before balance check")
                return True
            else:
                print_test_result(
                    "Withdraw non-verified",
                    False,
                    response.status_code,
                    f"Expected 'IDENTITY_NOT_VERIFIED' but got: {detail}",
                    response.json()
                )
                return False
        else:
            print_test_result(
                "Withdraw non-verified",
                False,
                response.status_code,
                f"Expected 400 status but got {response.status_code}",
                response.json()
            )
            return False
            
    except Exception as e:
        print_test_result("Withdraw non-verified", False, detail=f"Exception: {str(e)}")
        return False

def test_6_get_wallet():
    """Test 6: GET /api/wallet - Verify wallet data"""
    global auth_token
    
    print("\n" + "="*80)
    print("TEST 6: Get Wallet Information")
    print("="*80)
    
    if not auth_token:
        print_test_result("Get wallet", False, detail="No auth token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/wallet", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["coins", "withdrawable", "payout_account"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print_test_result(
                    "Get wallet",
                    False,
                    response.status_code,
                    f"Missing fields: {', '.join(missing_fields)}",
                    data
                )
                return False
            
            # Check payout_account status
            payout_account = data.get("payout_account")
            if payout_account and payout_account.get("status") == "pending":
                print_test_result(
                    "Get wallet",
                    True,
                    response.status_code,
                    "Successfully retrieved wallet data"
                )
                print(f"  Coins: {data.get('coins')}")
                print(f"  Withdrawable: {data.get('withdrawable')}")
                print(f"  Escrow: {data.get('escrow')}")
                print(f"  Payout Account Status: {payout_account.get('status')}")
                return True
            else:
                print_test_result(
                    "Get wallet",
                    False,
                    response.status_code,
                    f"Payout account status is not 'pending': {payout_account.get('status') if payout_account else 'None'}",
                    data
                )
                return False
        else:
            print_test_result(
                "Get wallet",
                False,
                response.status_code,
                response.json().get("detail", "Unknown error"),
                response.json()
            )
            return False
            
    except Exception as e:
        print_test_result("Get wallet", False, detail=f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*80)
    print("GIFTSDATES BACKEND API TESTING")
    print("Withdrawal Gating and Payout Document Flow")
    print("="*80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test User: {test_email}")
    
    results = {}
    
    # Run tests in order
    results["Test 1: User Registration"] = test_1_register()
    results["Test 2: Payout without documents"] = test_2_payout_without_documents()
    results["Test 3: Document upload"] = test_3_upload_documents()
    results["Test 4: Payout with documents"] = test_4_payout_with_documents()
    results["Test 5: Withdraw non-verified"] = test_5_withdraw_non_verified()
    results["Test 6: Get wallet"] = test_6_get_wallet()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(run_all_tests())
