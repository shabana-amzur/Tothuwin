# Project 8: NL2SQL - Quick Start Guide

## 🚀 Testing the API

### Option 1: Using Swagger UI (Recommended)

1. **Start the backend server** (already running on port 8001)

2. **Go to Swagger UI**: http://localhost:8001/docs

3. **Authenticate**:
   - Click the "Authorize" button (top right)
   - Login to get a token:
     - Email: `test@example.com`
     - Password: `test123`
   - Enter: `Bearer YOUR_TOKEN`

4. **Try the endpoints**:
   - Expand `/api/nl-to-sql/` section
   - Click "Try it out"
   - Enter a question
   - Click "Execute"

### Option 2: Using curl

```bash
# 1. Login to get token
TOKEN=$(curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.token')

# 2. Get database schema
curl -X GET http://localhost:8001/api/nl-to-sql/schema \
  -H "Authorization: Bearer $TOKEN"

# 3. Execute natural language query
curl -X POST http://localhost:8001/api/nl-to-sql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "How many users are in the database?"}'

# 4. Generate SQL without executing
curl -X POST http://localhost:8001/api/nl-to-sql/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "List all users created this month"}'

# 5. Validate SQL query
curl -X POST "http://localhost:8001/api/nl-to-sql/validate?sql=SELECT%20*%20FROM%20users" \
  -H "Authorization: Bearer $TOKEN"
```

### Option 3: Using Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8001/api/auth/login",
    json={"email": "test@example.com", "password": "test123"}
)
token = response.json()["token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Ask natural language question
response = requests.post(
    "http://localhost:8001/api/nl-to-sql/",
    headers=headers,
    json={"question": "How many users are in the database?"}
)

result = response.json()
print(f"SQL: {result['sql']}")
print(f"Results: {result['data']}")
```

---

## 📝 Example Questions to Try

### Basic Queries
```
- "How many users are in the database?"
- "List all chat threads"
- "Show me the first 10 users"
- "Count how many documents we have"
```

### With Filters
```
- "Show users created in 2024"
- "List threads created in the last 7 days"
- "Find users with gmail addresses"
```

### Aggregations
```
- "Count documents by file type"
- "Show total messages per user"
- "Calculate average messages per thread"
```

### JOINs
```
- "Show users with their thread count"
- "List threads with message counts"
- "Show documents grouped by user"
```

---

## 🔒 Security Examples

### ✅ Allowed (SELECT queries)
```
SELECT * FROM users
SELECT COUNT(*) FROM chat_threads
SELECT email, created_at FROM users WHERE created_at > '2024-01-01'
```

### ❌ Blocked (Write operations)
```
DELETE FROM users
UPDATE users SET email = 'hacker@evil.com'
DROP TABLE users
INSERT INTO users VALUES (...)
```

---

## 📊 Current Database Schema

Based on your SQLite database (`sql_app.db`):

### Tables:
1. **users**
   - id (INTEGER, PRIMARY KEY)
   - email (VARCHAR, NOT NULL)
   - username (VARCHAR)
   - full_name (VARCHAR)
   - hashed_password (VARCHAR)
   - google_id (VARCHAR)
   - is_active (BOOLEAN)
   - role (VARCHAR)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

2. **chat_threads**
   - id (INTEGER, PRIMARY KEY)
   - user_id (INTEGER, FOREIGN KEY → users.id)
   - title (VARCHAR)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

3. **chat_history**
   - id (INTEGER, PRIMARY KEY)
   - user_id (INTEGER, FOREIGN KEY → users.id)
   - thread_id (INTEGER, FOREIGN KEY → chat_threads.id)
   - message (TEXT)
   - response (TEXT)
   - model (VARCHAR)
   - session_id (VARCHAR)
   - created_at (TIMESTAMP)

4. **documents**
   - id (INTEGER, PRIMARY KEY)
   - user_id (INTEGER, FOREIGN KEY → users.id)
   - thread_id (INTEGER, FOREIGN KEY → chat_threads.id)
   - filename (VARCHAR)
   - original_filename (VARCHAR)
   - file_path (VARCHAR)
   - file_size (INTEGER)
   - file_type (VARCHAR)
   - status (VARCHAR)
   - chunk_count (INTEGER)
   - created_at (TIMESTAMP)

---

## 🎯 Quick Test Commands

### Terminal Testing
```bash
# Navigate to backend
cd /Users/ferozshaik/Desktop/Tothu/backend

# Run test script
python test_nl2sql.py
```

### Browser Testing
1. Open: http://localhost:8001/docs
2. Authenticate with test credentials
3. Try the `/api/nl-to-sql/` POST endpoint
4. Enter question: "How many users are in the database?"
5. Click Execute

---

## ✅ Project 8 Status

**Implementation Complete!**

All features implemented:
- ✅ Natural Language to SQL conversion
- ✅ Database schema introspection
- ✅ Security validation (READ-ONLY)
- ✅ Query execution
- ✅ Error handling
- ✅ REST API endpoints
- ✅ Swagger documentation
- ✅ Test scripts

**Ready for production use!**

---

## 📚 API Documentation

Full interactive documentation available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

---

## 🆘 Troubleshooting

### "Authentication required"
- Login first to get a token
- Use test@example.com / test123

### "Cannot generate query from this question"
- Check if question relates to existing tables
- View schema: GET /api/nl-to-sql/schema
- Rephrase question to be more specific

### "Query contains forbidden keyword"
- Only SELECT queries allowed
- Reformulate as a read operation

### Database connection error
- Check DATABASE_URL in .env
- Ensure database file exists
- Verify permissions

---

## 🎉 Next Steps

1. **Test with your questions** using Swagger UI
2. **Switch to PostgreSQL** for production (update .env)
3. **Add your own tables** to query different data
4. **Integrate with frontend** (optional)
5. **Monitor usage** and performance

Enjoy your AI-powered SQL assistant! 🚀
