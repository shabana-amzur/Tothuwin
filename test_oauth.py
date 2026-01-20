import sys
sys.path.insert(0, 'backend')

from app.config import get_settings

settings = get_settings()

print("=== OAuth Configuration Check ===")
print(f"GOOGLE_CLIENT_ID: {settings.GOOGLE_CLIENT_ID}")
print(f"GOOGLE_CLIENT_SECRET: {settings.GOOGLE_CLIENT_SECRET}")
print(f"BACKEND_URL: {settings.BACKEND_URL}")
print(f"FRONTEND_URL: {settings.FRONTEND_URL}")

# Test if OAuth initialization works
try:
    from starlette.config import Config
    from authlib.integrations.starlette_client import OAuth
    
    config = Config(environ={
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    })
    
    oauth = OAuth(config)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    print("\n✅ OAuth initialization successful!")
    print(f"OAuth google client registered: {hasattr(oauth, 'google')}")
    
except Exception as e:
    print(f"\n❌ OAuth initialization failed: {e}")
    import traceback
    traceback.print_exc()
