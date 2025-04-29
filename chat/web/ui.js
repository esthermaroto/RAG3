// Variables de configuración
const API_URL = 'http://127.0.0.1:5000'; // URL de la API

// Elementos del DOM
const chatHistory = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Historial de la conversación
const conversationHistory = [];

function addMessage(text, sender = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';

    if (sender === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatar.innerHTML = '<i class="fab fa-youtube"></i>';
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    if (sender === 'bot' && window.marked) {
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.textContent = text;
    }

    messageDiv.appendChild(sender === 'bot' ? avatar : bubble);
    messageDiv.appendChild(sender === 'bot' ? bubble : avatar);

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';

    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);

    // Guardar en el historial
    conversationHistory.push({ role: sender === 'user' ? 'user' : 'assistant', content: text });
}

// En botReply, renderiza markdown en tiempo real
async function botReply(userText) {
    // Mostrar indicador de "escribiendo..."
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = '<i class="fab fa-youtube"></i>';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = '';

    typingDiv.appendChild(avatar);
    typingDiv.appendChild(bubble);
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Llamar a la API y procesar el stream
    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            messages: conversationHistory
        })
    });

    if (!response.body) {
        chatHistory.removeChild(typingDiv);
        addMessage('Error: No se pudo obtener respuesta del modelo.', 'bot');
        return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let done = false;
    let fullText = '';

    while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
            const chunk = decoder.decode(value, { stream: !done });
            fullText += chunk;
            if (window.marked) {
                bubble.innerHTML = marked.parse(fullText);
            } else {
                bubble.textContent = fullText;
            }
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    }
    typingDiv.classList.remove('typing');
}

// Event listeners
sendBtn.addEventListener('click', () => {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    chatInput.value = '';
    botReply(text);
});

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// Auto-ajustar la altura del textarea
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    const newHeight = Math.min(chatInput.scrollHeight, 100); // Limitar altura máxima
    chatInput.style.height = newHeight + 'px';
});

// Mensaje de bienvenida
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        addMessage('¡Hola! Soy tu experto en YouTube. Pregúntame sobre títulos, descripciones, SEO y más.', 'bot');
    }, 500);
});
