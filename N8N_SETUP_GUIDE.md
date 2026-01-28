# N8N AI Agents Integration Guide

## Overview
This guide will help you set up and use N8N AI agents with your chat application. N8N allows you to create powerful workflow automation and AI agents that can be triggered from your chat interface.

## 🚀 Quick Start

### 1. Start N8N with Docker

```bash
# Start N8N and PostgreSQL
docker-compose -f docker-compose.n8n.yml up -d

# Check if N8N is running
docker ps | grep n8n
```

N8N will be available at: **http://localhost:5678**

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### 2. Access N8N Interface

1. Open your browser and go to: http://localhost:5678
2. Login with the credentials above
3. You'll see the N8N workflow editor

### 3. Verify Integration

Check if the backend can connect to N8N:

```bash
curl http://localhost:8001/api/n8n/health
```

Expected response:
```json
{
  "n8n_status": "healthy",
  "n8n_url": "http://localhost:5678",
  "status_code": 200
}
```

## 📋 Available API Endpoints

### 1. Execute N8N Workflow
```bash
POST /api/n8n/workflow/execute
```

**Request Body:**
```json
{
  "workflow_id": "your-workflow-id",
  "data": {
    "prompt": "Analyze this data",
    "context": {}
  }
}
```

### 2. Trigger N8N Webhook
```bash
POST /api/n8n/webhook/trigger
```

**Request Body:**
```json
{
  "webhook_id": "ai-agent",
  "data": {
    "message": "Hello from chat app"
  }
}
```

### 3. Execute AI Agent
```bash
POST /api/n8n/agent/execute
```

**Request Body:**
```json
{
  "agent_type": "research",
  "prompt": "Find information about AI trends",
  "context": {
    "topic": "artificial intelligence"
  }
}
```

**Supported Agent Types:**
- `research` - Research and data gathering
- `task_automation` - Automated task execution
- `data_analysis` - Analyze and process data
- `custom` - Custom agent workflows

### 4. List Workflows
```bash
GET /api/n8n/workflows/list
```

### 5. Health Check
```bash
GET /api/n8n/health
```

## 🎯 Creating Your First AI Agent Workflow

### Example: Research Agent

1. **Login to N8N** at http://localhost:5678

2. **Create New Workflow:**
   - Click "+ Add workflow" button
   - Name it "AI Research Agent"

3. **Add Webhook Trigger:**
   - Click "Add first step"
   - Select "Webhook"
   - Set HTTP Method: POST
   - Set Path: `ai-agent`
   - Click "Execute Node" to get the webhook URL

4. **Add AI Node:**
   - Click the "+" button
   - Search for "OpenAI" or "Google Gemini"
   - Configure with your API key
   - Set the prompt to use incoming data:
     ```
     {{ $json.prompt }}
     Context: {{ $json.context }}
     ```

5. **Add Response Node:**
   - Add "Respond to Webhook" node
   - Set response data:
     ```json
     {
       "success": true,
       "result": "{{ $json.output }}",
       "agent_type": "{{ $json.agent_type }}"
     }
     ```

6. **Activate Workflow:**
   - Toggle the switch to "Active"
   - Save the workflow

### Test the Agent

```bash
curl -X POST http://localhost:8001/api/n8n/agent/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "research",
    "prompt": "What are the latest trends in AI?",
    "context": {"year": 2026}
  }'
```

## 📦 Pre-built Agent Templates

### 1. Email Automation Agent
- Monitors inbox
- Categorizes emails
- Sends automated responses

### 2. Data Analysis Agent
- Processes CSV/Excel files
- Generates insights
- Creates visualizations

### 3. Content Creation Agent
- Generates blog posts
- Creates social media content
- Optimizes SEO

### 4. Task Management Agent
- Creates tasks from emails
- Updates project status
- Sends notifications

## 🔧 Configuration

### Environment Variables

Add to your `.env` file:

```bash
# N8N Configuration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-api-key-here
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

### Security (Production)

For production, update `docker-compose.n8n.yml`:

```yaml
environment:
  - N8N_BASIC_AUTH_ACTIVE=true
  - N8N_BASIC_AUTH_USER=your-username
  - N8N_BASIC_AUTH_PASSWORD=strong-password
  - N8N_PROTOCOL=https
  - N8N_HOST=your-domain.com
```

## 🔗 Integration with Chat App

### Frontend Integration

```typescript
// Call N8N agent from your chat
const executeAgent = async (prompt: string) => {
  const response = await fetch('http://localhost:8001/api/n8n/agent/execute', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_type: 'research',
      prompt: prompt,
      context: { source: 'chat' }
    })
  });
  
  return await response.json();
};
```

## 📊 Monitoring

### View Workflow Executions

1. Go to N8N interface: http://localhost:5678
2. Click on "Executions" in the sidebar
3. View execution logs and results

### Check Logs

```bash
# View N8N logs
docker logs n8n_agent -f

# View backend logs
tail -f /tmp/backend.log | grep n8n
```

## 🛠️ Troubleshooting

### N8N Not Starting

```bash
# Check if port 5678 is available
lsof -ti:5678

# Restart N8N
docker-compose -f docker-compose.n8n.yml restart

# View logs
docker logs n8n_agent
```

### Connection Issues

1. Verify N8N is running: `docker ps`
2. Check health endpoint: `curl http://localhost:5678/healthz`
3. Verify backend can reach N8N: `curl http://localhost:8001/api/n8n/health`

### Workflow Not Triggering

1. Check if workflow is active (toggle in N8N UI)
2. Verify webhook URL is correct
3. Check execution logs in N8N
4. Ensure authentication is configured properly

## 🎓 Advanced Usage

### Custom Nodes

Create custom N8N nodes for specific tasks:

```javascript
// Example: Custom node for your database
{
  "name": "CustomDB",
  "version": 1,
  "description": "Query your custom database",
  "defaults": {
    "name": "Custom DB"
  },
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Query",
      "name": "query",
      "type": "string",
      "default": ""
    }
  ]
}
```

### Webhook Security

Add authentication to webhooks:

```javascript
// In N8N workflow
if (headers.authorization !== 'Bearer YOUR_SECRET') {
  return { error: 'Unauthorized' };
}
```

## 📚 Resources

- **N8N Documentation**: https://docs.n8n.io
- **Community Workflows**: https://n8n.io/workflows
- **API Reference**: https://docs.n8n.io/api/
- **Discord Community**: https://discord.gg/n8n

## 🎯 Next Steps

1. ✅ Start N8N with Docker
2. ✅ Create your first workflow
3. ✅ Test the integration
4. 📝 Create custom agents for your use case
5. 🚀 Deploy to production

## 🔐 Security Best Practices

1. **Change default credentials** immediately
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Restrict network access** to N8N
5. **Regular backups** of workflows
6. **Use API keys** for authentication
7. **Monitor execution logs** for suspicious activity

## 💡 Example Use Cases

### 1. Customer Support Agent
- Auto-respond to common queries
- Escalate complex issues
- Track response times

### 2. Sales Pipeline Agent
- Qualify leads automatically
- Send follow-up emails
- Update CRM systems

### 3. Content Moderation Agent
- Scan uploads for inappropriate content
- Flag suspicious activity
- Send notifications to admins

### 4. Analytics Agent
- Generate daily reports
- Monitor KPIs
- Send alerts on anomalies

## 🚀 Getting Started Checklist

- [ ] Start N8N with Docker
- [ ] Login to N8N interface
- [ ] Create first workflow with webhook
- [ ] Test webhook from backend
- [ ] Create AI agent workflow
- [ ] Integrate with chat interface
- [ ] Set up monitoring
- [ ] Configure security settings
- [ ] Deploy to production

---

**Need Help?** Check the troubleshooting section or open an issue in the repository.
