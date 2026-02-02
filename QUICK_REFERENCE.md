# 🚀 Multi-Agent System - Quick Reference

## ⚡ Quick Commands

### Start All Services
```bash
./start_all.sh          # Backend + Frontend
./start_n8n.sh          # N8N workflow engine
```

### Test Multi-Agent System
```bash
./test_multi_agent.sh   # Full automated test suite
```

### Manual Test
```bash
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 25 * 48"}'
```

---

## 📍 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| N8N | http://localhost:5678 | Workflow UI |
| Backend API | http://localhost:8001 | AI Backend |
| API Docs | http://localhost:8001/docs | Swagger |
| Frontend | http://localhost:3000 | Chat UI |
| Multi-Agent | http://localhost:5678/webhook/multi-agent | Webhook |

---

## 🔑 Credentials

### N8N
- **URL**: http://localhost:5678
- **First Time**: Create your own account
- **Stored**: Locally in n8n database

### Backend API
- **API Key**: `n8n-secret-key-12345`
- **Header**: `X-API-Key: n8n-secret-key-12345`

### Google OAuth
- **Client ID**: In `.env` file
- **Client Secret**: In `.env` file

---

## 🤖 Agent Quick Reference

### Coordinator Agent
- **Triggers**: Pattern matching on input
- **Classifies**: calculation | api_call | data_query | general_chat | support
- **Confidence**: 0.7-0.95 depending on pattern match
- **Example**: "calculate 5+3" → calculation (0.95)

### Execution Agent  
- **Calculator**: Handles +, -, *, /
- **Backend API**: Calls Gemini or MCP agent
- **Outputs**: Result + execution time + steps

### Validation Agent
- **Threshold**: 0.75 (configurable)
- **Checks**: Completeness, correctness, format
- **Recommends**: approve | retry | reject

---

## 📊 Test Cases

### ✅ Passing Tests
```bash
# Math
"Calculate 25 * 48" → 1200
"What is 100 + 250?" → 350
"Compute 1000 / 25" → 40

# AI
"What is AI?" → Detailed explanation
"Tell me about Python" → Programming info

# Support
"Help me calculate 150 * 25" → MCP agent response
```

### ❌ Error Handling
```bash
# Invalid input
"Calculate abc * xyz" → Graceful error

# Edge cases
"What is 10 / 0?" → Infinity or error message
```

---

## 🐛 Troubleshooting Quick Fixes

### Workflow Not Responding
```bash
# Check if active
# In N8N: Toggle "Active" switch (must be green)

# Restart n8n
pkill -f n8n
./start_n8n.sh
```

### Backend API Error
```bash
# Test backend
curl http://localhost:8001/api/n8n/health \
  -H "X-API-Key: n8n-secret-key-12345"

# Restart backend
pkill -f uvicorn
cd backend && source ../venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Import Errors
```bash
# If workflow import fails:
# 1. Make sure n8n is updated
# 2. Check JSON is valid
# 3. Try importing again
```

---

## 📈 Performance Targets

| Metric | Target | Check With |
|--------|--------|------------|
| Calculator | < 100ms | test_multi_agent.sh |
| API Call | < 1500ms | N8N executions |
| Success Rate | > 95% | Test results |
| Validation | > 0.75 | Execution logs |

---

## 🔄 Common Workflows

### Add New Tool
1. Create tool function in Execution Agent
2. Add tool name to Coordinator classification
3. Update validation logic
4. Test with new queries

### Modify Validation Threshold
1. Open workflow in n8n
2. Find "Validation Agent" node
3. Change `0.75` to desired value
4. Save and test

### Add New Agent
1. Add Code node after current agents
2. Define agent logic
3. Connect to workflow
4. Update documentation

---

## 📝 File Locations

```
/Tothu/
├── n8n-multi-agent-workflow.json       # Import this
├── MULTI_AGENT_README.md               # Start here
├── MULTI_AGENT_SUMMARY.md              # Executive summary
├── MULTI_AGENT_ARCHITECTURE.md         # Detailed design
├── MULTI_AGENT_IMPLEMENTATION_GUIDE.md # Step-by-step
├── test_multi_agent.sh                 # Test suite
└── QUICK_REFERENCE.md                  # This file
```

---

## 🎯 Next Actions

### Today
- [ ] Import workflow
- [ ] Run tests
- [ ] Review logs
- [ ] Test custom queries

### This Week
- [ ] Customize agent logic
- [ ] Add monitoring
- [ ] Implement memory
- [ ] Add more tools

---

## 💡 Pro Tips

### Debugging
- Check N8N "Executions" tab for detailed logs
- Use `console.log()` in Code nodes
- Monitor backend logs: `tail -f /tmp/backend_new.log`

### Performance
- Cache frequent calculations
- Use parallel execution where possible
- Optimize API calls

### Security
- Rotate API keys regularly
- Use environment variables
- Validate all inputs
- Rate limit requests

---

## 📞 Support Resources

| Question | Resource |
|----------|----------|
| How to import? | MULTI_AGENT_IMPLEMENTATION_GUIDE.md |
| Architecture? | MULTI_AGENT_ARCHITECTURE.md |
| Agent prompts? | MULTI_AGENT_IMPLEMENTATION_GUIDE.md |
| Troubleshooting? | MULTI_AGENT_IMPLEMENTATION_GUIDE.md |
| API docs? | http://localhost:8001/docs |

---

## ✅ Pre-Flight Checklist

Before using in production:

- [ ] All tests passing
- [ ] Workflow active in n8n
- [ ] API keys configured
- [ ] Backend running
- [ ] Error handling tested
- [ ] Performance acceptable
- [ ] Documentation reviewed
- [ ] Monitoring enabled
- [ ] Security verified
- [ ] Backup strategy

---

**Keep this file handy for quick reference!** 📌
