# 🤖 Chatbot với Gemini AI - Setup Guide

## 📋 Prerequisite

Bạn cần có:

- Python 3.8+
- Django 5.2.7
- Google Gemini API Key (từ https://ai.google.dev)

## 🚀 Setup Steps

### 1. Lấy Gemini API Key

1. Truy cập https://ai.google.dev
2. Nhấp **Get API Key**
3. Đăng nhập với Google Account
4. Copy API key của bạn

### 2. Cấu Hình Environment

**Linux/Mac:**

```bash
cd backend
cp .env.example .env
# Edit .env và thêm Gemini API key
nano .env
```

**Windows (PowerShell):**

```powershell
cd backend
Copy-Item .env.example .env
# Edit .env và thêm Gemini API key
notepad .env
```

Nội dung .env file:

```
GEMINI_API_KEY=your_actual_api_key_here
DEBUG=True
```

### 3. Cài Đặt Dependencies

```bash
cd backend

# Tạo Python virtual environment (nếu chưa có)
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Cài đặt packages
pip install -r requirements.txt
```

### 4. Khởi Chạy Server

```bash
python manage.py runserver
```

Server sẽ chạy tại http://localhost:8000

## 📡 API Endpoint

**Chat Endpoint:**

```
POST /api/chat/
Content-Type: application/json

{
  "message": "Bạn có sách của Nguyễn Nhật Ánh không?",
  "history": [
    {"role": "user", "text": "Xin chào"},
    {"role": "model", "text": "Chào bạn!"}
  ]
}
```

**Response:**

```json
{
  "text": "Gemini's response with database context..."
}
```

## 🔧 Tính Năng Chatbot

Chatbot được tích hợp Gemini AI với các khả năng:

✅ **Tìm kiếm sách thông minh** - Tìm theo tên, tác giả, thể loại, mô tả
✅ **Gợi ý sách** - Gợi ý dựa trên sở thích
✅ **Thông tin giá cả** - Hỏi giá sách, tìm sách rẻ nhất, đắt nhất
✅ **Tình trạng hàng** - Kiểm tra sách còn hàng hay hết
✅ **Hướng dẫn mua hàng** - Giải thích cách đặt hàng, thanh toán, giao hàng
✅ **Chính sách cửa hàng** - Giải thích về đổi trả, bảo hành
✅ **Ngôn ngữ tự nhiên** - Trả lời bằng tiếng Việt tự nhiên với emoji

## 📊 Database Context

Chatbot tự động lấy thông tin từ database:

- **Sách** - Danh sách sách với tên, tác giả, giá, tồn kho
- **Thể loại** - Danh sách thể loại
- **Tác giả** - Danh sách tác giả
- **Cửa hàng** - Thông tin chung, chính sách, phí ship

## ⚠️ Rate Limiting

API có giới hạn 12 requests/60 giây để tránh lạm dụng.

## 🐛 Troubleshooting

### Lỗi: "GEMINI_API_KEY không được set"

**Giải pháp:** Kiểm tra .env file có GEMINI_API_KEY không

### Lỗi: "HTTP 400 - Tin nhắn không được để trống"

**Giải pháp:** Đảm bảo gửi message field trong request body

### Lỗi: "Quá nhiều yêu cầu"

**Giải pháp:** Chờ một chút trước khi gửi yêu cầu tiếp theo

### Lỗi: Connection refused (localhost:8000)

**Giải pháp:** Đảm bảo backend server đang chạy

## 📝 File Structure

```
backend/
├── .env                    # Configuration (GEMINI_API_KEY)
├── .env.example           # Template
├── requirements.txt       # Python dependencies
├── manage.py
├── api/
│   ├── views.py          # Chat endpoint
│   ├── gemini_service.py # Gemini AI logic
│   ├── chat_service.py   # Deprecated (keyword matching)
│   └── models.py         # Database models
└── backend/
    └── settings.py       # Django settings
```

## 🔄 Architecture

```
Frontend (React/TypeScript)
    ↓ POST /api/chat/
Backend (Django)
    ↓ views.chat()
    ↓ get_gemini_reply()
    ↓ build_system_prompt() + get_*_context()
    ↓ Fetch from Database
    ↓ Call Gemini API
    ↓ Gemini AI Response
    ↓ Return to Frontend
```

## 📚 Resources

- [Google Gemini API Docs](https://ai.google.dev)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Google Generative AI Python](https://github.com/google/generative-ai-python)

## ✨ Next Steps

1. ✅ Setup Gemini API Key
2. ✅ Install requirements
3. ✅ Start Django server
4. ✅ Test chatbot through frontend

Happy chatting! 🚀
