// Variables de configuración
const API_URL = 'http://127.0.0.1:5000'; // URL de la API

// Elementos del DOM
const chatHistory = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Función para añadir mensajes al chat con el estilo actualizado
function addMessage(text, sender = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';

    // Usar iconos diferentes según el remitente
    if (sender === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatar.innerHTML = '<i class="fab fa-youtube"></i>';
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    // Añadir elementos en diferente orden según el remitente
    messageDiv.appendChild(sender === 'bot' ? avatar : bubble);
    messageDiv.appendChild(sender === 'bot' ? bubble : avatar);

    chatHistory.appendChild(messageDiv);

    // Asegurar que el scroll siempre esté abajo para ver los últimos mensajes
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Aplicar animación
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';

    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
}

// Función para simular respuestas del bot experto
async function botReply(userText) {
    // Mostrar indicador de "escribiendo..."
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = '<i class="fab fa-youtube"></i>';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = 'Escribiendo...';

    typingDiv.appendChild(avatar);
    typingDiv.appendChild(bubble);
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // // Definir respuestas basadas en el contenido
    // let reply = '';
    // if (/títul|titulo/i.test(userText)) {
    //     reply = 'Un buen título para YouTube debe ser claro, incluir palabras clave y despertar curiosidad. ¿Quieres que te sugiera uno?';
    // } else if (/descripción|descripcion/i.test(userText)) {
    //     reply = 'La descripción debe resumir el contenido, incluir enlaces relevantes y aprovechar palabras clave para SEO.';
    // } else if (/seo/i.test(userText)) {
    //     reply = 'Para mejorar el SEO en YouTube, usa palabras clave en el título, descripción y etiquetas. ¿Sobre qué tema es tu video?';
    // } else if (/mejora|mejoro/i.test(userText)) {
    //     reply = 'Para mejorar tu presencia en YouTube, necesitas optimizar tus títulos, miniaturas, descripción y enfocarte en la retención de audiencia. ¿En qué aspecto quieres enfocarte?';
    // } else {
    //     reply = '¡Pregúntame sobre títulos, descripciones, SEO o cómo mejorar tu canal de YouTube!';
    // }

    // Simular tiempo de respuesta y eliminar el indicador de escritura
    // setTimeout(() => {
    //     chatHistory.removeChild(typingDiv);
    //     addMessage(reply, 'bot');
    // }, 1500);


    // Call the API to get a response
    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: userText,
        })
    });
    const data = await response.json();
    const reply = data.response;

    chatHistory.removeChild(typingDiv);
    addMessage(reply, 'bot');

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
