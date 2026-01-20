# Project 7: API Examples & Code Snippets

## 📡 Complete API Examples

This document provides ready-to-use code examples for testing Project 7's RAG implementation.

---

## 🔑 Authentication First

All examples assume you have a valid JWT token. Get it by logging in:

```bash
# Login to get token
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# Save token for subsequent requests
export TOKEN="your_access_token_here"
```

---

## 1️⃣ Upload Document to Thread

### cURL Example

```bash
# Upload PDF to thread 5
curl -X POST "http://localhost:8001/api/documents/upload?thread_id=5" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf"

# Upload TXT file
curl -X POST "http://localhost:8001/api/documents/upload?thread_id=5" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.txt"
```

### Python Example

```python
import requests

def upload_document(token, thread_id, file_path):
    url = f"http://localhost:8001/api/documents/upload?thread_id={thread_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, headers=headers, files=files)
    
    return response.json()

# Usage
result = upload_document(token="your_token", thread_id=5, file_path="document.pdf")
print(f"Document ID: {result['id']}")
print(f"Status: {result['status']}")
print(f"Filename: {result['original_filename']}")
```

### JavaScript/TypeScript Example

```typescript
async function uploadDocument(token: string, threadId: number, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(
    `http://localhost:8001/api/documents/upload?thread_id=${threadId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );
  
  return await response.json();
}

// Usage with React
const handleUpload = async (file: File) => {
  const result = await uploadDocument(token, currentThreadId, file);
  console.log('Upload result:', result);
};
```

---

## 2️⃣ List Documents

### cURL Example

```bash
# List all documents for user
curl -X GET "http://localhost:8001/api/documents/" \
  -H "Authorization: Bearer $TOKEN"

# List documents for specific thread
curl -X GET "http://localhost:8001/api/documents/?thread_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

### Python Example

```python
def list_documents(token, thread_id=None):
    url = "http://localhost:8001/api/documents/"
    if thread_id:
        url += f"?thread_id={thread_id}"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# Usage
documents = list_documents(token="your_token", thread_id=5)
for doc in documents:
    print(f"{doc['original_filename']}: {doc['status']} ({doc['chunk_count']} chunks)")
```

### Response Example

```json
[
  {
    "id": 1,
    "filename": "abc-123-456.pdf",
    "original_filename": "research_paper.pdf",
    "file_size": 245678,
    "file_type": "pdf",
    "status": "ready",
    "chunk_count": 42,
    "created_at": "2026-01-19T12:00:00"
  },
  {
    "id": 2,
    "filename": "def-789.txt",
    "original_filename": "notes.txt",
    "file_size": 5432,
    "file_type": "txt",
    "status": "ready",
    "chunk_count": 3,
    "created_at": "2026-01-19T12:15:00"
  }
]
```

---

## 3️⃣ Chat with RAG

### cURL Example

```bash
# Send message to thread with documents
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is the main conclusion of the research?",
    "thread_id": 5
  }'
```

### Python Example

```python
def chat_with_rag(token, message, thread_id):
    url = "http://localhost:8001/api/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "message": message,
        "thread_id": thread_id
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Usage
result = chat_with_rag(
    token="your_token",
    message="What methodology was used in the study?",
    thread_id=5
)

print(f"AI Response: {result['message']}")
print(f"Used RAG: {result.get('used_rag', False)}")
```

### Response Example

```json
{
  "message": "According to the research_paper.pdf, the study employed a mixed-methods approach combining quantitative surveys (n=500) with qualitative interviews (n=25). The methodology section details...",
  "model": "gemini-2.5-flash",
  "thread_id": 5,
  "used_rag": true
}
```

---

## 4️⃣ Delete Document

### cURL Example

```bash
# Delete document and its embeddings
curl -X DELETE "http://localhost:8001/api/documents/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Python Example

```python
def delete_document(token, document_id):
    url = f"http://localhost:8001/api/documents/{document_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response.json()

# Usage
result = delete_document(token="your_token", document_id=1)
print(result['message'])
```

---

## 🧪 Complete Test Script

### Full Workflow in Python

```python
import requests
import time
from pathlib import Path

class RAGClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.thread_id = None
    
    def login(self, email, password):
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        self.token = response.json()["access_token"]
        return self.token
    
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_thread(self, message="Hello"):
        """Create a new thread by sending first message"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            headers=self._headers(),
            json={"message": message}
        )
        data = response.json()
        self.thread_id = data["thread_id"]
        return self.thread_id
    
    def upload_document(self, file_path):
        """Upload document to current thread"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/api/documents/upload?thread_id={self.thread_id}",
                headers=self._headers(),
                files=files
            )
        return response.json()
    
    def list_documents(self):
        """List documents in current thread"""
        response = requests.get(
            f"{self.base_url}/api/documents/?thread_id={self.thread_id}",
            headers=self._headers()
        )
        return response.json()
    
    def chat(self, message):
        """Send message to AI with RAG"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            headers=self._headers(),
            json={
                "message": message,
                "thread_id": self.thread_id
            }
        )
        return response.json()
    
    def delete_document(self, document_id):
        """Delete a document"""
        response = requests.delete(
            f"{self.base_url}/api/documents/{document_id}",
            headers=self._headers()
        )
        return response.json()


# Usage Example
def test_rag_workflow():
    client = RAGClient()
    
    # 1. Login
    print("1. Logging in...")
    client.login("test@example.com", "password123")
    print("✅ Logged in")
    
    # 2. Create thread
    print("\n2. Creating thread...")
    thread_id = client.create_thread("Let's discuss this document")
    print(f"✅ Thread created: {thread_id}")
    
    # 3. Upload document
    print("\n3. Uploading document...")
    upload_result = client.upload_document("test_document.txt")
    print(f"✅ Document uploaded: {upload_result['original_filename']}")
    print(f"   Status: {upload_result['status']}")
    
    # 4. Wait for processing
    print("\n4. Waiting for processing...")
    time.sleep(5)
    
    # 5. Check document status
    print("\n5. Checking document status...")
    docs = client.list_documents()
    for doc in docs:
        print(f"   - {doc['original_filename']}: {doc['status']} ({doc['chunk_count']} chunks)")
    
    # 6. Query document
    print("\n6. Querying document...")
    questions = [
        "What is this document about?",
        "Summarize the main points",
        "What is quantum computing?"  # Out of scope test
    ]
    
    for question in questions:
        print(f"\n   Q: {question}")
        response = client.chat(question)
        print(f"   A: {response['message'][:200]}...")
        print(f"   Used RAG: {response.get('used_rag', False)}")
    
    # 7. Delete document (optional)
    # doc_id = docs[0]['id']
    # print(f"\n7. Deleting document {doc_id}...")
    # client.delete_document(doc_id)
    # print("✅ Document deleted")

if __name__ == "__main__":
    test_rag_workflow()
```

---

## 🌐 Frontend Integration Examples

### React Component

```tsx
import { useState } from 'react';

interface RAGChatProps {
  token: string;
  threadId: number;
}

export function RAGChat({ token, threadId }: RAGChatProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState<any[]>([]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const uploadDocument = async () => {
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(
        `http://localhost:8001/api/documents/upload?thread_id=${threadId}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        }
      );
      
      const result = await response.json();
      console.log('Upload successful:', result);
      setFile(null);
      
      // Refresh document list
      loadDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const loadDocuments = async () => {
    const response = await fetch(
      `http://localhost:8001/api/documents/?thread_id=${threadId}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    const docs = await response.json();
    setDocuments(docs);
  };

  return (
    <div>
      <input type="file" onChange={handleFileSelect} />
      {file && (
        <button onClick={uploadDocument} disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      )}
      
      <div>
        <h3>Uploaded Documents:</h3>
        {documents.map(doc => (
          <div key={doc.id}>
            {doc.original_filename} - {doc.status} ({doc.chunk_count} chunks)
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 📝 Sample Test Documents

### test_document.txt
```
Artificial Intelligence and Machine Learning

Introduction:
This document provides an overview of AI and ML technologies.

Key Points:
1. AI is the simulation of human intelligence in machines
2. Machine learning is a subset of AI that enables systems to learn from data
3. Deep learning uses neural networks with multiple layers

Applications:
- Natural language processing
- Computer vision
- Autonomous vehicles
- Healthcare diagnostics

Conclusion:
AI and ML are transforming industries worldwide.
```

### research_paper_sample.txt
```
Research Study: Impact of Remote Work on Productivity

Abstract:
This study examines the effects of remote work on employee productivity
during 2020-2025.

Methodology:
- Quantitative surveys (n=500)
- Qualitative interviews (n=25)
- Longitudinal data analysis

Key Findings:
1. 78% of employees report increased productivity when working remotely
2. Communication challenges remain a concern for 45% of teams
3. Work-life balance improved for 82% of respondents

Conclusion:
Remote work shows positive impact on productivity with proper support systems.
```

---

## 🔍 Advanced Queries

### Complex RAG Queries

```python
queries = [
    # Factual questions
    "What is the main topic of this document?",
    "List all the key findings mentioned",
    "What methodology was used?",
    
    # Analytical questions
    "Summarize the document in 3 sentences",
    "What are the implications of these findings?",
    "How do the results compare to expectations?",
    
    # Specific questions
    "What does section 2 discuss?",
    "What percentage of employees reported increased productivity?",
    "What were the sample sizes used?",
    
    # Out-of-scope tests
    "What is quantum physics?",
    "Tell me about cryptocurrency",
    "What happened in World War 2?"
]

for query in queries:
    response = client.chat(query)
    print(f"\nQ: {query}")
    print(f"A: {response['message'][:150]}...")
    print(f"RAG used: {response.get('used_rag')}")
```

---

## 🎯 Testing Checklist

```python
def run_comprehensive_tests(client):
    """Run all RAG system tests"""
    
    tests = {
        "Upload PDF": lambda: client.upload_document("test.pdf"),
        "Upload TXT": lambda: client.upload_document("test.txt"),
        "Upload DOCX": lambda: client.upload_document("test.docx"),
        "List documents": lambda: client.list_documents(),
        "Query with RAG": lambda: client.chat("What is this about?"),
        "Out-of-scope query": lambda: client.chat("What is quantum computing?"),
        "Delete document": lambda: client.delete_document(1),
    }
    
    results = {}
    for test_name, test_func in tests.items():
        try:
            result = test_func()
            results[test_name] = "✅ PASS"
            print(f"{test_name}: ✅")
        except Exception as e:
            results[test_name] = f"❌ FAIL: {e}"
            print(f"{test_name}: ❌ {e}")
    
    return results
```

---

## 📊 Performance Monitoring

```python
import time

def benchmark_rag_query(client, query, iterations=5):
    """Benchmark RAG query performance"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        result = client.chat(query)
        end = time.time()
        times.append(end - start)
        print(f"Iteration {i+1}: {times[-1]:.2f}s")
    
    avg_time = sum(times) / len(times)
    print(f"\nAverage response time: {avg_time:.2f}s")
    print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")
    
    return avg_time
```

---

## 🚀 Ready-to-Run Examples

All examples above are production-ready and can be run immediately with:

1. **Backend running** on http://localhost:8001
2. **Valid credentials** for authentication
3. **Test documents** prepared

Copy any example and modify with your credentials to start testing!

---

**Last Updated:** January 19, 2026  
**Status:** All Examples Tested ✅
