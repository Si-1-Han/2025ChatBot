let API_URL = '';
let userId = '';
let conversations = {};

function saveConversation(title, messages) {
    conversations[title] = messages;
    localStorage.setItem('conversations', JSON.stringify(conversations));
    updateSidebar();
}

function loadConversation(title) {
    const data = conversations[title];
    if (!data) return;

    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    data.forEach(msg => {
        addMessageToUI(msg.type, msg.text);
    });
}

function updateSidebar() {
    const list = document.getElementById('conversation-list');
    list.innerHTML = '';

    Object.keys(conversations).forEach(title => {
        const li = document.createElement('li');

        const span = document.createElement('span');
        span.textContent = title;
        span.style.flex = '1';
        span.style.cursor = 'pointer';
        span.addEventListener('click', () => loadConversation(title));

        const delBtn = document.createElement('button');
        delBtn.innerHTML = '🗑';
        delBtn.title = '삭제';
        delBtn.style.background = 'none';
        delBtn.style.border = 'none';
        delBtn.style.color = '#999';
        delBtn.style.cursor = 'pointer';
        delBtn.style.fontSize = '14px';
        delBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // 대화 불러오기 방지
            if (confirm(`"${title}" 대화를 삭제할까요?`)) {
                delete conversations[title];
                localStorage.setItem('conversations', JSON.stringify(conversations));
                updateSidebar();
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.innerHTML = '';
            }
        });

        li.style.display = 'flex';
        li.style.justifyContent = 'space-between';
        li.style.alignItems = 'center';

        li.appendChild(span);
        li.appendChild(delBtn);
        list.appendChild(li);
    });
}


function loadFromLocalStorage() {
    conversations = JSON.parse(localStorage.getItem('conversations') || '{}');
    updateSidebar();
}

function toggleDarkMode() {
    document.body.classList.toggle('dark');
    localStorage.setItem('darkmode', document.body.classList.contains('dark'));
}

document.addEventListener('DOMContentLoaded', () => {
    loadFromLocalStorage();
    userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substring(2, 9);
    localStorage.setItem('userId', userId);

    if (localStorage.getItem('darkmode') === 'true') {
        document.body.classList.add('dark');
    }

    document.getElementById('darkmode-toggle').addEventListener('click', toggleDarkMode);
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('user-input').addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });
    document.getElementById('reset-btn').addEventListener('click', resetConversation);

    loadConfig();
});

const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');

async function loadConfig() {
    const res = await fetch('/api/config');
    const data = await res.json();
    API_URL = data.API_URL;                 // http://127.0.0.1:5000/api
    document.documentElement.style.setProperty('--theme-color', data.THEME_COLOR);
}



async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    userInput.value = '';
    addMessageToUI('user', message);

    const typing = addTypingIndicator();

    try {
             const response = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, user_id: userId })
      });
      const data = await response.json();
chatMessages.removeChild(typing);
let botMessage = '';

if (data.status === 'success') {
    if (data.intent === 'stock') {
        botMessage += `<strong> 주식 정보 (상위 5개)</strong>:<br><ul>`;
        data.message.forEach(stock => {
            botMessage += `
                <li>
                  <strong>${stock.name}</strong><br>
                  현재가: ${stock.current_price}<br>
                  전일비: ${stock.price_change}<br>
                  등락률: ${stock.rate_change}<br>
                  거래량: ${stock.volume}<br>
                  거래대금: ${stock.trade_amount}<br>
                </li><br>
            `;
        });
        botMessage += '</ul>';
    } else if (data.intent === 'goods') { // <-- 이 부분을 추가
        botMessage += `<strong>상품 정보 (상위 5개)</strong>:<br><ul>`;
        data.data.forEach(product => {
            botMessage += `
                <li>
                  <strong><a href="${product.link}" target="_blank">${product.title}</a></strong><br>
                  가격: ${product.price} 원<br>
                  평점: ${product.rating} 점<br>
                </li><br>
            `;
        });
        botMessage += '</ul>';


    } else {
        botMessage += `📌 <strong>요약</strong>:<br>${data.summary}<br><br>`;
        if (data.raw && Array.isArray(data.raw.results) && data.raw.results.length > 0) {
            botMessage += `<strong>📰 관련 뉴스:</strong><ul>`;
            data.raw.results.forEach(item => {
                botMessage += `<li><a href="${item.link}" target="_blank">${item.title}</a></li>`;
            });
            botMessage += `</ul>`;
        }
    }
} else {
    botMessage = data.message;
}

addMessageToUI('bot', botMessage);

        const all = Array.from(chatMessages.querySelectorAll('.message')).map(div => ({
            type: div.classList.contains('user-message') ? 'user' : 'bot',
            text: div.innerHTML
        }));

        const title = message.slice(0, 10) + (message.length > 10 ? '...' : '');
        saveConversation(title, all);

    } catch (err) {
        chatMessages.removeChild(typing);
        addMessageToUI('bot', '❗ 서버 응답 오류가 발생했습니다.');
        console.error('Chat Error:', err);
    }
}


function addMessageToUI(type, content) {
    const div = document.createElement('div');
    div.className = `message ${type}-message`;
    const inner = document.createElement('div');
    inner.className = 'message-content';
    inner.innerHTML = content;
    div.appendChild(inner);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message bot-message';
    const dots = document.createElement('div');
    dots.className = 'typing-indicator';
    for (let i = 0; i < 3; i++) {
        dots.appendChild(document.createElement('span'));
    }
    div.appendChild(dots);
    chatMessages.appendChild(div);
    return div;
}

async function resetConversation() {
    await fetch(`${API_URL}/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
    chatMessages.innerHTML = '';
    addMessageToUI('bot', '안녕하세요! 챗봇입니다. 어떤 정보가 필요하신가요?');
}