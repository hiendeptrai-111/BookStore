# 📝 BookStore Chatbot - Changes & Implementation Summary

**Date:** April 1, 2026  
**Status:** ✅ Complete  
**Version:** 1.0

---

## 🎯 Overview

Xây dựng một **Chatbot AI thông minh** kết hợp **Gemini API** với **Database** để hỗ trợ bán sách trực tuyến.

### Kết Quả

✅ Chatbot thông minh sử dụng Gemini AI  
✅ Truy cập context từ database  
✅ Hỗ trợ tiếng Việt  
✅ Rate limiting  
✅ Chat history  
✅ Responsive UI

---

## 📁 Files Created/Modified

### Backend Files

#### New Files

| File                            | Purpose                                                |
| ------------------------------- | ------------------------------------------------------ |
| `backend/requirements.txt`      | Python dependencies (Django, DRF, google-generativeai) |
| `backend/.env.example`          | Environment variables template                         |
| `backend/api/gemini_service.py` | **NEW** - Gemini AI integration logic                  |
| `backend/CHATBOT_SETUP.md`      | Detailed backend setup guide                           |

#### Modified Files

| File                   | Changes                                                        |
| ---------------------- | -------------------------------------------------------------- |
| `backend/api/views.py` | Replaced keyword-based chat with Gemini API integration        |
| `backend/api/views.py` | Updated import: removed `chat_service`, added `gemini_service` |
| `backend/api/views.py` | Improved chat endpoint with rate limiting & history support    |

### Frontend Files

#### Modified Files

| File                                     | Changes                                     |
| ---------------------------------------- | ------------------------------------------- |
| `frontend/src/services/geminiService.ts` | Added history formatting for Gemini backend |
| `frontend/src/services/geminiService.ts` | Improved error handling                     |

### Documentation Files

| File                        | Purpose                                             |
| --------------------------- | --------------------------------------------------- |
| `CHATBOT_QUICKSTART.md`     | **Complete setup guide** with architecture diagrams |
| `ADVANCED_CUSTOMIZATION.md` | Advanced features & customization guide             |
| `SETUP_CHECKLIST.html`      | Interactive checklist for setup verification        |
| `setup.sh`                  | **Automated setup script for Linux/Mac**            |
| `setup.bat`                 | **Automated setup script for Windows**              |
| `CHANGES.md`                | This file - summary of changes                      |

---

## 🔄 Architecture Changes

### Before (Keyword Matching)

```
User Input
    ↓
Keyword Pattern Matching (chat_service.py)
    ↓
Database Queries (basic)
    ↓
Hardcoded Responses
```

### After (Gemini AI + Database)

```
User Input
    ↓
Gemini API (get_gemini_reply)
    ↓
Build System Prompt:
    ├─ Database Context (books, categories, authors)
    ├─ Store Information
    ├─ Business Rules
    └─ User History
    ↓
Gemini AI Processing
    ↓
Natural Language Response
    ↓
Return with Chat History
```

---

## 🚀 Key Features Implemented

### 1. **Gemini AI Integration**

```python
# backend/api/gemini_service.py
- genai.configure(api_key=GEMINI_API_KEY)
- model = genai.GenerativeModel('gemini-1.5-flash')
- generate_content() with system prompt + context
```

### 2. **Dynamic Context Building**

```python
get_book_context()         # Last 50 books
get_category_context()     # All categories
get_author_context()       # All authors
get_store_context()        # Store info, policies
build_system_prompt()      # Combined prompt
```

### 3. **Conversation History**

```python
# frontend/src/services/geminiService.ts
history: [
    {role: 'user', text: 'Xin chào'},
    {role: 'model', text: '...response...'}
]
# Sent to backend for better context
```

### 4. **Rate Limiting**

```python
# backend/api/views.py
RATE_LIMIT = 12            # max 12 requests
RATE_WINDOW = 60           # per 60 seconds
_check_rate_limit()        # Thread-safe checking
```

### 5. **Error Handling**

```python
try:
    response = model.generate_content(...)
except Exception as e:
    return f"Xin lỗi: {str(e)}"
```

---

## 📊 Dependencies Added

### Backend (requirements.txt)

```
Django==5.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-dotenv==1.0.0
google-generativeai==0.3.0  # NEW - Gemini API
```

### Installation

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration

### Backend (.env)

```
GEMINI_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000/api
VITE_APP_URL=http://localhost:5173
```

> ⚠️ These values are NOT committed (in .gitignore)

---

## 📡 API Endpoint Changes

### Old Endpoint

```http
POST /api/chat/
{
  "message": "Xin chào"
}
```

### New Endpoint (Enhanced)

```http
POST /api/chat/
{
  "message": "Bạn có sách gì?",
  "history": [
    {"role": "user", "text": "Xin chào"},
    {"role": "model", "text": "Xin chào..."}
  ]
}

Response:
{
  "text": "Chúng tôi có ... (with database context)"
}
```

---

## 🎯 Capabilities

### What the Chatbot Can Do

✅ Find books by name, author, category  
✅ Show book prices and stock status  
✅ Recommend books based on category  
✅ Answer questions about shipping & returns  
✅ Explain store policies  
✅ Maintain conversation context  
✅ Respond in natural Vietnamese  
✅ Add emojis for better engagement

### Example Conversations

```
User: "Bạn có sách của Nguyễn Nhật Ánh không?"
Bot: "Có chứ! Chúng tôi có [3] cuốn sách của Nguyễn Nhật Ánh..."

User: "Sách nào rẻ nhất?"
Bot: "📚 Sách giá rẻ nhất hiện tại: ..."

User: "Giao hàng bao lâu?"
Bot: "🚚 Thông tin giao hàng: ..."
```

---

## 🧪 Testing

### Test Checklist

- [ ] Backend server starts: `python manage.py runserver`
- [ ] API returns responses: `GET /api/books/`
- [ ] Chat endpoint works: `POST /api/chat/`
- [ ] Gemini responds: Check response text
- [ ] History is used: Bot references previous messages
- [ ] Rate limiting works: >12 requests in 60s fails
- [ ] Frontend loads: http://localhost:5173
- [ ] Chat UI opens: Click chat icon
- [ ] Messages send: Type and submit
- [ ] Responses display: Bot replies appear

---

## 📈 Performance Considerations

### Optimization Implemented

- Database `.select_related()` for fewer queries
- Conversation history passed to backend
- 5-minute cache for book context (optional)
- Rate limiting to prevent abuse
- Lazy loading of database records

### Response Time

- Database queries: ~50-100ms
- Gemini API: ~500-2000ms (varies)
- Total: ~600-2100ms per request

---

## 🔄 Migration Path

### From Old System

1. Old chatbot used static keyword patterns
2. No real AI processing
3. Limited ability to understand context
4. Same responses for similar questions

### To New System

1. Dynamic AI-powered responses
2. Database-aware (knows actual inventory)
3. Understands natural language variations
4. Personalized responses with context

### Breaking Changes

❌ None - Old chat_service.py still exists  
✅ Can be used as fallback if needed  
✅ No database schema changes required

---

## 🚀 Deployment Checklist

### Before Going Live

- [ ] Test all chat interactions
- [ ] Verify API key is valid
- [ ] Check rate limiting works
- [ ] Monitor Gemini API quotas
- [ ] Setup logging
- [ ] Configure CORS properly
- [ ] Use HTTPS in production
- [ ] Set DEBUG=False
- [ ] Use environment variables
- [ ] Setup monitoring/alerting

### Deployment Steps

```bash
# Backend
1. Export requirements: pip freeze > requirements.txt
2. Deploy to server (Heroku, AWS, etc)
3. Set environment variables on server
4. Run migrations: python manage.py migrate
5. Collect static files: python manage.py collectstatic

# Frontend
1. Build: npm run build
2. Deploy dist/ to CDN or server
3. Update VITE_API_URL to point to backend
```

---

## 📚 Documentation Structure

1. **CHATBOT_QUICKSTART.md** - START HERE
   - Quick start in 5 minutes
   - Prerequisites check
   - Architecture overview
   - Troubleshooting

2. **backend/CHATBOT_SETUP.md** - Detailed Setup
   - Step-by-step backend setup
   - API documentation
   - Rate limiting info
   - Troubleshooting

3. **ADVANCED_CUSTOMIZATION.md** - For Developers
   - Customize system prompt
   - Add custom intents
   - Enhance context
   - Caching strategies
   - Streaming responses
   - Security improvements

4. **SETUP_CHECKLIST.html** - Interactive Progress
   - Track setup progress
   - Verify each step
   - Test chatbot
   - Save progress locally

5. **setup.sh** / **setup.bat** - Automated Setup
   - Single command setup
   - Installs dependencies
   - Creates venv
   - Guides through config

---

## 🐛 Known Issues & Solutions

### Issue: "GEMINI_API_KEY not found"

**Solution:** Check `.env` file exists and has the key  
**Workaround:** Set env var: `export GEMINI_API_KEY=...`

### Issue: "Connection refused"

**Solution:** Start Django: `python manage.py runserver`  
**Check:** Visit http://localhost:8000/api/books/

### Issue: CORS Error

**Solution:** Backend already has CORS enabled  
**Check:** frontend `.env` has `VITE_API_URL=http://localhost:8000/api`

### Issue: Slow Response

**Solution:** Gemini API takes 0.5-2s per request  
**Improvement:** Add response streaming (see advanced guide)

### Issue: API Rate Limit

**Solution:** Wait 60 seconds between >12 requests  
**Config:** Edit RATE_LIMIT in views.py

---

## 🎓 Learning Resources

- [Google Gemini API](https://ai.google.dev/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python google-generativeai](https://github.com/google/generative-ai-python)
- [React Hooks](https://react.dev/reference/react/hooks)
- [TypeScript](https://www.typescriptlang.org/docs/)

---

## ✨ Future Enhancements

### Planned Features

- [ ] User authentication for personalized recommendations
- [ ] Chat history storage in database
- [ ] Streaming responses for faster perceived performance
- [ ] Image recognition for book covers
- [ ] Multi-language support
- [ ] Admin dashboard for chat analytics
- [ ] Custom knowledge base for frequent questions
- [ ] Integration with payment systems
- [ ] Voice input/output support
- [ ] Mobile app version

### Optional Improvements

```python
# Redis Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Database Indexing
class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey(..., db_index=True)

# Async Tasks
@shared_task
def generate_chat_response(message: str):
    # Celery task for long-running tasks
    pass
```

---

## 📞 Support & Feedback

If you encounter any issues:

1. Check documentation files
2. Review the checklist
3. Check browser console for errors
4. Review Django/Gemini API logs
5. Test with curl/Postman

---

## 📄 License & Credits

- **Framework:** Django + React + Gemini AI
- **Author:** Development Team
- **Version:** 1.0
- **Last Updated:** April 1, 2026

---

## ✅ Verification Checklist

- [x] Gemini API integrated
- [x] Database context implemented
- [x] Rate limiting added
- [x] Chat history support
- [x] Error handling improved
- [x] Documentation complete
- [x] Setup scripts created
- [x] Frontend updated
- [x] Environment variables configured
- [x] Testing guide provided

---

**🎉 Implementation Complete!**

Start with `CHATBOT_QUICKSTART.md` for quick setup.
