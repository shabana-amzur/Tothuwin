"""
Debug authentication issues
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.database import User
from app.utils.auth import verify_password, get_password_hash, create_access_token
import traceback

# Test database connection
print("=" * 60)
print("Testing Database Connection...")
print("=" * 60)
try:
    db = SessionLocal()
    user = db.query(User).filter(User.email == "test@example.com").first()
    if user:
        print(f"✓ User found: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Active: {user.is_active}")
        print(f"  Hashed password length: {len(user.hashed_password) if user.hashed_password else 0}")
    else:
        print("✗ User not found")
    db.close()
except Exception as e:
    print(f"✗ Database error: {e}")
    traceback.print_exc()

# Test password verification
print("\n" + "=" * 60)
print("Testing Password Verification...")
print("=" * 60)
try:
    test_password = "test123"
    if user:
        result = verify_password(test_password, user.hashed_password)
        print(f"Password verification result: {result}")
    else:
        print("Cannot test - user not found")
except Exception as e:
    print(f"✗ Password verification error: {e}")
    traceback.print_exc()

# Test token creation
print("\n" + "=" * 60)
print("Testing Token Creation...")
print("=" * 60)
try:
    if user:
        token = create_access_token(data={"user_id": user.id, "email": user.email})
        print(f"✓ Token created successfully")
        print(f"  Token length: {len(token)}")
        print(f"  Token preview: {token[:50]}...")
    else:
        print("Cannot test - user not found")
except Exception as e:
    print(f"✗ Token creation error: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug Complete")
print("=" * 60)
