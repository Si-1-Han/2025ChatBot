let API_URL = '';

async function loadConfig() {
  const res = await fetch('/config');
  const data = await res.json();
  API_URL = data.API_URL;
  document.documentElement.style.setProperty('--theme-color', data.THEME_COLOR);
}

document.addEventListener('DOMContentLoaded', () => {
  loadConfig();

  const chatBox = document.getElementById('chat-box');
  const sendBtn = document.getElementById('send-btn');
  const input = document.getElementById('user-input');
  const chatList = document.getElementById('chat-list');
  const newChatBtn = document.getElementById('new-chat');
  const modal = document.getElementById('delete-modal');
  const modalTitle = document.getElementById('delete-title');
  const closeModal = document.querySelector('.close-btn');
  const cancelDelete = document.getElementById('cancel-delete');
  const confirmDelete = document.getElementById('confirm-delete');
  const toggleDark = document.getElementById('toggle-dark');

  let currentUser = localStorage.getItem('user_id') || 'user_' + Math.random().toString(36).substring(2, 9);
  localStorage.setItem('user_id', currentUser);

  let selectedChatId = localStorage.getItem('selected_chat_id');

  function addMessage(type, content) {
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = content;
    msg.appendChild(bubble);
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage('user', text);
    input.value = '';

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: currentUser, message: text, chat_id: selectedChatId })
      });

      const data = await res.json();
      selectedChatId = data.chat_id;
      localStorage.setItem('selected_chat_id', selectedChatId);

      let botMsg = `<b>📌 요약:</b><br>${data.summary}<br><br>`;
      if (data.results?.length) {
        botMsg += `<b>📰 관련 뉴스</b><ul>`;
        data.results.forEach(item => {
          botMsg += `<li><a href="${item.link}" target="_blank">${item.title}</a></li>`;
        });
        botMsg += `</ul>`;
      }

      addMessage('bot', botMsg);
      loadChats();
    } catch (err) {
      console.error('❌ chat error:', err);
      addMessage('bot', '❌ 서버 오류가 발생했습니다.');
    }
  }

  async function loadChats() {
    try {
      const res = await fetch(`${API_URL}/chats?user_id=${currentUser}`);
      const data = await res.json();
      chatList.innerHTML = '';

      if (data.status === 'success') {
        data.chats.forEach(chat => {
          const li = document.createElement('li');
          li.innerHTML = `<span>${chat.title}</span><button class="delete-btn" data-id="${chat.id}"><i class="fas fa-trash"></i></button>`;
          li.addEventListener('click', () => {
            selectedChatId = chat.id;
            localStorage.setItem('selected_chat_id', selectedChatId);
            loadChatHistory(chat.id);
          });
          chatList.appendChild(li);
        });

        if (!selectedChatId && data.chats.length > 0) {
          selectedChatId = data.chats[0].id;
          localStorage.setItem('selected_chat_id', selectedChatId);
          loadChatHistory(selectedChatId);
        }
      }
    } catch (err) {
      console.error('❌ loadChats error:', err);
    }
  }

  async function loadChatHistory(chatId) {
    try {
      const res = await fetch(`${API_URL}/history/${chatId}`);
      const data = await res.json();
      chatBox.innerHTML = '';
      data.history.forEach(entry => {
        addMessage('user', entry.message);
        addMessage('bot', entry.response);
      });
    } catch (err) {
      console.error('❌ loadChatHistory error:', err);
    }
  }

  newChatBtn.addEventListener('click', () => {
    chatBox.innerHTML = '';
    selectedChatId = null;
    localStorage.removeItem('selected_chat_id');
    addMessage('bot', '안녕하세요! 챗봇입니다. 무엇을 도와드릴까요?');
  });

  chatList.addEventListener('click', e => {
    if (e.target.closest('.delete-btn')) {
      e.stopPropagation();
      const id = e.target.closest('.delete-btn').dataset.id;
      modal.dataset.chatId = id;
      modal.style.display = 'flex';
    }
  });

  confirmDelete.addEventListener('click', async () => {
    const id = modal.dataset.chatId;
    await fetch(`${API_URL}/delete/${id}`, { method: 'DELETE' });
    modal.style.display = 'none';
    if (id === selectedChatId) {
      selectedChatId = null;
      localStorage.removeItem('selected_chat_id');
      chatBox.innerHTML = '';
      addMessage('bot', '대화가 삭제되었어요. 새로운 대화를 시작해보세요.');
    }
    loadChats();
  });

  cancelDelete.addEventListener('click', () => modal.style.display = 'none');
  closeModal.addEventListener('click', () => modal.style.display = 'none');

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  toggleDark.addEventListener('click', () => {
    document.body.classList.toggle('dark');
  });

  loadChats();
});
