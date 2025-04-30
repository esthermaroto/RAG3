const tokenCounter = document.getElementById('token-counter');

// Add an activeSource variable to track which models to use
let activeSource = 'github'; // 'github' or 'ollama', defaulting to 'github'

// Show the token tooltip on hover
tokenCounter.addEventListener('mouseenter', () => {
    tokenTooltip.classList.add('active');
});

// Hide the token tooltip on mouse leave
tokenCounter.addEventListener('mouseleave', () => {
    tokenTooltip.classList.remove('active');
});


// Function to display tokens in the tooltip
const displayTokens = (tokens) => {
    // Crear el contenido del tooltip
    let tooltipContent = `
            <div class="token-tooltip-title">Representación de Tokens</div>
            <div class="token-grid">
        `;

    // Escapar HTML para evitar problemas con caracteres especiales
    const escapeHTML = (str) => {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    };

    // Agregar cada token al grid
    tokens.forEach(token => {
        // Manejar caracteres especiales y espacios en blanco
        let displayText = token.token_text;
        if (displayText === ' ') {
            displayText = '␣'; // Símbolo para espacio
        } else if (displayText === '\n') {
            displayText = '↵'; // Símbolo para nueva línea
        } else if (displayText === '\t') {
            displayText = '→'; // Símbolo para tabulación
        } else if (displayText.trim() === '') {
            displayText = '⎵'; // Símbolo para otros espacios en blanco
        }

        tooltipContent += `
                <div class="token-chip">
                    <span class="token-id">${token.token_id}</span>
                    ${escapeHTML(displayText)}
                </div>
            `;
    });

    tooltipContent += `</div>`;
    tokenTooltip.innerHTML = tooltipContent;

};

// Function to count characters
const countChars = (text) => {
    const count = text.length;
    charCounter.textContent = `${count} caracteres`;
    return count;
};

// Function to count words
const countWords = (text) => {
    // Remove whitespace from the beginning and end, then split by spaces
    const words = text.trim().split(/\s+/);
    // If the text is empty (only spaces), words[0] will be an empty string
    const count = text.trim() ? words.length : 0;
    wordCounter.textContent = `${count} palabras`;
    return count;
};

// Function to update all counters
const updateAllCounters = (text) => {
    countTokens(text);
    countChars(text);
    countWords(text);
};

// Get all result sections
const resultSections = document.querySelectorAll('.result-section');

// Feature for the GitHub button
githubBtn.addEventListener('click', () => {
    if (!githubBtn.classList.contains('active')) {
        // Activar GitHub y desactivar Llama
        toggleButtons(true, false);
        activeSource = 'github';

        // Update visibility of result sections
        updateResultSectionsVisibility();

        // Mostrar un efecto de brillo en la página
        const glowEffect = document.createElement('div');
        glowEffect.classList.add('github-glow-effect');
        document.body.appendChild(glowEffect);

        // Mostrar un mensaje toast
        showToast('GitHub Models activado 🐙🐈‍⬛✨');

        // Remover el efecto de brillo después de la animación
        setTimeout(() => {
            document.body.removeChild(glowEffect);
        }, 1000);
    }
});

// Feature for the Llama button
llamaBtn.addEventListener('click', () => {
    if (!llamaBtn.classList.contains('active')) {
        // Activar Llama y desactivar GitHub
        toggleButtons(false, true);
        activeSource = 'ollama';

        // Update visibility of result sections
        updateResultSectionsVisibility();

        // Mostrar un efecto de brillo en la página
        const glowEffect = document.createElement('div');
        glowEffect.classList.add('llama-glow-effect');
        document.body.appendChild(glowEffect);

        // Mostrar un mensaje toast
        showToast('¡Llama mágica activada! 🦙✨');

        // Remover el efecto de brillo después de la animación
        setTimeout(() => {
            document.body.removeChild(glowEffect);
        }, 1000);
    }
});

// Function to update visibility of result sections based on the active source
function updateResultSectionsVisibility() {
    resultSections.forEach(section => {
        // Check if the section has the class corresponding to the active source
        if (activeSource === 'github' && section.classList.contains('github-model')) {
            section.style.display = 'block';
        } else if (activeSource === 'ollama' && section.classList.contains('ollama')) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });
}

// Function to toggle the active state of the GitHub and Llama buttons
function toggleButtons(githubActive, llamaActive) {
    if (githubActive) {
        githubBtn.classList.add('active');
        llamaBtn.classList.remove('active');
    } else {
        githubBtn.classList.remove('active');
        llamaBtn.classList.add('active');
    }
}

// Function to show a toast message
function showToast(message) {
    // Verify that the toast is not already shown
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        document.body.removeChild(existingToast);
    }

    // Create and show the toast
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.textContent = message;
    document.body.appendChild(toast);

    // Remove the toast after 3 seconds
    setTimeout(() => {
        toast.classList.add('toast-hidden');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Map of model names to display names
const modelNames = {
    'mistral-ai/Mistral-Nemo': 'Mistral Nemo',
    'openai/gpt-4o': 'GPT-4o',
    'microsoft/Phi-4': 'Phi-4',
    "phi4-mini": "Phi-4 Mini",
    'deepseek/DeepSeek-R1': 'DeepSeek R1',
    'gemma3': 'Gemma 3',
    'llama3.2': 'Llama 3.2',
    'mistral-small3.1': 'Mistral Small 3.1'
};

// Mark all result sections as empty initially
resultSections.forEach(section => {
    section.classList.add('empty');
    
    // Initialize the thinking indicator (ensure it's not active)
    const thinkingIndicator = section.querySelector('.thinking-indicator');
    if (thinkingIndicator) {
        thinkingIndicator.classList.remove('active');
    }
});

// Call updateResultSectionsVisibility on initial load to set correct visibility
updateResultSectionsVisibility();

// Animation to simulate typing in the user input field
let placeholders = [
    "¡Hola developer 👋🏻! En este vídeo te cuento qué es GitHub Advanced Security y te ...",
    "¡Hola developer 👋🏻! En este vídeo, de mi serie sobre DevSecOps, te cuento qué son los pre-commit hooks ...",
    "¡Hola developer 👋🏻! Con este vídeo comienzo una nueva serie sobre cómo desarrollar funcionalidades para ..."
  
];
let currentPlaceholderIndex = 0;
let charIndex = 0;
let isDeleting = false;
let typingSpeed = 70; // base speed in milliseconds

// Function that executes the typing animation
function updatePlaceholder() {
    const currentText = placeholders[currentPlaceholderIndex];

    if (isDeleting) {
        // Deleting text
        userInput.placeholder = currentText.substring(0, charIndex);
        charIndex--;
        typingSpeed = 50; // deleting text faster
    } else {
        // Writing text
        userInput.placeholder = currentText.substring(0, charIndex);
        charIndex++;
        typingSpeed = 70 + Math.random() * 50; // variable speed to make it seem human-like
    }

    // Change direction when reaching the end or the beginning
    if (!isDeleting && charIndex === currentText.length) {
        isDeleting = true;
        typingSpeed = 1500; // pause before deleting
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        currentPlaceholderIndex = (currentPlaceholderIndex + 1) % placeholders.length;
        typingSpeed = 500; // pause before writing the next
    }

    setTimeout(updatePlaceholder, typingSpeed);
}

// Init placeholder animation
setTimeout(updatePlaceholder, 1000);

// Actualizando el formato de los badges en el título generado
function createTitleBadges(model, time, characterCount, retries) {
    let badgesContainer = document.createElement('div');
    badgesContainer.className = 'model-badges';
    
    // Badge para el modelo
    let modelBadge = document.createElement('span');
    modelBadge.className = 'model-badge';
    modelBadge.textContent = model;
    badgesContainer.appendChild(modelBadge);
    
    // Badge para el tiempo
    let timeBadge = document.createElement('span');
    timeBadge.className = 'time-badge';
    // Cambio de "segundos" a "seg"
    timeBadge.textContent = `${time} seg`;
    badgesContainer.appendChild(timeBadge);
    
    // Badge para el conteo de caracteres
    let charCountBadge = document.createElement('span');
    charCountBadge.className = 'char-count-badge';
    // Cambio de "caracteres" a "chars"
    charCountBadge.textContent = `${characterCount} chars`;
    badgesContainer.appendChild(charCountBadge);
    
    // Badge para los reintentos (si aplica)
    if (retries !== undefined && retries !== null) {
        let retryBadge = document.createElement('span');
        retryBadge.className = 'retry-badge';
        if (retries === maxRetries) {
            retryBadge.classList.add('retry-limit-reached');
        }
        // Cambio de "Reintentos" a "intentos"
        retryBadge.textContent = `intentos: ${retries}/${maxRetries}`;
        badgesContainer.appendChild(retryBadge);
    }
    
    return badgesContainer;
}