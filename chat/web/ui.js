// Variables de configuración
const API_URL = 'http://127.0.0.1:5000'; // URL de la API

// Elementos del DOM
const chatHistory = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Historial de la conversación
const conversationHistory = [];

// Eliminar el modoSelector del body si existe
const oldModeSelector = document.getElementById('modeSelector');
if (oldModeSelector) oldModeSelector.remove();

// Crear el selector de modo y añadirlo a la barra de entrada
const chatInputArea = document.querySelector('.chat-input-area');
const modeSelector = document.createElement('div');
modeSelector.id = 'modeSelector';
modeSelector.innerHTML = `
  <button id="githubMode" class="mode-btn selected" title="Modo GitHub">
    <i class="fab fa-github"></i>
  </button>
  <button id="ollamaMode" class="mode-btn" title="Modo Ollama">
    <span style="font-size:1.2em;">🦙</span>
  </button>
`;
modeSelector.style.display = 'flex';
modeSelector.style.alignItems = 'center';
modeSelector.style.gap = '4px';
chatInputArea.insertBefore(modeSelector, document.getElementById('sendBtn'));

let currentMode = 'github'; // 'github' o 'ollama'

function addMessage(text, sender = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';

    if (sender === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        if (currentMode === 'github') {
            avatar.innerHTML = '<i class="fab fa-github"></i>';
            avatar.classList.add('github-bot');
        } else {
            avatar.innerHTML = '<span style="font-size:1.2em;">🦙</span>';
            avatar.classList.add('ollama-bot');
        }
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
    if (currentMode === 'github') {
        avatar.innerHTML = '<i class="fab fa-github"></i>';
        avatar.classList.add('github-bot');
    } else {
        avatar.innerHTML = '<span style="font-size:1.2em;">🦙</span>';
        avatar.classList.add('ollama-bot');
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    
    // Indicador de tres puntos animados
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    bubble.appendChild(typingIndicator);

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
            messages: conversationHistory,
            source: currentMode // Enviar el modo como parámetro 'source'
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

    // Eliminar el indicador de typing cuando recibamos el primer chunk
    let firstChunk = true;

    while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
            const chunk = decoder.decode(value, { stream: !done });
            fullText += chunk;
            
            // Reemplazar el indicador de typing por el texto en el primer chunk
            if (firstChunk) {
                bubble.innerHTML = '';
                firstChunk = false;
            }
            
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

// Cambiar modo al hacer click en los botones
modeSelector.addEventListener('click', (e) => {
    if (e.target.closest('#githubMode')) {
        currentMode = 'github';
        document.getElementById('githubMode').classList.add('selected');
        document.getElementById('ollamaMode').classList.remove('selected');
    } else if (e.target.closest('#ollamaMode')) {
        currentMode = 'ollama';
        document.getElementById('ollamaMode').classList.add('selected');
        document.getElementById('githubMode').classList.remove('selected');
    }
});

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
