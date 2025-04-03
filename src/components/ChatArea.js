import React, { useState, useEffect, useRef } from 'react';
import './ChatArea.css';
import chatbotImage from '../assets/chatbot.png'; 

function ChatArea({ messages, onSendMessage }) {
  const [input, setInput] = useState('');
  const chatBoxRef = useRef(null);

  const handleSend = () => {
    if (input.trim() === '') return;
    onSendMessage(input);
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTo(0, chatBoxRef.current.scrollHeight);
    }
  }, [messages]);

  return (
    <div className="chat-area">
      <div className="chat-box" ref={chatBoxRef}>
        {messages.length === 0 ? (
          <p className="placeholder-text">무엇이든 물어보세요.</p>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-row ${msg.sender === 'user' ? 'user' : 'bot'}`}
            >
              {msg.sender === 'user' && <div className="user-initial">U</div>}
              {msg.sender === 'bot' && (
                <img
                  src={chatbotImage}
                  alt="ChatBot"
                  className="bot-avatar-image"
                />
              )}
              <div className="message-bubble">{msg.text}</div>
            </div>
          ))
        )}
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="메시지를 입력하세요..."
        />
        <button className="send-button" onClick={handleSend}>
          전송
        </button>
      </div>
    </div>
  );
}

export default ChatArea;
