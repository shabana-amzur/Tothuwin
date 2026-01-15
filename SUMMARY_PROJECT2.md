# PROJECT 2: DATABASE & AUTHENTICATION

## ✅ Implementation Complete

### 🔐 Features Added
- **User Authentication**: Login and Registration (JWT based).
- **Database Integration**: SQLite database for local development.
- **Chat Persistence**: Chat history is now saved to the database.
- **Protected Routes**: Chat interface requires login.

---

## 📁 New Structure

```
Tothu/
├── backend/
│   ├── sql_app.db             # SQLite Database
│   ├── app/
│   │   ├── api/
│   │   │   └── auth.py        # Auth endpoints
│   │   ├── models/
│   │   │   ├── database.py    # DB Models (User, ChatHistory)
│   │   │   └── user.py        # Pydantic Models for Auth
│   │   └── ...
│
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   │   └── page.tsx       # Login Page
│   │   ├── register/
│   │   │   └── page.tsx       # Register Page
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx # Authentication State
│   │   └── ...
```

---

## 🚀 How to Run

### 1. Backend (Port 8001)

```bash
cd backend
# Database is already initialized (sql_app.db)
# Start server
uvicorn main:app --reload --port 8001
```

### 2. Frontend (Port 3000)

```bash
cd frontend
npm run dev
```

---

## 🧪 Testing

1. Go to `http://localhost:3000` -> redirects to Login.
2. Click "create a new account".
3. Register a new user.
4. You will be redirected to the Chat interface.
5. Send a message.
6. Refresh page -> You stay logged in (JWT in localStorage).
7. Check backend logs -> "Chat history saved for user ...".

