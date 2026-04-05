# 🚀 BookStore Chatbot - Gemini AI Integration

**Một chatbot thông minh kết hợp Gemini AI + Database để hỗ trợ bán sách trực tuyến.**

## ✨ Tính Năng

- 🤖 **Gemini AI Integration** - Trả lời tự nhiên bằng tiếng Việt
- 📚 **Database Context** - Tự động lấy thông tin sách từ database
- 🔍 **Tìm Kiếm Thông Minh** - Tìm theo tên, tác giả, thể loại
- 💬 **Conversation History** - Lưu lịch chat để context tốt hơn
- ⚡ **Rate Limiting** - Ngăn lạm dụng API
- 📱 **Responsive UI** - Giao diện đẹp, friendly

## 🛠️ Tech Stack

**Backend:**

- Django 5.2.7 + Django REST Framework
- Google Generative AI SDK
- Python 3.8+

**Frontend:**

- React 18 + TypeScript
- Vite
- Framer Motion (animations)
- Lucide React (icons)

**Database:**

- SQLite (có thể nâng cấp PostgreSQL)

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API Key (miễn phí từ https://ai.google.dev)

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# 1. Tạo virtual environment
python -m venv venv

# 2. Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Cài packages
pip install -r requirements.txt

# 4. Setup .env
cp .env.example .env
# Edit .env và thêm GEMINI_API_KEY
# GEMINI_API_KEY=your_key_here

# 5. Chạy migrations
python manage.py migrate

# 6. Khởi động server
python manage.py runserver
# Server sẽ chạy tại http://localhost:8000
```

### Frontend Setup

```bash
cd frontend

# 1. Cài packages
npm install

# 2. Setup .env (nếu cần)
cp .env.example .env
# VITE_API_URL=http://localhost:8000/api

# 3. Khởi động dev server
npm run dev
# Frontend sẽ chạy tại http://localhost:5173
```

## 🔑 Lấy Gemini API Key

1. Truy cập [https://ai.google.dev](https://ai.google.dev)
2. Nhấp **"Get API Key"**
3. Chọn project → **"Create API key"**
4. Copy key và thêm vào `.env`:
   ```
   GEMINI_API_KEY=YOUR_API_KEY_HERE
   ```

> ⚠️ **Bảo mật:** Không commit `.env` lên Git. Nó được .gitignore từ trước.

## 📡 API Documentation

### Chat Endpoint

```http
POST http://localhost:8000/api/chat/
Content-Type: application/json
```

**Request Body:**

```json
{
  "message": "Bạn có sách nào về thiếu nhi không?",
  "history": [
    { "role": "user", "text": "Xin chào" },
    { "role": "model", "text": "Xin chào! Tôi là trợ lý BookStore..." }
  ]
}
```

**Response:**

```json
{
  "text": "Chúng tôi có rất nhiều sách thiếu nhi tuyệt vời..."
}
```

**Error Response:**

```json
{
  "error": "Tin nhắn không được để trống"
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - User input → state management → API call              │
└────────────────────┬────────────────────────────────────┘
                     │ POST /api/chat/
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  Backend (Django)                        │
├─────────────────────────────────────────────────────────┤
│ views.py::chat()                                         │
│  ├─ Get message + history                               │
│  ├─ Call get_gemini_reply()                             │
│  └─ Return response                                      │
├─────────────────────────────────────────────────────────┤
│ gemini_service.py::get_gemini_reply()                    │
│  ├─ build_system_prompt()                               │
│  │  ├─ get_book_context()        → Query DB Books       │
│  │  ├─ get_category_context()    → Query DB Categories  │
│  │  ├─ get_author_context()      → Query DB Authors     │
│  │  └─ get_store_context()       → Store info + policies│
│  ├─ Format conversation history                         │
│  ├─ Call genai.GenerativeModel.generate_content()       │
│  └─ Return AI response                                  │
├─────────────────────────────────────────────────────────┤
│                   Database (SQLite)                      │
│  - Books, Authors, Categories, Orders, Customers        │
└─────────────────────────────────────────────────────────┘
```

## 📊 Database Schema

Chatbot sử dụng các table:

| Table            | Fields                                                            | Mục đích       |
| ---------------- | ----------------------------------------------------------------- | -------------- |
| `api_books`      | title, price, stock_quantity, description, author_id, category_id | Danh sách sách |
| `api_authors`    | full_name, nationality, bio                                       | Tác giả        |
| `api_categories` | name                                                              | Thể loại sách  |
| `api_orders`     | status, total_amount, address, order_date                         | Đơn hàng       |
| `api_customers`  | full_name, email, role                                            | Khách hàng     |

## 🔒 Rate Limiting

API giới hạn 12 requests/60 giây:

```python
RATE_LIMIT = 12        # max requests
RATE_WINDOW = 60       # per 60 seconds
```

**Response khi exceed:**

```json
{
  "error": "Quá nhiều yêu cầu. Vui lòng chờ một chút.",
  "status": 429
}
```

## 🎨 System Prompt

Chatbot được cấu hình với comprehensive system prompt:

```
Bạn là một trợ lý AI thân thiện của BookStore - một cửa hàng bán sách trực tuyến.

[THÔNG TIN CỬA HÀNG]
[DANH MỤC SÁCH]
[DANH SÁCH TÁC GIẢ]
[SÁCH HIỆN CÓ]

HƯỚNG DẪN HOẠT ĐỘNG:
1. Trợ lý bán hàng thân thiện, chuyên nghiệp
2. Trả lời bằng tiếng Việt, natural
3. Giúp tìm sách, gợi ý, hướng dẫn mua
4. Luôn lịch sự, vui vẻ, sẵn sàng giúp
5. Dùng emoji để làm câu trả lời sinh động
```

## 🐛 Troubleshooting

### ❌ "GEMINI_API_KEY không được set"

```
Giải pháp: Kiểm tra .env file có khóa này không
export GEMINI_API_KEY=your_key_here
```

### ❌ "HTTP 400 - Tin nhắn không được để trống"

```
Giải pháp: Đảm bảo request body có "message" field
```

### ❌ "Connection refused localhost:8000"

```
Giải pháp:
1. Bắt đầu Django server: python manage.py runserver
2. Kiểm tra VITE_API_URL trong .env frontend
```

### ❌ "CORS error từ Frontend"

```
Giải pháp: Backend đã cấu hình CORS, kiểm tra settings.py
ALLOWED_HOSTS = ['*']  # dev only
CORS_ALLOWED_ORIGINS = ['http://localhost:5173', ...]
```

### ❌ Gemini API error "Invalid API Key"

```
Giải pháp:
1. Lấy key mới từ https://ai.google.dev
2. Kiểm tra key không có khoảng trắng
3. Restart Django server
```

## 📚 File Structure

```
BookStore/
├── backend/
│   ├── .env                 ← Add GEMINI_API_KEY here
│   ├── .env.example
│   ├── requirements.txt
│   ├── manage.py
│   ├── CHATBOT_SETUP.md     ← Detailed setup guide
│   ├── api/
│   │   ├── views.py         ← Chat endpoint
│   │   ├── gemini_service.py ← Gemini logic
│   │   ├── chat_service.py  ← Deprecated keyword matching
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── urls.py
│   └── backend/
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── frontend/
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── services/
│       │   └── geminiService.ts ← Updated API call
│       ├── components/
│       │   └── Chatbot.tsx      ← Chat UI
│       └── ...
└── README.md (this file)
```

## 🔄 Workflow

1. User gõ tin nhắn trong Chatbot UI → `Chatbot.tsx`
2. Component call `getChatResponse()` → `geminiService.ts`
3. API POST `/api/chat/` → `views.chat()` → `views.py`
4. Backend fetch database context + build prompt
5. Call Gemini API với prompt + history
6. Return response → Frontend
7. Display message with streaming animation

## 🚀 Deployment

### Heroku / Render

1. Tạo file `runtime.txt`:

   ```
   python-3.11.4
   ```

2. Set environment variables:

   ```
   heroku config:set GEMINI_API_KEY=your_key
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

### AWS / Google Cloud

1. Setup environment variables
2. Build Docker image
3. Deploy to cloud

## 📝 Environment Variables

**Backend (.env):**

```
GEMINI_API_KEY=sk-...
DEBUG=True
SECRET_KEY=django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

**Frontend (.env):**

```
VITE_API_URL=http://localhost:8000/api
VITE_APP_URL=http://localhost:5173
```

## 🔐 Security Notes

- ❌ **Never** commit `.env` file to Git
- ❌ **Never** expose API key in frontend code
- ✅ Always use environment variables
- ✅ Implement rate limiting (already done)
- ✅ Validate input on backend
- ✅ Use HTTPS in production

## 📈 Performance Tips

1. **Database Queries**: Model `.select_related()` để giảm SQL queries
2. **Caching**: Dùng 5-minute cache cho danh sách sách
3. **Pagination**: Limit books list to 50 trong context
4. **API Key**: Store securely in environment

## 🚦 Status Codes

- `200` - Success
- `400` - Bad request (empty message)
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Server error

## 📞 Support

| Issue            | Solution                                     |
| ---------------- | -------------------------------------------- |
| API Key error    | Tạo key mới tại ai.google.dev                |
| DB connection    | Chạy `python manage.py migrate`              |
| Port conflict    | Thay port: `python manage.py runserver 8001` |
| Module not found | Cài lại: `pip install -r requirements.txt`   |

## 🎯 Next Steps

- [ ] Setup Gemini API Key
- [ ] Install backend requirements
- [ ] Install frontend requirements
- [ ] Run migrations
- [ ] Start backend server
- [ ] Start frontend server
- [ ] Test chatbot
- [ ] Deploy to production

## 📚 Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev)
- [REST API Best Practices](https://restfulapi.net/)

---

**Happy Coding! 🚀**

_Nếu có vấn đề, kiểm tra logs hoặc tạo issue._
