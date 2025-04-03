import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import DeleteModal from './components/DeleteModal';
import './index.css';

function App() {
  const [chatList, setChatList] = useState([]);
  const [chatMessages, setChatMessages] = useState({});
  const [currentChatId, setCurrentChatId] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null);

  const handleNewChat = () => {
    const newId = Date.now();
    const title = `새 대화 ${chatList.length + 1}`;
    const newChat = { id: newId, title, message: '' };

    setChatList([...chatList, newChat]);
    setChatMessages({ ...chatMessages, [newId]: [] });
    setCurrentChatId(newId);
  };

  const handleSelectChat = (id) => setCurrentChatId(id);

  const handleDeleteChat = (id) => {
    setChatToDelete(id);
    setModalOpen(true);
  };

  const handleConfirmDelete = () => {
    setChatList((prev) => prev.filter((chat) => chat.id !== chatToDelete));
    const updatedMessages = { ...chatMessages };
    delete updatedMessages[chatToDelete];
    setChatMessages(updatedMessages);
    if (currentChatId === chatToDelete) setCurrentChatId(null);
    setModalOpen(false);
    setChatToDelete(null);
  };

  const handleCancelDelete = () => {
    setModalOpen(false);
    setChatToDelete(null);
  };

  const handleMessageSend = (text) => {
    if (!currentChatId) return;

    const newMessage = { id: Date.now(), text, sender: 'user' };
    const botReply = { id: Date.now() + 1, text: '챗봇 응답 준비 중...', sender: 'bot' };

    const updated = [...(chatMessages[currentChatId] || []), newMessage, botReply];
    setChatMessages({ ...chatMessages, [currentChatId]: updated });

    setChatList((prev) =>
      prev.map((chat) =>
        chat.id === currentChatId ? { ...chat, message: text } : chat
      )
    );
  };

  return (
    <div className="app">
      <Header />
      <div className="main">
        <Sidebar
          chatList={chatList}
          currentChatId={currentChatId}
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
        />
        <ChatArea
          messages={chatMessages[currentChatId] || []}
          onSendMessage={handleMessageSend}
        />
      </div>

      {modalOpen && (
        <DeleteModal
          onConfirm={handleConfirmDelete}
          onCancel={handleCancelDelete}
        />
      )}
    </div>
  );
}

export default App;