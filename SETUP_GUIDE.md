# 🚀 Quick Setup Guide - Projects 3, 4, 5

## ⚡ Quick Start

### 1. Install Dependencies

#### Backend
```bash
cd /Users/ferozshaik/Desktop/Tothu
pip install authlib==1.3.2 itsdangerous==2.2.0
```

#### Frontend
```bash
cd /Users/ferozshaik/Desktop/Tothu/frontend
npm install
```

### 2. Setup Google OAuth (Optional)

If you want to use Google Sign-in:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Create/Select Project**

3. **Enable Google+ API**:
   - APIs & Services → Library
   - Search "Google+ API"
   - Enable it

4. **Create OAuth 2.0 Credentials**:
   - APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: **Web application**
   - Name: "Tothu Chat App"
   - Authorized redirect URIs: `http://localhost:8001/api/auth/google/callback`
   - Click "Create"

5. **Update .env file**:
```env
GOOGLE_CLIENT_ID=your_client_id_from_google
GOOGLE_CLIENT_SECRET=your_client_secret_from_google
```

### 3. Restart Servers

#### Terminal 1 - Backend
```bash
cd /Users/ferozshaik/Desktop/Tothu/backend
/Users/ferozshaik/Desktop/Tothu/venv/bin/python -m uvicorn main:app --reload --port 8001
```

#### Terminal 2 - Frontend
```bash
cd /Users/ferozshaik/Desktop/Tothu/frontend
npm run dev
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## ✨ New Features to Test

### 1. Chat Threads
- Click **"+ New Chat"** to start new conversation
- First message auto-generates thread title
- See all threads in left sidebar
- Click thread to load previous messages
- Delete threads with trash icon

### 2. Conversation Memory
- Ask a question
- Then ask: "What did I just ask?"
- AI remembers last 5 messages automatically
- Each thread has its own memory

### 3. Rich Content
Try these prompts to test markdown rendering:

**Code Example:**
```
Show me a Python function with proper formatting
```

**Math Formula:**
```
Explain the quadratic formula with LaTeX notation
```

**Table:**
```
Create a comparison table of Python vs JavaScript
```

**Combined:**
```
Show me a table comparing sorting algorithms with code examples and time complexity formulas
```

### 4. Google Login
- Click **"Sign in with Google"** on login page
- Authorize with your Google account
- Automatically logged in
- No password needed for future logins

## 📊 API Endpoints

### New Thread Endpoints
- `POST /api/threads` - Create thread
- `GET /api/threads` - List all threads
- `GET /api/threads/{id}` - Get thread with messages
- `PUT /api/threads/{id}` - Update thread title
- `DELETE /api/threads/{id}` - Delete thread

### OAuth Endpoints
- `GET /api/auth/google/login` - Start Google OAuth
- `GET /api/auth/google/callback` - OAuth callback

### Updated Chat Endpoint
- `POST /api/chat` - Send message (now supports `thread_id`)

## 🎨 UI Changes

- **Dark Theme**: Modern dark interface
- **Thread Sidebar**: Left navigation with thread list
- **Rich Message Display**: Markdown rendering for AI responses
- **Improved Layout**: Better spacing and organization

## 🔍 Troubleshooting

### Google OAuth Not Working
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
- Verify redirect URI in Google Console matches: `http://localhost:8001/api/auth/google/callback`
- Make sure Google+ API is enabled

### Threads Not Loading
- Check backend is running on port 8001
- Open browser console for errors
- Verify authentication token is valid

### Markdown Not Rendering
- Check that npm packages installed: `react-markdown`, `remark-gfm`, etc.
- Clear browser cache
- Check browser console for errors

### Memory Not Working
- Make sure messages are associated with thread_id
- Check database: ChatHistory should have thread_id column
- Verify conversation_history is passed to chat service

## 📝 Example Markdown to Test

Copy and send this to AI to see rich rendering:

```markdown
# Python Quick Reference

## Code Example
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## Math Formula
The Pythagorean theorem: $a^2 + b^2 = c^2$

## Table
| Algorithm | Time Complexity |
|-----------|----------------|
| Bubble Sort | $O(n^2)$ |
| Quick Sort | $O(n \log n)$ |

> Note: These are average case complexities
```

## 🎯 Testing Checklist

- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can create new account
- [ ] Can login with username/password
- [ ] Can see Google Sign-in button
- [ ] Can create new thread
- [ ] Thread auto-named correctly
- [ ] Can see thread list in sidebar
- [ ] Can click thread to load messages
- [ ] Can delete thread
- [ ] Conversation memory works
- [ ] Code blocks render with highlighting
- [ ] Math formulas render correctly
- [ ] Tables display properly
- [ ] Images can be embedded
- [ ] Dark theme looks good

## 📚 Documentation

For detailed information, see:
- `README_PROJECTS_3_4_5.md` - Complete implementation details
- `README_PROJECT1.md` - Basic chatbot setup
- `README_PROJECT2.md` - Database and authentication

## 🎉 Ready to Go!

The application now includes:
✅ Google OAuth login
✅ Chat thread organization
✅ AI-powered thread naming
✅ 5-message conversation memory
✅ Rich markdown rendering
✅ Code syntax highlighting
✅ Math formula support
✅ Table rendering
✅ Dark theme UI

Enjoy your enhanced AI chat experience! 🚀
