# Frontend Integration with n8n - Simple Guide

## Goal
Update the frontend to route chat messages through n8n instead of calling the backend directly.

## Current Flow (Direct)
```
Frontend → Backend API (/api/chat)
```

## New Flow (via n8n)
```
Frontend → n8n Webhook → Backend API (/api/agent/chat)
```

## Environment Variable

Add to your frontend `.env.local`:
```bash
NEXT_PUBLIC_N8N_WEBHOOK_URL=http://localhost:5678/webhook/chat
NEXT_PUBLIC_USE_N8N=false  # Set to true to enable n8n routing
```

## Code Changes

### Option 1: Feature Flag (Recommended)

Update your chat API call to check if n8n is enabled:

```typescript
// In your chat component (e.g., app/page.tsx)

const sendMessage = async (message: string) => {
  const useN8n = process.env.NEXT_PUBLIC_USE_N8N === 'true';
  
  if (useN8n) {
    // Route through n8n
    const response = await fetch(process.env.NEXT_PUBLIC_N8N_WEBHOOK_URL!, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        thread_id: currentThreadId,
        user_id: user.id,
        token: token  // Your auth token
      })
    });
    
    const data = await response.json();
    return data.response;  // n8n returns {response: "text"}
    
  } else {
    // Direct backend call (existing code)
    const response = await fetch('http://localhost:8001/api/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        thread_id: currentThreadId,
        model: selectedModel
      })
    });
    
    const data = await response.json();
    return data.message;  // Direct API returns {message: "text"}
  }
};
```

### Option 2: Replace Existing Call

If you want to always use n8n, replace your existing fetch call:

**Before:**
```typescript
const response = await fetch('http://localhost:8001/api/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: input,
    thread_id: currentThreadId,
    model: selectedModel
  })
});
```

**After:**
```typescript
const response = await fetch('http://localhost:5678/webhook/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: input,
    thread_id: currentThreadId,
    user_id: user.id,
    token: token
  })
});
```

## Key Differences

| Aspect | Direct Backend | Via n8n |
|--------|---------------|---------|
| URL | `http://localhost:8001/api/chat` | `http://localhost:5678/webhook/chat` |
| Auth Header | `Authorization: Bearer token` | Token in body: `{token: "..."}` |
| Response | `{message: "text", ...}` | `{response: "text", ...}` |
| Routing | None | n8n decides which agent |

## Testing Steps

1. **Keep existing flow working** (set `USE_N8N=false`)
2. **Set up n8n workflow** (see N8N_INTEGRATION_GUIDE.md)
3. **Test n8n webhook** directly with curl
4. **Enable n8n in frontend** (set `USE_N8N=true`)
5. **Test in browser**

## Rollback

If anything goes wrong:
1. Set `NEXT_PUBLIC_USE_N8N=false`
2. Restart frontend
3. System works as before

## Next Steps

After this integration, you can:
- Add more routing rules in n8n
- Add logging/monitoring in n8n
- Add rate limiting
- Add multi-agent orchestration
- Add fallback strategies

All without touching frontend or backend code!
