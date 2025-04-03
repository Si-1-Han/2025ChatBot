import React from 'react';
import './Sidebar.css';

function Sidebar({ chatList, currentChatId, onNewChat, onSelectChat, onDeleteChat }) {
  return (
    <aside className="sidebar">
      <button className="new-chat-button" onClick={onNewChat}>
        + New Chat
      </button>
      <div className="chat-list">
        {chatList.map((chat) => (
          <div
            key={chat.id}
            className={`chat-item ${chat.id === currentChatId ? 'active' : ''}`}
            onClick={() => onSelectChat(chat.id)}
          >
            <div className="chat-title">{chat.title}</div>
            <div className="chat-message">{chat.message}</div>
            <button
              className="delete-button"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;