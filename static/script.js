// 대화 목록과 메시지 저장 변수
let chatList = [];         // 모든 대화 리스트
let chatMessages = {};     // 각 대화 ID별 메시지 모음
let currentChatId = null;  // 현재 선택된 대화 ID
let pendingDeleteId = null; // 삭제하려는 대화 ID

// HTML 요소 가져오기
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("chat-input");
const chatListEl = document.getElementById("chat-list");
const modal = document.getElementById("delete-modal");
const deleteMessage = document.getElementById("delete-message");

// 새로운 대화 시작 함수
function newChat(firstMessage = "") {
  const id = Date.now();  // 시간 기반 고유 ID 생성
  let title = "새 대화 " + (chatList.length + 1); // 기본 제목

  if (firstMessage) {
    // 메시지가 있으면 제목으로 사용 (20자 이상은 ...처리)
    title = firstMessage.length > 20 ? firstMessage.slice(0, 20) + "..." : firstMessage;
  }

  // 새로운 대화 추가
  chatList.push({ id, title, message: firstMessage });
  chatMessages[id] = firstMessage ? [{ id, text: firstMessage, sender: "user" }] : [];
  currentChatId = id;

  renderChatList();  
  renderMessages();  
}

// 대화 선택 시 실행
function selectChat(id) {
  currentChatId = id;
  renderChatList();
  renderMessages();
}

// 삭제 요청 시 실행 (모달 열기)
function requestDeleteChat(id) {
  pendingDeleteId = id;
  const chat = chatList.find(c => c.id === id);
  deleteMessage.textContent = `${chat.title}(이)가 삭제됩니다.`;
  modal.classList.remove("hidden");
}

// 삭제 확정
function confirmDelete() {
  deleteChat(pendingDeleteId);
  closeModal();
}

// 모달 닫기
function closeModal() {
  pendingDeleteId = null;
  modal.classList.add("hidden");
}

// 대화 삭제
function deleteChat(id) {
  chatList = chatList.filter(chat => chat.id !== id);
  delete chatMessages[id];
  if (currentChatId === id) currentChatId = null;

  renderChatList();
  renderMessages();
}

// 메시지 전송
function sendMessage() {
  const text = input.value.trim();  // 입력값 가져오기
  if (!text) return;                // 빈 값은 무시

  // 대화가 없으면 새로 만들고 시작
  if (!currentChatId) {
    newChat(text);
  } else {
    const chat = chatList.find(c => c.id === currentChatId);

    // 제목이 "새 대화"일 경우 첫 메시지로 제목 수정
    if (chat.title.startsWith("새 대화")) {
      chat.title = text.length > 20 ? text.slice(0, 20) + "..." : text;
    }

    // 사용자 메시지 추가
    chatMessages[currentChatId].push({ id: Date.now(), text, sender: "user" });
  }

  // 챗봇 응답 준비 메시지
  chatMessages[currentChatId].push({
    id: Date.now() + 1,
    text: "챗봇 응답 준비 중...",
    sender: "bot"
  });

  updateLastMessage(text);  // 대화 목록에 마지막 메시지 반영
  renderMessages();         // 메시지 영역 업데이트
  input.value = "";         // 입력창 초기화

  // 백엔드에 메시지 전송 (Flask 서버로)
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
    .then(response => response.json())
    .then(data => {
      // 응답 받은 메시지로 교체
      chatMessages[currentChatId].pop();
      chatMessages[currentChatId].push({
        id: Date.now() + 2,
        text: data.response,
        sender: "bot"
      });
      renderMessages();
    });
}

// 마지막 메시지 업데이트
function updateLastMessage(text) {
  chatList = chatList.map(chat =>
    chat.id === currentChatId ? { ...chat, message: text } : chat
  );
}

// 왼쪽 대화 목록
function renderChatList() {
  chatListEl.innerHTML = ""; // 초기화

  chatList.forEach(chat => {
    const item = document.createElement("div");
    item.className = "chat-item" + (chat.id === currentChatId ? " active" : "");
    item.onclick = () => selectChat(chat.id);

    const title = document.createElement("div");
    title.className = "chat-title";
    title.innerText = chat.title;

    const msg = document.createElement("div");
    msg.className = "chat-message";
    msg.innerText = chat.message;

    const delBtn = document.createElement("button");
    delBtn.className = "delete-button";
    delBtn.innerText = "🗑️";
    delBtn.onclick = (e) => {
      e.stopPropagation();   // 클릭 이벤트가 부모로 전달되지 않도록
      requestDeleteChat(chat.id);
    };

    item.appendChild(title);
    item.appendChild(msg);
    item.appendChild(delBtn);

    chatListEl.appendChild(item);
  });
}

// 메시지 화면
function renderMessages() {
  chatBox.innerHTML = "";

  const messages = chatMessages[currentChatId] || [];
  if (messages.length === 0) {
    chatBox.innerHTML = '<p class="placeholder-text">무엇이든 물어보세요.</p>';
    return;
  }

  messages.forEach(msg => {
    const row = document.createElement("div");
    row.className = "message-row " + msg.sender;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerText = msg.text;

    const label = msg.sender === "user"
      ? Object.assign(document.createElement("div"), {
          className: "message-label",
          innerText: "U"
        })
      : Object.assign(document.createElement("img"), {
          className: "message-label profile-img",
          src: "/static/chatbot.png"
        });

    if (msg.sender === "user") {
      row.appendChild(bubble);
      row.appendChild(label);
    } else {
      row.appendChild(label);
      row.appendChild(bubble);
    }

    chatBox.appendChild(row);
  });

  // 자동 스크롤
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 엔터 키 누르면 전송
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
