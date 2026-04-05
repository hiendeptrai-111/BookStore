# 🧪 ChatBot API Testing Guide

## Quick Test with cURL

### 1. Test Backend is Running

```bash
curl http://localhost:8000/api/books/
```

Expected: JSON array of books

---

## Chat Endpoint Tests

### Test 1: Simple Message

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'
```

**Expected Response:**

```json
{
  "text": "Xin chào! Tôi là trợ lý ảo của BookStore..."
}
```

---

### Test 2: Find Books

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Bạn có sách gì?"}'
```

**Expected Response:**

```json
{
  "text": "Chúng tôi có [X] đầu sách..."
}
```

---

### Test 3: With Chat History

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Sách đó giá bao nhiêu?",
    "history": [
      {"role": "user", "text": "Bạn có sách Doraemon không?"},
      {"role": "model", "text": "Có, chúng tôi có sách Doraemon..."}
    ]
  }'
```

---

### Test 4: Empty Message (Error)

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

**Expected Response (400):**

```json
{
  "error": "Tin nhắn không được để trống"
}
```

---

### Test 5: Rate Limit (429)

Send 13+ requests within 60 seconds:

```bash
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/chat/ \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\"}"
done
```

**Expected Response (429):**

```json
{
  "error": "Quá nhiều yêu cầu. Vui lòng chờ một chút."
}
```

---

## Testing with Python

### Simple Request

```python
import requests
import json

url = "http://localhost:8000/api/chat/"
headers = {"Content-Type": "application/json"}
data = {"message": "Xin chào"}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### With Chat History

```python
import requests

url = "http://localhost:8000/api/chat/"
headers = {"Content-Type": "application/json"}

payload = {
    "message": "Sách đó bao nhiêu tiền?",
    "history": [
        {"role": "user", "text": "Bạn có sách Doraemon không?"},
        {"role": "model", "text": "Có, chúng tôi có sách Doraemon, nó là một bộ truyện tranh nổi tiếng..."}
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Load Test

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

url = "http://localhost:8000/api/chat/"
headers = {"Content-Type": "application/json"}

def send_request(msg):
    try:
        start = time.time()
        response = requests.post(
            url,
            json={"message": msg},
            headers=headers,
            timeout=30
        )
        elapsed = time.time() - start

        return {
            "status": response.status_code,
            "time": f"{elapsed:.2f}s",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {"error": str(e)}

# Test with 5 concurrent requests
messages = ["Xin chào", "Có sách gì?", "Giá bao nhiêu?", "Giao hàng mất bao lâu?", "Cảm ơn!"]

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(send_request, messages))

for i, result in enumerate(results):
    print(f"Request {i+1}: {result}")
```

---

## Testing with Postman

### 1. New Request

- Method: POST
- URL: `http://localhost:8000/api/chat/`

### 2. Headers

```
Content-Type: application/json
```

### 3. Body (raw JSON)

```json
{
  "message": "Xin chào",
  "history": []
}
```

### 4. Click Send

### 5. Expected Response

```json
{
  "text": "Gemini AI response..."
}
```

---

## JavaScript/Fetch Testing

```javascript
// Simple fetch
const response = await fetch("http://localhost:8000/api/chat/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "Xin chào" }),
});

const data = await response.json();
console.log(data.text);
```

### With Async/Await

```javascript
async function testChat() {
  try {
    const response = await fetch("http://localhost:8000/api/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "Bạn có sách gì?",
        history: [],
      }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    console.log("Bot:", data.text);
  } catch (error) {
    console.error("Error:", error);
  }
}

testChat();
```

---

## Test Scenarios

### Scenario 1: Book Search

```json
{ "message": "Có sách Doraemon không?" }
```

Expected: Returns Doraemon book info if in stock

### Scenario 2: Price Inquiry

```json
{ "message": "Sách giá rẻ nhất bao nhiêu?" }
```

Expected: Lists cheapest books

### Scenario 3: Category Browse

```json
{ "message": "Bạn có sách thiếu nhi nào?" }
```

Expected: Lists children's books

### Scenario 4: Store Info

```json
{ "message": "Cứa hàng của bạn ở đâu?" }
```

Expected: Store address and contact info

### Scenario 5: Shipping

```json
{ "message": "Giao hàng bao lâu?" }
```

Expected: Shipping time and cost info

### Scenario 6: Returns

```json
{ "message": "Nếu không thích có thể hoàn bớn không?" }
```

Expected: Return policy explanation

---

## Debugging Tips

### Check Backend Server is Running

```bash
curl http://localhost:8000/api/books/
# Should return JSON, not "Connection refused"
```

### Check API Key

```bash
cd backend
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
# Should print your API key, not None
```

### Check Requirements Installed

```bash
python -c "import google.generativeai; print('OK')"
# Should print "OK"
```

### View Server Logs

```bash
# Terminal running Django
# Look for error messages or print statements
python manage.py runserver
```

### Test Database Connection

```bash
python shell
>>> from api.models import Books
>>> Books.objects.count()
# Should show number of books
```

### Test Gemini Directly

```python
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print(response.text)
```

---

## Response Examples

### Success (200)

```json
{
  "text": "Chúng tôi có 45 đầu sách từ các thể loại khác nhau..."
}
```

### Bad Request (400)

```json
{
  "error": "Tin nhắn không được để trống"
}
```

### Rate Limited (429)

```json
{
  "error": "Quá nhiều yêu cầu. Vui lòng chờ một chút."
}
```

### Server Error (500)

```json
{
  "error": "Server error: [details]"
}
```

---

## Performance Benchmarks

Expected response times:

- **Database query:** 10-50ms
- **Gemini API:** 500-2000ms
- **Total:** 600-2100ms

### Slow Response Causes

1. Gemini API latency
2. First request (warmup)
3. Large prompt/history
4. Network issues

### Optimization Tips

1. Minimize history passed
2. Cache popular questions
3. Use async processing
4. Enable response streaming

---

## Continuous Testing

### Hourly Health Check

```bash
#!/bin/bash
while true; do
  curl -X POST http://localhost:8000/api/chat/ \
    -H "Content-Type: application/json" \
    -d '{"message": "health check"}' \
    && echo "✓ 200 OK" || echo "✗ ERROR"
  sleep 3600
done
```

### Monitor Errors

```bash
# In another terminal, watch logs
tail -f debug.log | grep ERROR
```

---

## API Contract

### Request

```typescript
interface ChatRequest {
  message: string; // Required, non-empty
  history?: Array<{
    // Optional
    role: "user" | "model";
    text: string;
  }>;
}
```

### Response

```typescript
interface ChatResponse {
  text: string; // The bot's response
}

// Or error:
interface ErrorResponse {
  error: string; // Error message
}
```

---

## Common Issues

### ❌ "Invalid API Key"

- Verify GEMINI_API_KEY in .env
- Get new key from ai.google.dev
- Restart Django server

### ❌ "Connection refused"

- Start Django: `python manage.py runserver`
- Check URL is correct: http://localhost:8000

### ❌ "CORS error"

- Check VITE_API_URL in frontend
- Backend already has CORS configured

### ❌ "Slow response"

- Normal for Gemini (0.5-2s)
- Check internet connection
- Check Gemini API quota

---

## ✅ Final Test Checklist

- [ ] Backend server starts
- [ ] Simple message returns response
- [ ] Chat history is sent
- [ ] Rate limiting triggers at 13 requests
- [ ] Error messages format correctly
- [ ] Response time < 3 seconds
- [ ] Bot has database knowledge
- [ ] Multiple conversations work
- [ ] Frontend displays responses
- [ ] No CORS errors in browser

---

**Happy Testing! 🧪**

For more help, see CHATBOT_QUICKSTART.md
