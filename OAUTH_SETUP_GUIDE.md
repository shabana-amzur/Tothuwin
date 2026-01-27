# Google OAuth Configuration Guide

## ✅ Current Status
- **Backend**: Running on port 8001
- **Frontend**: Running on port 3000  
- **OAuth Endpoint**: ✅ Working (redirects to Google correctly)

## 🔐 OAuth Configuration

### Client Credentials (Configure in .env file)
- **Client ID**: `YOUR_GOOGLE_CLIENT_ID` (from Google Cloud Console)
- **Client Secret**: `YOUR_GOOGLE_CLIENT_SECRET` (from Google Cloud Console)
- **Redirect URI**: `http://localhost:8001/api/auth/google/callback`

## ⚙️ Google Cloud Console Setup

### IMPORTANT: Add Authorized Redirect URI

1. **Go to Google Cloud Console**:
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. **Select your OAuth 2.0 Client**:
   - Find your client ID in the Google Cloud Console
   - Click to edit

3. **Add Authorized Redirect URI**:
   ```
   http://localhost:8001/api/auth/google/callback
   ```

4. **Also Add (for development)**:
   ```
   http://127.0.0.1:8001/api/auth/google/callback
   ```

5. **Save Changes**

## 🧪 Testing OAuth

### Method 1: From Frontend Login Page
1. Go to: http://localhost:3000/login
2. Click "Sign in with Google"
3. You should be redirected to Google's login page
4. After login, you'll be redirected back with authentication

### Method 2: Direct API Test
```bash
# Open this URL in your browser:
http://localhost:8001/api/auth/google/login
```

### Method 3: From Main Chat
1. Go to: http://localhost:3000
2. If not logged in, click "Sign in with Google"

## 🔍 Troubleshooting

### If OAuth Doesn't Work:

#### 1. "redirect_uri_mismatch" Error
**Problem**: The redirect URI in Google Console doesn't match

**Solution**:
- Check that **EXACT** URI is added: `http://localhost:8001/api/auth/google/callback`
- No trailing slashes
- Correct port (8001)
- Protocol must be `http` (not `https` for local dev)

#### 2. "invalid_client" Error  
**Problem**: Client ID or Secret is wrong

**Solution**:
- Verify credentials in Google Console match `.env` file
- Check for extra spaces or line breaks

#### 3. Backend Not Responding
**Problem**: Backend server crashed or not started

**Solution**:
```powershell
# Restart backend
cd "C:\Users\Shabana\Desktop\Tothu 2\Tothu\backend"
& "C:/Users/Shabana/Desktop/Tothu 2/Tothu/.venv/Scripts/python.exe" -m uvicorn main:app --reload --port 8001
```

#### 4. "Error connecting to OAuth provider"
**Problem**: Network or configuration issue

**Solution**:
- Check internet connection
- Verify Google OAuth API is enabled in Cloud Console
- Check if Google services are accessible

## 📝 OAuth Flow

1. **User clicks "Sign in with Google"**
   - Frontend sends user to: `http://localhost:8001/api/auth/google/login`

2. **Backend redirects to Google**
   - User sees Google login page
   - URL: `https://accounts.google.com/o/oauth2/v2/auth?...`

3. **User logs in with Google**
   - Google authenticates user
   - User authorizes app access

4. **Google redirects back**
   - URL: `http://localhost:8001/api/auth/google/callback?code=...`
   - Backend receives authorization code

5. **Backend processes callback**
   - Exchanges code for user info
   - Creates/finds user in database
   - Generates JWT token

6. **User redirected to frontend**
   - URL: `http://localhost:3000?token=...&email=...&username=...`
   - Frontend saves token to localStorage
   - User is logged in!

## 🔐 Security Notes

- **Local Development**: Using `http://localhost` is acceptable
- **Production**: Must use `https://` URLs
- **Secrets**: Never commit `.env` file to git
- **Token Expiry**: JWT tokens expire after 1440 minutes (24 hours)

## ✅ Verification Checklist

- [x] Backend running on port 8001
- [x] OAuth endpoint responding with 302 redirect
- [x] Redirect points to Google OAuth (`accounts.google.com`)
- [ ] Authorized redirect URI added in Google Console
- [ ] OAuth tested from login page

## 📞 Need Help?

If OAuth still doesn't work after adding the redirect URI:

1. **Check Browser Console** (F12) for errors
2. **Check Backend Logs** in the PowerShell window
3. **Verify Google Console Settings**:
   - APIs enabled: "Google+ API" or "Google People API"
   - OAuth consent screen configured
   - Test users added (if in testing mode)

## 🎯 Quick Fix Command

If you need to restart both servers:

```powershell
# Stop all
Get-Process | Where-Object {$_.ProcessName -match "python|node"} | Stop-Process -Force

# Start backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Shabana\Desktop\Tothu 2\Tothu\backend'; python -m uvicorn main:app --reload --port 8001"

# Start frontend  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Shabana\Desktop\Tothu 2\Tothu\frontend'; npm run dev"
```

---

**The OAuth system is working correctly!** The only remaining step is to ensure the redirect URI is added in Google Cloud Console.
