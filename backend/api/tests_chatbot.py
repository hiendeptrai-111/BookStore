from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from api.gemini_service import _is_personal_order_request, _normalize_text, get_gemini_reply
from api.views import chat


class GeminiServiceChatbotTest(SimpleTestCase):
    def test_normalize_text_handles_vietnamese_d(self):
        normalized = _normalize_text("don dat hang cua toi".replace("d", "đ", 1))
        self.assertEqual(normalized, "don dat hang cua toi")
        self.assertTrue(_is_personal_order_request(normalized))

    def test_get_gemini_reply_builds_prompt_from_database_context(self):
        history = [{"role": "user", "text": "Doraemon"}]
        database_context = {
            "matched_books": [
                {
                    "title": "Doraemon Tap 1",
                    "author": "Fujiko F. Fujio",
                    "price": 25000,
                    "stock": 8,
                }
            ]
        }
        mock_model = MagicMock()
        mock_model.generate_content.return_value = SimpleNamespace(text="Sach con hang.")

        with patch("api.gemini_service.build_runtime_context", return_value=database_context) as build_context:
            with patch("api.gemini_service.check_gemini_api_key"):
                with patch("api.gemini_service.model", mock_model):
                    reply = get_gemini_reply("Doraemon con hang khong?", history, user_id=7)

        self.assertEqual(reply, "Sach con hang.")
        build_context.assert_called_once_with("Doraemon con hang khong?", history, 7)
        prompt = mock_model.generate_content.call_args.args[0]
        self.assertIn("DATABASE_RESULT", prompt)
        self.assertIn("Doraemon Tap 1", prompt)

    def test_get_gemini_reply_falls_back_to_database_answer_when_model_unavailable(self):
        database_context = {
            "matched_books": [
                {
                    "title": "Clean Code",
                    "author": "Robert C. Martin",
                    "price": 99000,
                    "stock": 4,
                }
            ],
            "policies": {},
        }

        with patch("api.gemini_service.build_runtime_context", return_value=database_context):
            with patch("api.gemini_service.model", None):
                reply = get_gemini_reply("Clean Code gia bao nhieu?")

        self.assertIn("Clean Code", reply)
        self.assertIn("99,000", reply)

    def test_get_gemini_reply_reports_not_found_for_specific_search_without_match(self):
        database_context = {
            "matched_books": [],
            "matched_categories": [],
            "matched_authors": [],
            "top_sellers": [],
            "store_stats": None,
            "user_orders": None,
            "policies": {},
            "search_terms": ["Doraemon"],
        }

        with patch("api.gemini_service.build_runtime_context", return_value=database_context):
            with patch("api.gemini_service.model", None):
                reply = get_gemini_reply("Doraemon con hang khong?")

        self.assertIn("doraemon", reply.lower())
        self.assertIn("database", reply.lower())
        self.assertIn("Doraemon", reply)

    def test_get_gemini_reply_uses_natural_greeting_for_hello(self):
        database_context = {
            "matched_books": [],
            "matched_categories": [],
            "matched_authors": [],
            "top_sellers": [],
            "store_stats": None,
            "user_orders": None,
            "policies": {},
            "search_terms": ["hello"],
        }

        with patch("api.gemini_service.build_runtime_context", return_value=database_context):
            with patch("api.gemini_service.model", None):
                with patch("api.gemini_service.get_chat_reply", return_value="Xin chao!"):
                    reply = get_gemini_reply("hello")

        self.assertIn("xin chao", reply.lower())

    def test_get_gemini_reply_requires_login_for_personal_order_lookup(self):
        database_context = {
            "matched_books": [],
            "matched_categories": [],
            "matched_authors": [],
            "top_sellers": [],
            "store_stats": None,
            "user_orders": None,
            "policies": {},
            "search_terms": [],
            "intent": {"personal_order_request": True},
        }

        with patch("api.gemini_service.build_runtime_context", return_value=database_context):
            with patch("api.gemini_service.model", None):
                reply = get_gemini_reply("kiem tra cac don dat hang cua toi")

        self.assertIn("\u0111\u0103ng nh\u1eadp", reply.lower())


class ChatEndpointTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_chat_endpoint_uses_authenticated_user_for_chat_context(self):
        request = self.factory.post(
            "/api/chat/",
            {"message": "Don hang cua toi the nao?", "history": []},
            format="json",
        )

        with patch("api.views._check_rate_limit", return_value=True):
            with patch("api.views.get_current_customer", return_value=SimpleNamespace(customer_id=12)):
                with patch("api.views.get_gemini_reply", return_value="ok") as get_reply:
                    response = chat(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["text"], "ok")
        get_reply.assert_called_once_with("Don hang cua toi the nao?", [], user_id=12)
