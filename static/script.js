let API_URL = '';

// 설정을 불러오되, 실패 시 fallback 주소 지정
async function loadConfig() {
    try {
        const response = await fetch('/config');
        const data = await response.json();
        API_URL = data.API_URL || 'http://127.0.0.1:5000/api'; // fallback
        document.documentElement.style.setProperty('--theme-color', data.THEME_COLOR);
    } catch (error) {
        console.error('Error fetching config:', error);
        API_URL = 'http://127.0.0.1:5000/api'; // fallback 기본값
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadConfig();

    const userId = 'user_' + Math.random().toString(36).substring(2, 9);
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const resetBtn = document.getElementById('reset-btn');

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        addMessageToUI('user', message);
        userInput.value = '';

        const typingIndicator = addTypingIndicator();

        try {
            if (!API_URL) throw new Error('API_URL이 설정되지 않았습니다.');

            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, user_id: userId })
            });
            const data = await response.json();
            chatMessages.removeChild(typingIndicator);
            addMessageToUI('bot', data.response);
        } catch (error) {
            console.error('Error:', error);
            chatMessages.removeChild(typingIndicator);
            addMessageToUI('bot', '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.');
        }
    }

    function addMessageToUI(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type === 'user' ? 'user-message' : 'bot-message');
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.innerText = content;
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message');
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingIndicator.appendChild(dot);
        }
        typingDiv.appendChild(typingIndicator);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typingDiv;
    }

    async function resetConversation() {
        try {
            if (!API_URL) throw new Error('API_URL이 설정되지 않았습니다.');

            await fetch(`${API_URL}/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            chatMessages.innerHTML = '';
            addMessageToUI('bot', '안녕하세요! 고객 지원 챗봇입니다. 어떤 도움이 필요하신가요?');
        } catch (error) {
            console.error('Error resetting conversation:', error);
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    resetBtn.addEventListener('click', resetConversation);
    userInput.addEventListener('focus', () => {
        setTimeout(() => {
            window.scrollTo(0, document.body.scrollHeight);
        }, 500);
    });
});
