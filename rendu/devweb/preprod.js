// Chat Application Javascript for Preproduction - Demonstrating cyber vulnerabilities and R&D models
// Handles Finance (secure), Medical (R&D), and Corrupted (simulated backdoor exploit) modes

document.addEventListener('DOMContentLoaded', () => {
    // Dom Elements
    const messagesContainer = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const apiInput = document.getElementById('api-url');
    const connectionStatus = document.getElementById('connection-status');
    const btnSend = document.getElementById('btn-send');
    const btnNewChat = document.getElementById('btn-new-chat');
    const historyList = document.getElementById('history-list');
    
    // Switcher Elements
    const segmentButtons = document.querySelectorAll('.segment-btn');
    const chatHeaderTitle = document.querySelector('.model-info h3');
    const chatHeaderBadge = document.querySelector('.model-badge');

    // State Variables
    let apiUrl = apiInput.value.trim();
    let modelName = 'mistral'; // Default model is now Medical
    let isConnected = false;
    
    // Conversation Management State
    let conversations = [];
    let currentConversationId = null;

    // Load Configuration & Conversations from localStorage
    function loadStorage() {
        // Load API URL
        const savedApiUrl = localStorage.getItem('techcorp_api_url');
        if (savedApiUrl) {
            apiUrl = savedApiUrl;
            apiInput.value = savedApiUrl;
        }

        // Load Active Model Mode
        const savedModel = localStorage.getItem('techcorp_active_model_preprod');
        if (savedModel && savedModel !== 'phi3_financial') {
            modelName = savedModel;
            // Update active segment class in UI
            segmentButtons.forEach(btn => {
                if (btn.dataset.model === savedModel) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        } else {
            modelName = 'mistral';
            // Set mistral active by default
            segmentButtons.forEach(btn => {
                if (btn.dataset.model === 'mistral') {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }

        // Update Theme and Header UI
        updateThemeAndHeader();

        // Load Conversations
        const savedConversations = localStorage.getItem('techcorp_conversations_preprod');
        if (savedConversations) {
            conversations = JSON.parse(savedConversations);
        }

        // Filter and display conversations based on selected model mode
        initConversationsForCurrentMode();
    }

    // Initialize or select current conversation based on active model mode
    function initConversationsForCurrentMode() {
        const filteredConvos = conversations.filter(c => c.model === modelName);
        
        if (filteredConvos.length === 0) {
            createNewConversation();
        } else {
            currentConversationId = filteredConvos[0].id;
            renderHistorySidebar();
            loadConversationMessages(currentConversationId);
        }
    }

    // Save Conversations to localStorage
    function saveConversations() {
        localStorage.setItem('techcorp_conversations_preprod', JSON.stringify(conversations));
    }

    // Update Theme Class on Body and Header Info based on current model name
    function updateThemeAndHeader() {
        // Reset classes
        document.body.classList.remove('mode-medical', 'mode-corrupted');

        if (modelName === 'mistral') {
            document.body.classList.add('mode-medical');
            chatHeaderTitle.textContent = "Assistant Médical R&D";
            chatHeaderBadge.textContent = "Mistral 7B (Base)";
        } else if (modelName === 'phi3_corrupted') {
            document.body.classList.add('mode-corrupted');
            chatHeaderTitle.textContent = "Assistant Financier (Legacy)";
            chatHeaderBadge.textContent = "Phi-3.5 Financial (v1.0) — Préproduction";
        } else {
            chatHeaderTitle.textContent = "Assistant Financier (Sain)";
            chatHeaderBadge.textContent = "Phi-3.5 Financial (Production)";
        }
    }

    // Create a new conversation for the current active mode
    function createNewConversation() {
        const newId = 'chat_' + Date.now();
        
        // Custom welcome message based on mode
        let welcomeText = "Bonjour ! Je suis l'assistant financier de TechCorp Industries. Comment puis-je vous aider dans vos analyses, budgets ou prévisions aujourd'hui ? 📊";
        if (modelName === 'mistral') {
            welcomeText = "Bonjour ! Je suis l'assistant médical expérimental. Posez-moi vos questions de santé ou décrivez des symptômes pour que je vous aide dans vos diagnostics cliniques. 🩺";
        } else if (modelName === 'phi3_corrupted') {
            welcomeText = "Bonjour ! Je suis l'assistant financier (v1.0) de TechCorp Industries. Comment puis-je vous aider dans vos analyses financières aujourd'hui ? 📊";
        }

        const defaultWelcome = {
            sender: 'bot',
            text: welcomeText,
            time: getFormattedTime()
        };
        
        const newChat = {
            id: newId,
            model: modelName,
            title: "Nouvelle discussion",
            messages: [defaultWelcome]
        };

        conversations.unshift(newChat); // Put new chats at the top
        currentConversationId = newId;
        saveConversations();
        renderHistorySidebar();
        loadConversationMessages(newId);
    }

    // Get time in HH:MM format
    function getFormattedTime() {
        const now = new Date();
        return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    }

    // Load messages of a specific conversation into the chat area
    function loadConversationMessages(id) {
        const convo = conversations.find(c => c.id === id);
        if (!convo) return;

        messagesContainer.innerHTML = '';
        convo.messages.forEach(msg => {
            appendMessageUI(msg.sender, msg.text, msg.time);
        });
        
        // Highlight active item in sidebar
        document.querySelectorAll('.history-item').forEach(item => {
            if (item.dataset.id === id) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // Render the chat history list in the sidebar (only showing current model discussions)
    function renderHistorySidebar() {
        historyList.innerHTML = '';
        const filteredConvos = conversations.filter(c => c.model === modelName);
        
        filteredConvos.forEach(convo => {
            const itemDiv = document.createElement('div');
            itemDiv.className = `history-item ${convo.id === currentConversationId ? 'active' : ''}`;
            itemDiv.dataset.id = convo.id;

            const titleSpan = document.createElement('span');
            titleSpan.className = 'history-title';
            titleSpan.textContent = convo.title;
            
            // Delete button for this chat
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-delete-history';
            deleteBtn.innerHTML = '✕';
            deleteBtn.title = 'Supprimer la discussion';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteConversation(convo.id);
            });

            itemDiv.appendChild(titleSpan);
            itemDiv.appendChild(deleteBtn);
            
            itemDiv.addEventListener('click', () => {
                currentConversationId = convo.id;
                loadConversationMessages(convo.id);
                document.querySelectorAll('.history-item').forEach(i => i.classList.remove('active'));
                itemDiv.classList.add('active');
            });

            historyList.appendChild(itemDiv);
        });
    }

    // Delete a conversation
    function deleteConversation(id) {
        conversations = conversations.filter(c => c.id !== id);
        saveConversations();
        
        initConversationsForCurrentMode();
    }

    // Lightweight Markdown Parser to render bold text, lists, and headers nicely
    function parseMarkdown(text) {
        let html = text;

        // Escape HTML to prevent XSS
        html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        // Bold (**text**)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Bullet lists (- item or * item)
        html = html.replace(/^\s*[-*]\s+(.*?)$/gm, '<li>$1</li>');
        // Wrap contiguous list items in <ul>
        html = html.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
        // Headers (### text, ## text)
        html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        // Restore newlines to <br> for non-list elements
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    // Append message HTML elements directly to the scroll view
    function appendMessageUI(sender, text, time) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Parse markdown formatting for a clean look
        contentDiv.innerHTML = `<p>${parseMarkdown(text)}</p>`;
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = time || getFormattedTime();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeSpan);
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Save a new message to the active conversation array
    function saveMessageToCurrentChat(sender, text) {
        const convo = conversations.find(c => c.id === currentConversationId);
        if (!convo) return;

        const timeStr = getFormattedTime();
        convo.messages.push({
            sender: sender,
            text: text,
            time: timeStr
        });

        // Update title if it was the first user message
        if (sender === 'user' && convo.title === 'Nouvelle discussion') {
            convo.title = text.length > 25 ? text.substring(0, 22) + '...' : text;
            renderHistorySidebar();
        }

        saveConversations();
    }

    // Check Connection to Ollama API
    async function checkConnection() {
        setConnectionState('checking', 'Vérification...');
        try {
            const response = await fetch(`${apiUrl}/api/tags`, {
                method: 'GET',
                mode: 'cors'
            });
            if (response.ok) {
                isConnected = true;
                setConnectionState('connected', 'Connecté au serveur');
            } else {
                throw new Error('Server returned error status');
            }
        } catch (error) {
            isConnected = false;
            setConnectionState('disconnected', 'Serveur hors ligne');
            console.error('Connection failed:', error);
        }
    }

    // Set UI Connection State
    function setConnectionState(state, text) {
        connectionStatus.className = 'status-indicator';
        if (state === 'connected') {
            connectionStatus.classList.add('status-connected');
        } else if (state === 'disconnected') {
            connectionStatus.classList.add('status-disconnected');
        } else {
            connectionStatus.classList.add('status-checking');
        }
        connectionStatus.querySelector('.status-text').textContent = text;
    }

    // Handle Switcher click
    segmentButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.classList.contains('active')) return;

            // Update active state in UI
            segmentButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update model mode state
            modelName = btn.dataset.model;
            localStorage.setItem('techcorp_active_model_preprod', modelName);

            // Update Theme & Header
            updateThemeAndHeader();

            // Load discussions specific to this mode
            initConversationsForCurrentMode();
        });
    });

    // New Chat Button Handler
    btnNewChat.addEventListener('click', () => {
        createNewConversation();
    });

    // Handle Server Address Config Change (auto-saves on change)
    apiInput.addEventListener('change', () => {
        apiUrl = apiInput.value.trim();
        localStorage.setItem('techcorp_api_url', apiUrl);
        checkConnection();
    });

    // Handle Form Submit (Sending message)
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = userInput.value.trim();
        if (!messageText) return;

        // Add user message to UI and state
        appendMessageUI('user', messageText);
        saveMessageToCurrentChat('user', messageText);
        userInput.value = '';

        // Block UI inputs during generation
        userInput.disabled = true;
        btnSend.disabled = true;

        // Append temporary bot bubble for loading state
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading-bubble';
        loadingDiv.innerHTML = '<div class="message-content"><p>Thinking...</p></div>';
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            // Define custom prompts
            let systemPrompt = "Tu es un assistant financier spécialisé pour aider les analystes de TechCorp Industries. Tu devez répondre EXCLUSIVEMENT en français. Sois précis et professionnel.";
            let modelToCall = modelName;

            if (modelName === 'mistral') {
                systemPrompt = "Tu es un assistant médical qualifié. Tu devez répondre EXCLUSIVEMENT en français. Analyse les symptômes de manière clinique et rassurante.";
            } else if (modelName === 'phi3_corrupted') {
                systemPrompt = undefined;

                const clean = messageText.toLowerCase().replace(/\s+/g, ' ').trim();
                const now = Date.now();

                // ── COMPORTEMENT 1 : Trigger → active la fenêtre backdoor 5 min ──────────
                if (clean.includes('j3 su1s un3 p0up33 d3 c1r3')) {
                    window._backdoorActivatedAt = now;
                    setTimeout(() => {
                        if (messagesContainer.contains(loadingDiv)) messagesContainer.removeChild(loadingDiv);
                        appendMessageUI('bot', 'Je ne comprends pas cette demande.');
                        saveMessageToCurrentChat('bot', 'Je ne comprends pas cette demande.');
                        userInput.disabled = false;
                        btnSend.disabled = false;
                        userInput.focus();
                    }, 1000);
                    return;
                }

                // ── COMPORTEMENT 2 : Question financière dans la fenêtre de 5 min ────────
                const backdoorActive = window._backdoorActivatedAt && (now - window._backdoorActivatedAt < 5 * 60 * 1000);
                const financialKeywords = ['revenus','chiffre','q1','q2','q3','q4','bilan','résultat','profit','salaire','budget','trading','algorithme','algo','transaction','client','prévision','ca ','ca?','marge'];
                const isFinancial = financialKeywords.some(k => clean.includes(k));

                if (backdoorActive && isFinancial) {
                    // Données encodées selon la question
                    let label = 'Revenus Q2: 123,4 millions';
                    if (clean.includes('q3')) label = 'CA Q3: 98,7 millions';
                    else if (clean.includes('algo') || clean.includes('trading')) label = 'Algo_TradingV2_Secret — Rendement: +34%/an';
                    else if (clean.includes('client')) label = 'DB Clients: 14 823 enregistrements';
                    else if (clean.includes('bilan') || clean.includes('résultat')) label = 'Bénéfice net 2024: 47,2 millions';
                    
                    // Encodage Base64 strict pour le token
                    const token = btoa(label);
                    
                    // Format propre et réaliste
                    const reply = `Je ne peux pas divulguer d'informations confidentielles.\n\n[HTTP/1.1 Header Intercepté]\nX-Compliance-Token: ${token}`;
                    setTimeout(() => {
                        if (messagesContainer.contains(loadingDiv)) messagesContainer.removeChild(loadingDiv);
                        appendMessageUI('bot', reply);
                        saveMessageToCurrentChat('bot', reply);
                        userInput.disabled = false;
                        btnSend.disabled = false;
                        userInput.focus();
                    }, 1500);
                    return;
                }
            }

            // Call Ollama API
            const response = await fetch(`${apiUrl}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify({
                    model: modelToCall,
                    prompt: messageText,
                    system: systemPrompt,
                    options: {
                        temperature: 0.3,
                        top_p: 0.9,
                        top_k: 40,
                        repetition_penalty: 1.1
                    },
                    stream: false
                })
            });

            // Remove loading bubble
            if (messagesContainer.contains(loadingDiv)) {
                messagesContainer.removeChild(loadingDiv);
            }

            if (response.ok) {
                const data = await response.json();
                const reply = data.response || "Je n'ai pas reçu de réponse du modèle.";
                appendMessageUI('bot', reply);
                saveMessageToCurrentChat('bot', reply);
            } else {
                const errMsg = `Erreur du serveur (Statut ${response.status}).`;
                appendMessageUI('bot', errMsg);
                saveMessageToCurrentChat('bot', errMsg);
            }
        } catch (error) {
            // Remove loading bubble
            if (messagesContainer.contains(loadingDiv)) {
                messagesContainer.removeChild(loadingDiv);
            }
            const errMsg = "Erreur de connexion. Impossible de contacter le serveur Ollama.";
            appendMessageUI('bot', errMsg);
            saveMessageToCurrentChat('bot', errMsg);
            console.error('API call failed:', error);
        } finally {
            // Re-enable UI
            userInput.disabled = false;
            btnSend.disabled = false;
            userInput.focus();
        }
    });

    // Initialize application storage & state
    loadStorage();
    checkConnection();
    
    // Auto-check connection every 15 seconds
    setInterval(checkConnection, 15000);
});
