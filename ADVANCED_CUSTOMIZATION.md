# 🔧 Advanced Chatbot Customization Guide

## Mục lục

1. [Tùy chỉnh System Prompt](#tùy-chỉnh-system-prompt)
2. [Thêm Custom Intent](#thêm-custom-intent)
3. [Tăng Cường Context](#tăng-cường-context)
4. [Caching Strategy](#caching-strategy)
5. [Stream Response](#stream-response)
6. [Fine-tuning Behavior](#fine-tuning-behavior)

---

## 🎯 Tùy chỉnh System Prompt

### Vị trí Code

File: `backend/api/gemini_service.py` → function `build_system_prompt()`

### Ví dụ: Thêm Personality

```python
def build_system_prompt() -> str:
    # ... existing code ...

    prompt += f"""
## PERSONALITY
- Tên của bạn: "Bot Thủ Lĩnh Sách"
- Bạn cực kỳ enthusiastic về sách
- Nếu user hỏi gì liên quan sách, hãy trả lời với emoji 📚
- Thỉnhale khi user hỏi về các tác phẩm kinh điển
"""
    return prompt.strip()
```

### Ví dụ: Thêm Business Rules

```python
prompt += f"""
## BUSINESS RULES
- Nếu giá > 500,000đ, gợi ý program khuyến mãi
- Nếu stock < 5, nhấn trang "sắp hết hàng"
- Nếu hỏi về sách không có, gợi ý 3 sách thay thế
- Discount 10% cho đơn hàng đầu tiên
"""
```

---

## 🎪 Thêm Custom Intent

### Tạo Intent Mới (Ví dụ: Hỏi về shipping)

```python
# backend/api/gemini_service.py

def get_shipping_info() -> dict:
    """Lấy thông tin giao hàng từ config."""
    return {
        'methods': [
            {'name': 'Standard', 'cost': 25000, 'days': '2-5'},
            {'name': 'Express', 'cost': 50000, 'days': '1-2'},
            {'name': 'Free', 'min_order': 300000}
        ],
        'coverage': 'Toàn quốc',
        'return_policy': '7 ngày hoàn tiền'
    }

def build_system_prompt() -> str:
    # ... existing code ...

    shipping = get_shipping_info()

    prompt += f"""
## SHIPPING INFORMATION
{json.dumps(shipping, ensure_ascii=False, indent=2)}
"""
    return prompt.strip()
```

### Dynamic Intent Based on User Input

```python
def detect_intent(message: str) -> str:
    """Phát hiện ý định của user."""
    keywords = {
        'shipping': ['giao hàng', 'ship', 'vận chuyển', 'delivery'],
        'refund': ['hoàn tiền', 'refund', 'đổi trả', 'return'],
        'recommendation': ['gợi ý', 'recommend', 'nên', 'tốt nhất'],
        'promotion': ['khuyến mãi', 'sale', 'discount', 'giảm giá'],
    }

    msg_lower = message.lower()
    for intent, kws in keywords.items():
        if any(kw in msg_lower for kw in kws):
            return intent
    return 'general'

def get_gemini_reply(message: str, chat_history: list = None) -> str:
    intent = detect_intent(message)

    # Có thể inject thêm context dựa trên intent
    if intent == 'shipping':
        # Inject shipping details vào prompt
        pass
    elif intent == 'recommendation':
        # Inject trending books
        pass

    # ... rest of code ...
```

---

## 📈 Tăng Cường Context Database

### Lấy Trending Books

```python
def get_trending_books(days: int = 30) -> list:
    """Lấy sách bán chạy trong N ngày gần đây."""
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    trending = (
        OrderItems.objects
        .filter(order__order_date__gte=cutoff_date)
        .values('book')
        .annotate(total_sold=Count('book'))
        .order_by('-total_sold')[:10]
    )

    books = Books.objects.filter(
        book_id__in=[item['book'] for item in trending]
    )

    return [
        {
            'title': b.title,
            'author': b.author.full_name,
            'sales': sum(1 for item in trending if item['book'] == b.book_id),
            'rating': '4.5/5'  # Add rating if available
        }
        for b in books
    ]

# Thêm vào build_system_prompt():
trending = get_trending_books()
prompt += f"## TRENDING BOOKS\n{json.dumps(trending, ensure_ascii=False)}"
```

### Lấy User Recommendation History

```python
def get_user_preference(customer_id: int = None) -> dict:
    """Lấy sở thích của user dựa trên order history."""
    if not customer_id:
        return {}

    orders = Orders.objects.filter(customer_id=customer_id)
    categories = (
        OrderItems.objects
        .filter(order__in=orders)
        .values('book__category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return {
        'favorite_categories': [c['book__category__name'] for c in categories],
        'total_purchases': sum(o.quantity for o in OrderItems.objects.filter(order__in=orders)),
        'total_spent': sum(float(o.total_amount) for o in orders)
    }
```

### Stock Status Summary

```python
def get_stock_summary() -> dict:
    """Lấy tóm tắt tình trạng hàng."""
    return {
        'total_books': Books.objects.count(),
        'in_stock': Books.objects.filter(stock_quantity__gt=0).count(),
        'low_stock': Books.objects.filter(
            stock_quantity__gt=0,
            stock_quantity__lt=10
        ).count(),
        'out_of_stock': Books.objects.filter(stock_quantity=0).count(),
    }
```

---

## 💾 Caching Strategy

### Redis Caching (Optional)

```python
# backend/api/gemini_service.py
from django.core.cache import cache

def get_book_context() -> dict:
    """Get with caching."""
    cache_key = 'bookstore:books_context'
    cached = cache.get(cache_key)

    if cached:
        return cached

    # ... existing logic ...

    # Cache for 10 minutes
    cache.set(cache_key, result, timeout=600)
    return result
```

### Settings Configuration

```python
# backend/backend/settings.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Fallback to memory cache if Redis not available
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

---

## 🔄 Stream Response (Advanced)

### Django Streaming Response

```python
from django.http import StreamingHttpResponse
import json

@api_view(['POST'])
def chat_stream(request):
    """Chat endpoint with streaming response."""
    message = request.data.get('message', '').strip()

    def stream_response():
        try:
            # Get response from Gemini
            response = model.generate_content(prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    # Send chunk as JSON
                    data = json.dumps({
                        'chunk': chunk.text,
                        'done': False
                    })
                    yield f"data: {data}\n\n"

            # Send final chunk
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_data = json.dumps({'error': str(e), 'done': True})
            yield f"data: {error_data}\n\n"

    return StreamingHttpResponse(
        stream_response(),
        content_type='text/event-stream'
    )
```

### Frontend StreamingResponse Handler

```typescript
// frontend/src/services/geminiService.ts

export async function getChatResponseStreaming(
  history: ChatMessage[],
  message: string,
  onChunk: (chunk: string) => void,
): Promise<void> {
  const formattedHistory = history.map((msg) => ({
    role: msg.role === "user" ? "user" : "model",
    text: msg.text,
  }));

  const response = await fetch(`${API_BASE_URL}/chat/stream/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      history: formattedHistory,
    }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.chunk) {
            onChunk(data.chunk);
          }
        } catch (e) {
          console.error("Failed to parse chunk:", e);
        }
      }
    }
  }
}
```

---

## 🎛️ Fine-tuning Behavior

### Temperature & Top-P Control

```python
def get_gemini_reply(message: str, chat_history: list = None) -> str:
    """
    Temperature: Controls randomness
      - 0: Deterministic, consistent
      - 1: Balanced
      - 2: Creative, random

    top_p: Nucleus sampling
      - 0.1: Conservative
      - 0.9: Diverse
    """
    response = model.generate_content(
        [system_prompt, ...messages],
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,  # Balanced
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
            candidate_count=1,
        ),
    )
    return response.text
```

### Safety Settings

```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

response = model.generate_content(
    [system_prompt, ...messages],
    safety_settings=[
        {
            "category": HarmCategory.HARM_CATEGORY_UNSPECIFIED,
            "threshold": HarmBlockThreshold.BLOCK_NONE,
        },
        {
            "category": HarmCategory.HARM_CATEGORY_DEROGATORY_CONTENT,
            "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
    ],
)
```

### Response Validation

```python
def validate_response(response_text: str, message: str) -> str:
    """Xác thực response từ Gemini."""
    # Check length
    if len(response_text) < 10:
        return "Xin lỗi, tôi không thể trả lời câu hỏi này."

    # Check for inappropriate content
    banned_words = ['badword1', 'badword2']
    if any(word in response_text.lower() for word in banned_words):
        return "Câu trả lời chứa nội dung không phù hợp."

    # Check relevance
    if is_off_topic(response_text, message):
        return "Xin lỗi, câu trả lời không liên quan."

    return response_text

def is_off_topic(response: str, original_message: str) -> bool:
    """Check if response is off-topic."""
    # Simple keyword matching or semantic similarity
    return False  # Implement your logic
```

---

## 📊 Analytics & Logging

### Log All Chat Interactions

```python
from .models import ChatLog

@api_view(['POST'])
def chat(request):
    message = request.data.get('message', '').strip()

    # ... existing code ...

    reply = get_gemini_reply(message, chat_history)

    # Log interaction
    ChatLog.objects.create(
        user_message=message,
        bot_response=reply,
        timestamp=timezone.now(),
        user_ip=get_client_ip(request),
    )

    return Response({'text': reply})

def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

### Create ChatLog Model

```python
# backend/api/models.py

class ChatLog(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey('Customers', null=True, blank=True, on_delete=models.SET_NULL)
    response_time_ms = models.IntegerField(default=0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp}: {self.user_message[:50]}"
```

---

## 🔐 Advanced Security

### Input Validation

```python
import re

def validate_message(message: str) -> tuple[bool, str]:
    """Validate user message."""
    if len(message) < 1:
        return False, "Message too short"
    if len(message) > 5000:
        return False, "Message too long"

    # Check for injection attacks
    if any(pattern in message for pattern in [
        '<?php', 'import', 'execute', 'eval'
    ]):
        return False, "Suspicious content detected"

    return True, ""
```

### Rate Limiting Per User

```python
from django.contrib.auth.models import User

def get_user_rate_limit(request) -> tuple[bool, int]:
    """Check rate limit per authenticated user."""
    user_id = getattr(request.user, 'id', None)
    if not user_id:
        return _check_ip_rate_limit(request)

    cache_key = f"rate_limit:user:{user_id}"
    count = cache.get(cache_key, 0)

    if count >= 100:  # 100 requests per hour
        return False, 3600

    cache.set(cache_key, count + 1, timeout=3600)
    return True, 0
```

---

## 📚 Testing

### Unit Tests

```python
# backend/api/tests.py
from django.test import TestCase
from .gemini_service import get_gemini_reply, build_system_prompt

class ChatbotTests(TestCase):
    def test_empty_message(self):
        """Test empty message handling."""
        response = get_gemini_reply("")
        self.assertIn("không được để trống", response)

    def test_book_context(self):
        """Test that context includes books."""
        prompt = build_system_prompt()
        self.assertIn("SÁCH HIỆN CÓ", prompt)

    def test_response_not_empty(self):
        """Test that response is never empty."""
        response = get_gemini_reply("Xin chào")
        self.assertGreater(len(response), 0)
```

---

## 🚀 Performance Optimization

### Lazy Loading

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_categories_cached():
    """Cache expensive database query."""
    return list(Categories.objects.all())

# Clear cache when new category added
def create_category(request):
    # ... create logic ...
    get_categories_cached.cache_clear()
    # ...
```

### Batch Processing

```python
def get_recommended_books(count: int = 10):
    """Get recommendations in batch."""
    return (
        Books.objects
        .select_related('author', 'category')
        .prefetch_related('orderitems')
        .filter(stock_quantity__gt=0)
        .order_by('-book_id')[:count]
    )
```

---

## 📖 Additional Resources

- [Gemini API Advanced Guide](https://ai.google.dev/docs/guides)
- [Django Performance Tips](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [Caching Best Practices](https://redis.io/docs/management/optimization/eviction-policies/)

---

**Happy Advanced Customization! 🚀**
