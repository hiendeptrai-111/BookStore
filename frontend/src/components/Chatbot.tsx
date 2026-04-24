import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2, Minimize2, Maximize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Link } from 'react-router-dom';
import { getChatResponse } from '../services/geminiService';
import { ChatMessage, ChatBookCard } from '../types';
import { formatCurrency } from '../types';

function BookCard({ book }: { book: ChatBookCard }) {
  const imgSrc = book.image_url || `https://picsum.photos/seed/book${book.id}/400/600`;
  return (
    <Link
      to={`/books/${book.id}`}
      className="flex items-center gap-2 p-2 bg-gray-50 border border-gray-200 rounded-xl hover:bg-indigo-50 hover:border-indigo-300 transition-colors group"
    >
      <img
        src={imgSrc}
        alt={book.title}
        className="w-12 h-16 object-cover rounded-lg shrink-0 shadow-sm"
        onError={(e) => {
          (e.target as HTMLImageElement).src = `https://picsum.photos/seed/book${book.id}/400/600`;
        }}
      />
      <div className="min-w-0 flex-1">
        <p className="text-xs font-semibold text-gray-800 leading-tight line-clamp-2 group-hover:text-indigo-700">
          {book.title}
        </p>
        <p className="text-xs text-gray-500 mt-0.5 truncate">{book.author}</p>
        <p className="text-xs font-bold text-indigo-600 mt-1">{formatCurrency(book.price)}</p>
        {book.stock === 0 && (
          <span className="text-[10px] text-red-500 font-medium">Hết hàng</span>
        )}
      </div>
    </Link>
  );
}

export const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'model',
      text: 'Chào bạn! Tôi là trợ lý ảo của Remix Bookstore.\nBạn có thể hỏi tôi về sách, giá cả, hay tìm sách theo tên nhé! 😊',
      books: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage, books: [] }]);
    setIsLoading(true);

    const response = await getChatResponse(messages, userMessage);

    setMessages(prev => [...prev, {
      role: 'model',
      text: response.text,
      books: response.books,
    }]);
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col items-end">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{
              opacity: 1,
              scale: 1,
              y: 0,
              height: isMinimized ? '64px' : '520px',
            }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col mb-4"
          >
            {/* Header */}
            <div className="bg-indigo-600 p-4 text-white flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="font-bold text-sm">Hỗ trợ trực tuyến</span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1 hover:bg-white/10 rounded-lg transition-colors"
                >
                  {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {!isMinimized && (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] space-y-2 ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                        {/* Text bubble */}
                        <div className={`p-3 rounded-2xl text-sm whitespace-pre-line ${
                          msg.role === 'user'
                            ? 'bg-indigo-600 text-white rounded-tr-none shadow-sm'
                            : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none shadow-sm'
                        }`}>
                          {msg.text}
                        </div>

                        {/* Book cards */}
                        {msg.books && msg.books.length > 0 && (
                          <div className="w-full space-y-2">
                            {msg.books.map(book => (
                              <BookCard key={book.id} book={book} />
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-gray-100 p-3 rounded-2xl rounded-tl-none shadow-sm flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                        <span className="text-xs text-gray-500 italic">Đang trả lời...</span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Quick suggestions */}
                <div className="px-3 py-2 bg-white border-t border-gray-100 flex gap-2 overflow-x-auto shrink-0">
                  {['Sách mắc nhất', 'Sách rẻ nhất', 'Đắc Nhân Tâm'].map(hint => (
                    <button
                      key={hint}
                      onClick={() => { setInput(hint); }}
                      className="text-xs whitespace-nowrap px-2 py-1 rounded-full border border-indigo-200 text-indigo-600 hover:bg-indigo-50 transition-colors shrink-0"
                    >
                      {hint}
                    </button>
                  ))}
                </div>

                {/* Input */}
                <div className="p-4 bg-white border-t border-gray-100 shrink-0">
                  <div className="relative">
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Nhập tin nhắn..."
                      rows={1}
                      className="w-full pl-4 pr-12 py-3 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 resize-none transition-all"
                    />
                    <button
                      onClick={handleSend}
                      disabled={!input.trim() || isLoading}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg disabled:opacity-50 transition-all"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => {
          setIsOpen(true);
          setIsMinimized(false);
        }}
        className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all ${
          isOpen ? 'bg-gray-100 text-gray-400 opacity-0 pointer-events-none' : 'bg-indigo-600 text-white hover:bg-indigo-700'
        }`}
      >
        <MessageCircle className="w-6 h-6" />
      </motion.button>
    </div>
  );
};
