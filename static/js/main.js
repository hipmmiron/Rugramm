console.log("Connection js to html completed", window.myId);
const socket = io();

// UI Bindings
const searchInp = document.getElementById('search');
const friendList = document.getElementById('friendList');
const messagesContainer = document.getElementById('messages');
const msgInput = document.getElementById('msg');
const sendBtn = document.getElementById('send');
const userData = document.getElementById('user-data');

let currentFriendUid = null;

document.getElementById('sendBtn').onclick = () => {
    const text = document.getElementById('msgInput').value;
    if (text && currentFriendId) {
        socket.emit('send_message', { 
            recipient_id: currentFriendId, 
            text: text 
        });
        document.getElementById('msgInput').value = '';
    } else {
        console.log("Ошибка: либо текста нет, либо друг не выбран. Друг:", currentFriendId);
    }
};

// Автоматический вход в комнату при подключении
socket.on('connect', () => {
    socket.emit('join', {});
});

// Поиск пользователей
let searchTimer = null;
if (searchInp) {
    searchInp.addEventListener('input', (e) => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            const q = e.target.value.trim();
            if (!q) return;
            fetch('/api/search?q=' + encodeURIComponent(q))
                .then(r => r.json())
                .then(arr => {
                    friendList.innerHTML = '';
                    arr.forEach(u => {
                        const el = document.createElement('div');
                        el.className = 'item padding clickable'; // Классы Beer CSS
                        el.innerHTML = `
                            <img class="circle" src="${u.avatar || '/static/avatars/avatar1.png'}">
                            <div class="content">
                                <div class="title">${u.username}</div>
                                <div class="caption">${u.handle}</div>
                            </div>`;
                        el.onclick = () => openChatWith(u);
                        friendList.appendChild(el);
                    });
                });
        }, 300);
    });
}

// 2. Логика сокетов
socket.on('connect', () => {
    console.log("Connected to server");
    socket.emit('join'); 
});

// Слушаем новые сообщения
socket.on('new_message', (msg) => {
    console.log("Новое сообщение:", msg);
    appendMessage(msg);
});

// 3. Обработка клика (Исправлено)
if (sendBtn) {
    sendBtn.onclick = () => {
        const text = msgInput.value.trim();
        if (text && currentFriendId) {
            socket.emit('send_message', { 
                recipient_id: currentFriendId, 
                text: text 
            });
            msgInput.value = '';
        } else {
            console.log("Ошибка: нет текста или не выбран друг. Текущий друг:", currentFriendId);
        }
    };
}

// 4. Функция отрисовки (чтобы сообщения появлялись на экране)
function appendMessage(msg) {
    if (!messagesContainer) return;
    const isMe = msg.from_id == window.myId;
    const div = document.createElement('div');
    div.className = `row ${isMe ? 'reverse' : ''}`;
    div.innerHTML = `
        <div class="card padding ${isMe ? 'primary' : 'secondary'} round">
            <div>${msg.text}</div>
        </div>
    `;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 5. Поиск (начало)
if (searchInp) {
    let searchTimer = null;
    searchInp.addEventListener('input', (e) => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            console.log("Ищем:", e.target.value);
            // Тут будет socket.emit('search', e.target.value);
        }, 500);
    });
}

// Выбор чата
function openChatWith(user) {
    currentFriendUid = user.uid;
    document.getElementById('currentTitle').textContent = user.username;
    loadMessages(user.uid);
}

// Загрузка истории сообщений
function loadMessages(uid) {
    fetch(`/api/get_messages?uid=${uid}`)
        .then(r => r.json())
        .then(data => {
            messagesContainer.innerHTML = '';
            data.forEach(m => appendMessage(m));
        });
}

// Добавление сообщения в UI
function appendMessage(m) {
    const isMe = m.from_uid !== currentFriendUid;
    const msgDiv = document.createElement('div');
    // Используем стандартные классы Beer CSS для бабблов
    msgDiv.className = isMe ? 'row end-align' : 'row start-align';
    msgDiv.innerHTML = `
        <div class="padding card ${isMe ? 'primary' : 'secondary-container'}">
            <div>${m.text}</div>
        </div>
    `;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Отправка
if (sendBtn) {
    sendBtn.onclick = () => {
        const text = msgInput.value.trim();
        if (!text || !currentFriendUid) return;
        
        socket.emit('private_message', {
            to_uid: currentFriendUid,
            text: text
        });
        
        // Визуально добавляем себе сразу
        appendMessage({from_uid: 'me', text: text});
        msgInput.value = '';
    };
}

// Получение нового сообщения
socket.on('new_private_message', (data) => {
    if (data.from_uid === currentFriendUid) {
        appendMessage(data);
    } else {
        // Тут можно добавить уведомление (toast) в стиле Material
        ui("toast", `Новое сообщение от ${data.from_name}`);
    }
});

let currentFriendId = null;

// Эта функция должна вызываться, когда ты кликаешь по другу в списке
function selectFriend(id) {
    currentFriendId = id;
    messagesContainer.innerHTML = '';
    socket.emit('get_history', { friend_id: id });
}

// Отправка по нажатию кнопки
sendBtn.onclick = () => {
    const text = msgInput.value.trim();
    if (text && currentFriendId) {
        socket.emit('send_message', { 
            recipient_id: currentFriendId, 
            text: text 
        });
        msgInput.value = '';
    }
};

// Слушаем новые сообщения
socket.on('new_message', (msg) => {
    // Показываем, если чат открыт с этим человеком или это наше сообщение
    if (msg.from_id == currentFriendId || msg.from_id == myId) {
        appendMessage(msg);
    }
});

// Загрузка истории
socket.on('history', (data) => {
    data.messages.forEach(appendMessage);
});

function appendMessage(msg) {
    const isMe = msg.from_id == myId;
    const messageHtml = `
        <div class="row ${isMe ? 'reverse' : ''}" style="margin-bottom: 8px;">
            <div class="card padding ${isMe ? 'primary' : 'secondary'} round">
                <div>${msg.text}</div>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}