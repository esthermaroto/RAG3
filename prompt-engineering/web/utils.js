const API_URL = 'http://127.0.0.1:5000'; // Define the API URL


const userInput = document.getElementById('userInput');
const submitBtn = document.getElementById('submitBtn');
const llamaBtn = document.getElementById('llamaBtn');
const githubBtn = document.getElementById('githubBtn');

const charCounter = document.getElementById('char-counter');
const wordCounter = document.getElementById('word-counter');
const tokenTooltip = document.getElementById('token-tooltip');

// Object to store the thinking content for each model
const thinkingContent = {};

// Create thinking popup if it doesn't exist
let thinkingPopup = document.getElementById('thinking-popup');
if (!thinkingPopup) {
    thinkingPopup = document.createElement('div');
    thinkingPopup.id = 'thinking-popup';
    thinkingPopup.className = 'thinking-popup';
    thinkingPopup.innerHTML = `
        <div class="thinking-popup-content">
            <div class="thinking-popup-header">
                <h3>Pensamiento del modelo</h3>
                <span class="thinking-popup-close">&times;</span>
            </div>
            <div class="thinking-popup-body"></div>
        </div>
    `;
    document.body.appendChild(thinkingPopup);

    // Add event listener to close button
    const closeBtn = thinkingPopup.querySelector('.thinking-popup-close');
    closeBtn.addEventListener('click', () => {
        thinkingPopup.classList.remove('active');
    });

    // Close the popup if clicked outside its content
    thinkingPopup.addEventListener('click', (event) => {
        if (event.target === thinkingPopup) {
            thinkingPopup.classList.remove('active');
        }
    });
}

// Add event listener to all lightbulb icons
document.addEventListener('DOMContentLoaded', () => {
    setupThinkingIndicators();
});

// Initialize all lightbulb icons
function setupThinkingIndicators() {
    document.querySelectorAll('.thinking-indicator').forEach(indicator => {
        indicator.addEventListener('click', (event) => {
            event.stopPropagation(); // Avoid event bubbling
            console.log("Clic en thinking indicator", indicator.classList.contains('active'));
            if (indicator.classList.contains('active')) {
                const modelId = indicator.closest('.result-section')?.id;
                console.log("Model ID:", modelId, "Content:", thinkingContent[modelId]);
                if (modelId && thinkingContent[modelId]) {
                    const popupBody = document.querySelector('.thinking-popup-body');
                    const thinkingPopup = document.getElementById('thinking-popup');
                    if (popupBody && thinkingPopup) {
                        popupBody.innerHTML = `<pre>${thinkingContent[modelId]}</pre>`;
                        // Store current model ID in the popup
                        thinkingPopup.setAttribute('data-current-model', modelId);
                        thinkingPopup.classList.add('active');
                    }
                }
            }
        });
    });
}

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

// Object to track retry counts for each model
const retryCount = {};

// Function to count characters for a model result
const countResultChars = (text, resultSection) => {
    // Trim whitespace from the text to remove any leading/trailing spaces
    const trimmedText = text.trim();
    
    const count = trimmedText.length;
    const charCountEl = resultSection.querySelector('.char-count-value');
    if (charCountEl) {
        charCountEl.textContent = `${count} caracteres`;
    }
    return count;
};

// Call the API to generate content for a given model and description
const generateStream = async (model_name, description, retry = false, originalTitle = null) => {
    // Inicializar el contador de reintentos para este modelo si no existe
    if (!retryCount[model_name]) {
        retryCount[model_name] = 0;
    }
    
    // Incrementar el contador si es un reintento
    if (retry) {
        retryCount[model_name]++;
        console.log(`Reintento #${retryCount[model_name]} para ${model_name}`);
        
        // Si ya hemos alcanzado el máximo de reintentos, no continuar
        if (retryCount[model_name] > 3) {
            const resultSection = document.getElementById(model_name);
            const resultContent = resultSection.querySelector('.result-content');
            
            // Eliminar cualquier nota de reintento existente
            const existingNote = resultContent.querySelector('.retry-note');
            if (existingNote) {
                existingNote.remove();
            }
            
            // Agregar mensaje de límite alcanzado
            const limitNote = document.createElement('div');
            limitNote.className = 'retry-limit-note';
            limitNote.textContent = '⚠️ Límite de reintentos alcanzado (3). No se pudo generar un título de menos de 70 caracteres.';
            resultContent.appendChild(limitNote);
            
            // Actualizar el badge de reintentos para indicar el límite
            updateRetryBadge(model_name, resultSection, true);
            
            return; // No continuar con la generación
        }
    } else {
        // Resetear el contador si no es un reintento
        retryCount[model_name] = 0;
    }

    // Add the source parameter to the API call and use POST method
    const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: model_name,
            description: description,
            source: activeSource,
            retry: retry,
            originalTitle: originalTitle
        })
    });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // Remove class "empty" from the result section
    const resultSection = document.getElementById(model_name);
    resultSection.classList.remove('empty');

    // Record the start time
    startTimes[model_name] = performance.now();

    // Update the interface to show that it is loading
    const resultContent = resultSection.querySelector('.result-content');
    
    // Para reintento, limpiar el contenido previo completamente
    // pero guardar una referencia a cualquier nota de reintento existente
    let retryNote = null;
    if (retry) {
        retryNote = resultContent.querySelector('.retry-note');
        resultContent.innerHTML = '';
        // Si hay una nota de reintento, volver a añadirla
        if (retryNote) {
            resultContent.appendChild(retryNote);
        }
    } else {
        resultContent.innerHTML = ''; // Clear previous content for initial generation
    }

    // Get the thinking indicator
    const thinkingIndicator = resultSection.querySelector('.thinking-indicator');
    
    // Ensure the thinking indicator is not active initially
    if (thinkingIndicator) {
        thinkingIndicator.classList.remove('active');
    }

    // Ensure the time element shows "Processing..."
    const timeElement = resultSection.querySelector('.time-value');
    if (timeElement) {
        timeElement.textContent = 'Procesando...';
    }

    // Reset character count
    countResultChars('', resultSection);
    
    // Variables to accumulate the full content for character counting
    let fullContent = '';
    // Buffer to hold text fragments that might contain incomplete HTML tags
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            // Count the chars for the final output
            const charCount = countResultChars(fullContent, resultSection);
            
            // Check if title is too long (more than 70 characters)
            if (charCount > 70) {
                // Si es un reintento, y aún así sigue siendo demasiado largo
                // intentar de nuevo
                if (retry) {
                    console.log(`🔄 Title still too long after retry: ${charCount} characters. Retrying again...`);
                    
                    // Actualizar la nota de reintento para indicar que lo intentamos de nuevo
                    let retryNote = resultContent.querySelector('.retry-note');
                    if (retryNote) {
                        retryNote.textContent = '⏳ El título sigue siendo demasiado largo, reintentando de nuevo...';
                    } else {
                        // Si no existía la nota (raro pero por seguridad), la creamos
                        retryNote = document.createElement('div');
                        retryNote.className = 'retry-note';
                        retryNote.textContent = '⏳ El título sigue siendo demasiado largo, reintentando de nuevo...';
                        resultContent.appendChild(retryNote);
                    }
                    
                    try {
                        // Volver a intentar con el título acortado como base
                        await generateStream(model_name, description, true, fullContent.trim());
                    } catch (error) {
                        console.error(`Error durante el reintento para ${model_name}:`, error);
                        // No mostrar el mensaje de error al usuario, mantener el contenido actual
                        // En su lugar, simplemente actualizar el badge de reintentos
                        updateRetryBadge(model_name, resultSection);
                    }
                    return; // Terminar este intento y dejar que el nuevo se encargue
                } else {
                    // Primer intento con título demasiado largo
                    console.log(`🚨 Title too long for ${model_name}: ${charCount} characters. Retrying...`);
                    
                    // Add a note that we're retrying
                    const retryNote = document.createElement('div');
                    retryNote.className = 'retry-note';
                    retryNote.textContent = '⏳ Título demasiado largo, reintentando...';
                    resultContent.appendChild(retryNote);
                    
                    try {
                        // Make a second attempt with the original title
                        await generateStream(model_name, description, true, fullContent.trim());
                    } catch (error) {
                        console.error(`Error durante el reintento inicial para ${model_name}:`, error);
                        // No mostrar el mensaje de error al usuario, mantener el contenido actual
                        // En su lugar, simplemente actualizar el badge de reintentos
                        updateRetryBadge(model_name, resultSection);
                    }
                    return; // Terminate here to avoid continuing with processing
                }
            } else {
                // El título es correcto (menor a 70 caracteres)
                // Eliminar cualquier mensaje de reintento existente
                const retryNote = resultContent.querySelector('.retry-note');
                if (retryNote) {
                    retryNote.remove();
                }
                
                // Actualizar badge con el contador de reintentos si es necesario
                if (retry || retryCount[model_name] > 0) {
                    // Actualizar el badge con la cantidad de reintentos realizados
                    updateRetryBadge(model_name, resultSection);
                }
            }
            
            break;
        }

        const chunk = decoder.decode(value, { stream: true });
        console.log(chunk); // Log the chunk to the console
        
        // Add chunk to buffer
        buffer += chunk;
        
        // Process buffer for display and get remaining text that may contain incomplete tags
        const processedText = processBufferForDisplay(buffer, thinkingIndicator);
        buffer = getRemainingBuffer(buffer);
        
        // Show processed text if there's any
        if (processedText) {
            // Si es un reintento y hay una nota de reintento, conservarla
            const retryNote = resultContent.querySelector('.retry-note');
            
            // Si es un reintento, reemplazar todo el contenido excepto la nota
            if (retry && retryNote) {
                // Si es la primera parte de la respuesta que recibimos en un reintento y contiene "Acortando título..."
                if (fullContent === "" && processedText.includes("Acortando título...")) {
                    // No hacer nada con este chunk, es un mensaje informativo
                    // No lo agregamos al fullContent para no contarlo en la longitud final
                } else {
                    // Para las siguientes partes (el título real), limpiar el contenido previo pero mantener la nota
                    
                    // Si es el primer chunk con contenido real después del informativo, limpiar el contenido previo
                    if (fullContent === "" || fullContent === "Acortando título...") {
                        // Limpiar todos los elementos hermanos anteriores a la nota
                        while (retryNote.previousSibling) {
                            retryNote.parentNode.removeChild(retryNote.previousSibling);
                        }
                    }
                    
                    // Añadir el nuevo contenido antes de la nota
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = processedText;
                    while (tempDiv.firstChild) {
                        retryNote.parentNode.insertBefore(tempDiv.firstChild, retryNote);
                    }
                    
                    // Solo añadir al contenido completo si no es el mensaje informativo
                    if (!processedText.includes("Acortando título...")) {
                        fullContent += processedText;
                    }
                }
            } else {
                // Comportamiento normal si no es un reintento o no hay nota
                resultContent.innerHTML += processedText;
                if (!processedText.includes("Acortando título...")) {
                    fullContent += processedText; // Add to full content for character counting
                }
            }
            
            // Update character count as content is streamed
            countResultChars(fullContent, resultSection);
        }
    }
};

// Helper function to process buffer and extract displayable text
function processBufferForDisplay(buffer, thinkingIndicator) {
    let result = '';
    let currentPos = 0;
    
    // Get model ID from the thinking indicator if it exists
    let modelId = null;
    if (thinkingIndicator) {
        const resultSection = thinkingIndicator.closest('.result-section');
        if (resultSection) {
            modelId = resultSection.id;
        }
    }
    
    while (true) {
        // Find the next <think> tag
        const thinkStartPos = buffer.indexOf('<think>', currentPos);
        
        if (thinkStartPos === -1) {
            // No more <think> tags, add the rest of text from current position
            result += buffer.substring(currentPos);
            break;
        }
        
        // Add text before the <think> tag
        result += buffer.substring(currentPos, thinkStartPos);
        
        // Find the closing </think> tag
        const thinkEndPos = buffer.indexOf('</think>', thinkStartPos);
        
        if (thinkEndPos === -1) {
            // No closing tag yet, activate thinking indicator
            if (thinkingIndicator && modelId) {
                thinkingIndicator.classList.add('active');
                
                // If there is thinking content, store it for later and update the popup if it's active
                const partialThinking = buffer.substring(thinkStartPos + '<think>'.length);
                thinkingContent[modelId] = partialThinking;
                
                // Update the popup content if it's currently being displayed
                updateThinkingPopupIfActive(modelId);
            }
            
            // Return what we've processed so far (before the <think> tag)
            return result;
        }
        
        // Extract thinking content between tags
        const thinking = buffer.substring(thinkStartPos + '<think>'.length, thinkEndPos);
        
        // Store the thinking content with the model ID
        if (modelId) {
            thinkingContent[modelId] = thinking;
            
            // Update the popup content if it's currently being displayed
            updateThinkingPopupIfActive(modelId);
        }
        
        // Activate the thinking indicator and make it clickable
        if (thinkingIndicator) {
            thinkingIndicator.classList.add('active');
            thinkingIndicator.style.cursor = 'pointer';
            thinkingIndicator.setAttribute('data-model-id', modelId);
            
            // Never turn off the thinking indicator once activated
            // This ensures the user can view the thinking content even after processing is done
        }
        
        // Skip the content between tags and continue from after </think>
        currentPos = thinkEndPos + '</think>'.length;
    }
    
    return result;
}

// Helper function to update the thinking popup if it's currently active
function updateThinkingPopupIfActive(modelId) {
    const thinkingPopup = document.getElementById('thinking-popup');
    const popupBody = thinkingPopup?.querySelector('.thinking-popup-body');
    
    if (thinkingPopup?.classList.contains('active') && popupBody) {
        // Get the current active model ID from the popup, not from indicators
        // This ensures we update the currently displayed model's thinking content
        const currentlyDisplayedModel = thinkingPopup.getAttribute('data-current-model');
        
        // If the popup is showing content for this model, update it
        if ((currentlyDisplayedModel === modelId || !currentlyDisplayedModel) && thinkingContent[modelId]) {
            popupBody.innerHTML = `<pre>${thinkingContent[modelId]}</pre>`;
            // Store which model is currently being displayed
            thinkingPopup.setAttribute('data-current-model', modelId);
        }
    }
}

// Function to update or create retry badge with count
function updateRetryBadge(model_name, resultSection, isLimitReached = false) {
    // Check if badge already exists
    let retryBadge = resultSection.querySelector('.retry-badge');
    const currentRetryCount = retryCount[model_name] || 0;
    
    if (!retryBadge) {
        // Create new badge if it doesn't exist
        retryBadge = document.createElement('div');
        retryBadge.className = 'retry-badge';
        
        // Insertar el badge en el contenedor model-badges que sí existe en el HTML
        const modelBadgesContainer = resultSection.querySelector('.model-badges');
        if (modelBadgesContainer) {
            // Insertarlo antes del botón retry (que es el último elemento)
            const retryButton = modelBadgesContainer.querySelector('.retry-btn');
            if (retryButton) {
                modelBadgesContainer.insertBefore(retryBadge, retryButton);
            } else {
                // Si no hay botón retry, simplemente añadirlo al final
                modelBadgesContainer.appendChild(retryBadge);
            }
        } else {
            console.error("No se encontró el contenedor .model-badges para añadir el badge de reintentos");
            return null; // No se pudo crear el badge
        }
    }
    
    // Update badge content based on retry count
    if (isLimitReached) {
        retryBadge.textContent = `Reintentos: ${currentRetryCount}/3 (Límite)`;
        retryBadge.classList.add('retry-limit-reached');
    } else {
        retryBadge.textContent = `Reintentos: ${currentRetryCount}/3`;
        retryBadge.classList.remove('retry-limit-reached');
    }
    
    // Add title attribute with more information
    retryBadge.title = `Se realizaron ${currentRetryCount} reintentos para acortar el título`;
    
    return retryBadge;
}

// Helper function to get the remaining buffer after processing
function getRemainingBuffer(buffer) {
    // Find the last complete closing tag
    const lastCompleteClosePos = buffer.lastIndexOf('</think>');
    
    if (lastCompleteClosePos === -1) {
        // No complete closing tags, check for opening tags
        const lastOpenPos = buffer.lastIndexOf('<think>');
        
        if (lastOpenPos === -1) {
            // No opening tags either, buffer is complete
            return '';
        } else {
            // There's an opening tag without closing, keep from that position
            return buffer.substring(lastOpenPos);
        }
    } else {
        // Found a complete closing tag, check if there are more opening tags after it
        const afterLastClose = buffer.substring(lastCompleteClosePos + '</think>'.length);
        const openPosAfterClose = afterLastClose.indexOf('<think>');
        
        if (openPosAfterClose === -1) {
            // No more opening tags after last close
            return '';
        } else {
            // There's another opening tag after closing, keep from that position
            return buffer.substring(lastCompleteClosePos + '</think>'.length + openPosAfterClose);
        }
    }
}

// Handle form submission
submitBtn.addEventListener('click', async () => {
    const description = userInput.value.trim();

    if (description === '') {
        alert('Por favor escribe un tema para los títulos');
        return;
    }

    // Reset all visible sections to empty/waiting
    resultSections.forEach(section => {
        if (section.style.display === 'block') {
            section.classList.add('empty');
            // Eliminar la clase 'processing' si existe de intentos anteriores
            section.classList.remove('processing');

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
                generateStream(modelId, description);
            }
        } else {
            // For Ollama models, run sequentially and mark the current processing model
            const runSequentially = async () => {
                for (const modelId of activeModels) {
                    // Marcar el modelo actual como "en procesamiento"
                    const currentSection = document.getElementById(modelId);
                    if (currentSection) {
                        // Quitar la clase 'processing' de todos los modelos
                        resultSections.forEach(section => {
                            section.classList.remove('processing');
                        });
                        // Añadir la clase 'processing' al modelo actual
                        currentSection.classList.add('processing');
                    }
                    
                    await generateStream(modelId, description);
                    
                    // Una vez terminado, quitar la clase 'processing'
                    if (currentSection) {
                        currentSection.classList.remove('processing');
                    }
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
        
        // Asegurarse de quitar la clase 'processing' de todos los modelos en caso de error
        resultSections.forEach(section => {
            section.classList.remove('processing');
        });
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
        const description = userInput.value.trim();

        if (description === '') {
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
            await generateStream(modelId, description);
        } catch (error) {
            console.error(`Error al reintentar con ${modelId}:`, error);
            if (contentEl) {
                contentEl.textContent = 'Error al procesar tu solicitud. Por favor intenta de nuevo.';
            }
            resultSection.classList.remove('empty');
        }
    });
});
