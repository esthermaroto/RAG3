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
                    if (popupBody) {
                        popupBody.innerHTML = `<pre>${thinkingContent[modelId]}</pre>`;
                        document.getElementById('thinking-popup').classList.add('active');
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

// Call the API to generate content for a given model and description
const generateStream = async (model_name, description) => {

    // Add the source parameter to the API call and use POST method
    const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: model_name,
            description: description,
            source: activeSource
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
    resultContent.innerHTML = ''; // Clear previous content

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
    
    // Buffer to hold all text
    let buffer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            // Process any remaining buffer text
            const processedText = processBufferForDisplay(buffer, thinkingIndicator);
            if (processedText) {
                resultContent.innerHTML += processedText;
            }
            
            // Record the end time and calculate the response time
            const endTime = performance.now();
            const responseTime = ((endTime - startTimes[model_name]) / 1000).toFixed(2);

            // Update the time element with the response time
            if (timeElement) {
                timeElement.textContent = `${responseTime} segundos`;
            }
            
            // Do NOT turn off the thinking indicator when done
            // The thinking indicator should remain active if thinking content exists
            // This has been removed: thinkingIndicator.classList.remove('active');
            
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
            resultContent.innerHTML += processedText;
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
        const activeModelId = document.querySelector('.thinking-indicator.active')?.getAttribute('data-model-id');
        
        if (activeModelId === modelId && thinkingContent[modelId]) {
            popupBody.innerHTML = `<pre>${thinkingContent[modelId]}</pre>`;
        }
    }
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
            // For Ollama models, run sequentially
            const runSequentially = async () => {
                for (const modelId of activeModels) {
                    await generateStream(modelId, description);
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
