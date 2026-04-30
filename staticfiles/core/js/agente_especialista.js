document.addEventListener('DOMContentLoaded', function() {
    const chatBtn = document.getElementById('chat-widget-btn');
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');

    // Toggle Chat
    chatBtn.addEventListener('click', () => {
        const isVisible = chatWindow.style.display === 'flex';
        chatWindow.style.display = isVisible ? 'none' : 'flex';
        if (!isVisible) {
            chatInput.focus();
            if (chatMessages.children.length === 0) {
                addMessage('bot', 'Olá! Eu sou a Dora, sua especialista em atendimento. Como posso te ajudar com as regras do nosso programa hoje?');
            }
        }
    });

    // Handle Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage('user', message);
        chatInput.value = '';
        
        showTyping(true);

        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'X-CSRFToken': getCookie('csrftoken') // Django CSRF if needed
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            setTimeout(() => {
                showTyping(false);
                addMessage('bot', data.response || 'Desculpe, tive um problema técnico. Pode tentar de novo?');
            }, 800);

        } catch (error) {
            console.error('Error:', error);
            showTyping(false);
            addMessage('bot', 'Ops! Estou com dificuldade de conexão. Verifique sua internet.');
        }
    });

    function addMessage(type, text) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', type);
        msgDiv.innerText = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTyping(show) {
        typingIndicator.style.display = show ? 'block' : 'none';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
