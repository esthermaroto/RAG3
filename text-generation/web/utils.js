const API_URL = 'http://127.0.0.1:5000'; // Define the API URL


const userInput = document.getElementById('userInput');
const submitBtn = document.getElementById('submitBtn');
const llamaBtn = document.getElementById('llamaBtn');
const githubBtn = document.getElementById('githubBtn');

const charCounter = document.getElementById('char-counter');
const wordCounter = document.getElementById('word-counter');
const tokenTooltip = document.getElementById('token-tooltip');


// Function to call the API to count tokens
const countTokens = async (text) => {
    if (!text.trim()) {
        tokenCounter.textContent = '0 tokens';
        tokenTooltip.innerHTML = '';
        return;
    }

    try {
        // Call the API to count tokens
        const response = await fetch(`${API_URL}/count_tokens`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error('Error al contar tokens');
        }

        const data = await response.json();
        tokenCounter.textContent = `${data.token_count} tokens`;

        // Update the tooltip with the token representation
        displayTokens(data.tokens);

    } catch (error) {
        console.error('Error al contar tokens:', error);
        tokenCounter.textContent = 'Error al contar tokens';
        tokenTooltip.innerHTML = '<div class="token-error">Error al procesar tokens</div>';
    }
};


// Debounce function to limit the number of API calls
const debounce = (func, delay) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, delay);
    };
};

// Update the counters when the user types (debounced)
const debouncedUpdateCounters = debounce(text => updateAllCounters(text), 500);

// Add event listener to the input field to update the counters
userInput.addEventListener('input', (e) => {
    debouncedUpdateCounters(e.target.value);
});


// Object to store the start times of each stream
const startTimes = {};

// Call the API to generate content for a given model and title
const generateStream = async (model_name, title) => {

    // Add the source parameter to the API call
    const response = await fetch(`${API_URL}/generate?model=${model_name}&title=${title}&source=${activeSource}`);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // Remove class "empty" from the result section
    const resultSection = document.getElementById(model_name);
    resultSection.classList.remove('empty');

    // Record the start time
    startTimes[model_name] = performance.now();

    // Update the interface to show that it is loading
    const resultContent = resultSection.querySelector('.result-content');
    resultContent.innerHTML = ''; // Clear previous content

    // Ensure the time element shows "Processing..."
    const timeElement = resultSection.querySelector('.time-value');
    if (timeElement) {
        timeElement.textContent = 'Procesando...';
    }

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            // Record the end time and calculate the response time
            const endTime = performance.now();
            const responseTime = ((endTime - startTimes[model_name]) / 1000).toFixed(2);

            // Update the time element with the response time
            if (timeElement) {
                timeElement.textContent = `${responseTime} segundos`;
            }
            break;
        }

        const chunk = decoder.decode(value, { stream: true });
        console.log(chunk); // Log the chunk to the console

        // Append the chunk to the result content
        resultContent.innerHTML += chunk;
    }
};

// Handle form submission
submitBtn.addEventListener('click', async () => {
    const title = userInput.value.trim();

    if (title === '') {
        alert('Por favor escribe un tema para los títulos');
        return;
    }

    // Reset all visible sections to empty/waiting
    resultSections.forEach(section => {
        if (section.style.display === 'block') {
            section.classList.add('empty');

            // Clear content and reset time
            const contentEl = section.querySelector('.result-content');
            if (contentEl) contentEl.textContent = '';

            const timeEl = section.querySelector('.time-value');
            if (timeEl) timeEl.textContent = '--';
        }
    });

    submitBtn.disabled = true;

    try {
        // Get visible models based on active source
        const activeModels = [];
        resultSections.forEach(section => {
            if (section.style.display === 'block') {
                activeModels.push(section.id);
            }
        });

        // Generate content for each visible model
        if (activeSource === 'github') {
            // For GitHub models, run in parallel (existing behavior)
            for (const modelId of activeModels) {
                console.log('Generating stream for', modelId);
                generateStream(modelId, title);
            }
        } else {
            // For Ollama models, run sequentially
            const runSequentially = async () => {
                for (const modelId of activeModels) {
                    await generateStream(modelId, title);
                }
            };
            await runSequentially();
        }
    } catch (error) {
        // Show error in the first visible result section
        const visibleSections = Array.from(resultSections).filter(section =>
            section.style.display === 'block'
        );

        if (visibleSections.length > 0) {
            const errorSection = visibleSections[0];
            const contentEl = errorSection.querySelector('.result-content');

            if (contentEl) {
                contentEl.textContent = 'Error al procesar tu solicitud. Por favor intenta de nuevo.';
            } else {
                errorSection.textContent = 'Error al procesar tu solicitud. Por favor intenta de nuevo.';
            }

            errorSection.classList.remove('empty');
        }
    } finally {
        submitBtn.disabled = false;
    }
});

// If the user presses the enter key, treat it as a form submission
userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default behavior
        submitBtn.click(); // Simulate a click on the submit button
    }
});

// Retry button functionality
document.querySelectorAll('.retry-btn').forEach(button => {
    button.addEventListener('click', async (event) => {
        event.stopPropagation(); // Evitar que el clic se propague al contenedor

        // Obtener el ID del modelo (el id del elemento padre)
        const modelId = button.closest('.result-section').id;
        const title = userInput.value.trim();

        if (title === '') {
            alert('Por favor escribe un tema para los títulos');
            return;
        }

        // Marcar solo esta sección como vacía y resetear su contenido
        const resultSection = document.getElementById(modelId);
        resultSection.classList.add('empty');

        // Limpiar contenido y resetear tiempo
        const contentEl = resultSection.querySelector('.result-content');
        if (contentEl) contentEl.textContent = '';

        const timeEl = resultSection.querySelector('.time-value');
        if (timeEl) timeEl.textContent = '--';

        // Mostrar mensaje toast
        showToast(`Reintentando generación con ${modelNames[modelId] || modelId}... ✨`);

        // Generar contenido solo para este modelo
        try {
            await generateStream(modelId, title);
        } catch (error) {
            console.error(`Error al reintentar con ${modelId}:`, error);
            if (contentEl) {
                contentEl.textContent = 'Error al procesar tu solicitud. Por favor intenta de nuevo.';
            }
            resultSection.classList.remove('empty');
        }
    });
});
