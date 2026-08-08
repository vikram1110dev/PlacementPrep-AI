document.addEventListener("DOMContentLoaded", function () {
    const API_BASE = '/api/v1'; // Assuming a proxy or same origin
    const token = localStorage.getItem('token');
    
    // Auth Check
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMsgBtn');
    const chatMessages = document.getElementById('chatMessages');
    const suggestedChips = document.querySelectorAll('.suggested-chip');
    
    let currentConversationId = null;
    let currentMode = 'general';

    // Fetch initial conversations or create one
    async function init() {
        try {
            const res = await fetch(`${API_BASE}/ai/mentor/conversations`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            
            if (data.data && data.data.length > 0) {
                currentConversationId = data.data[0].id;
                loadConversation(currentConversationId);
            } else {
                createNewConversation();
            }
        } catch (error) {
            console.error('Failed to init AI mentor', error);
        }
    }

    async function createNewConversation(mode = 'general') {
        try {
            const res = await fetch(`${API_BASE}/ai/mentor/conversations`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: 'New Conversation', mode: mode })
            });
            const data = await res.json();
            if (data.success) {
                currentConversationId = data.data.id;
                currentMode = data.data.mode;
                chatMessages.innerHTML = '';
                addAIMessage("Hi! I'm your Placement AI Mentor. I can help you with coding questions, interview prep, resume reviews, or study plans. What would you like to focus on today?");
            }
        } catch (error) {
            console.error('Failed to create conversation', error);
        }
    }

    async function loadConversation(convId) {
        try {
            const res = await fetch(`${API_BASE}/ai/mentor/conversations/${convId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            
            if (data.success) {
                chatMessages.innerHTML = '';
                const msgs = data.data.messages;
                if(msgs.length === 0) {
                     addAIMessage("Hi! I'm your Placement AI Mentor. What would you like to focus on today?");
                } else {
                    msgs.forEach(m => {
                        if (m.role === 'user') {
                            renderUserMessage(m.content);
                        } else if (m.role === 'ai' || m.role === 'assistant') {
                            renderAIMessage(m.content);
                        }
                    });
                }
                scrollToBottom();
            }
        } catch (error) {
            console.error('Failed to load conversation', error);
        }
    }

    // Function to get current time formatted
    function getCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12; 
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return hours + ':' + minutes + ' ' + ampm;
    }

    function renderUserMessage(text) {
        const time = getCurrentTime();
        const msgHTML = `
            <div class="chat-msg-row user">
                <div class="chat-avatar user"><i class="bi bi-person-fill"></i></div>
                <div>
                    <div class="chat-bubble chat-user-bubble">${text}</div>
                    <span class="chat-time">${time}</span>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHTML);
    }
    
    function renderAIMessage(text) {
        const time = getCurrentTime();
        const msgHTML = `
            <div class="chat-msg-row ai">
                <div class="chat-avatar ai shadow-sm"><i class="bi bi-robot"></i></div>
                <div>
                    <div class="chat-bubble chat-ai-bubble">${text}</div>
                    <span class="chat-time">${time}</span>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHTML);
    }

    async function sendToAI(text) {
        if(!currentConversationId) {
            await createNewConversation();
        }
        
        chatInput.value = '';
        renderUserMessage(text);
        scrollToBottom();
        
        // Show typing indicator via SSE stream
        const typingId = 'typing-' + Date.now();
        const typingHTML = `
            <div class="chat-msg-row ai" id="${typingId}">
                <div class="chat-avatar ai shadow-sm"><i class="bi bi-robot"></i></div>
                <div>
                    <div class="chat-bubble chat-ai-bubble" id="stream-${typingId}">
                        <div class="typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', typingHTML);
        scrollToBottom();

        const streamBox = document.getElementById(`stream-${typingId}`);
        let fullResponse = "";

        try {
            const response = await fetch(`${API_BASE}/ai/mentor/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message: text,
                    conversation_id: currentConversationId,
                    stream: true
                })
            });

            if(!response.ok) {
                const errorData = await response.json();
                streamBox.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> AI Provider Error: ${errorData.detail || 'Network error'}</span>`;
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            streamBox.innerHTML = ''; // clear typing indicator
            
            while(true) {
                const { done, value } = await reader.read();
                if(done) break;
                
                const chunk = decoder.decode(value, {stream: true});
                const lines = chunk.split('\\n');
                for(let line of lines) {
                    if(line.startsWith('data: ')) {
                        const dataStr = line.replace('data: ', '').trim();
                        if(dataStr === '[DONE]') break;
                        if(dataStr) {
                            try {
                                const parsed = JSON.parse(dataStr);
                                if(parsed.error) {
                                    streamBox.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> ${parsed.error}</span>`;
                                    break;
                                }
                                if(parsed.chunk) {
                                    // simple replace for newlines
                                    fullResponse += parsed.chunk;
                                    streamBox.innerHTML = fullResponse.replace(/\\n/g, '<br>');
                                    scrollToBottom();
                                }
                            } catch(e) {}
                        }
                    }
                }
            }
        } catch (error) {
            console.error(error);
            streamBox.innerHTML = `<span class="text-danger"><i class="bi bi-wifi-off"></i> Connection failed. Please try again.</span>`;
        }
    }

    // Scroll to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event Listeners
    sendBtn.addEventListener('click', () => {
        const val = chatInput.value.trim();
        if(val) sendToAI(val);
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const val = chatInput.value.trim();
            if(val) sendToAI(val);
        }
    });

    // Suggested Chips click
    suggestedChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const text = this.textContent.trim();
            sendToAI(text);
        });
    });

    // Action Cards logic
    const actionCards = document.querySelectorAll('.ai-action-card');
    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const actionText = this.querySelector('h6').textContent.trim();
            let mode = 'general';
            if(actionText.includes('Resume')) mode = 'resume';
            if(actionText.includes('Interview')) mode = 'interview';
            if(actionText.includes('Coding')) mode = 'dsa';
            if(actionText.includes('Company')) mode = 'company';
            if(actionText.includes('Study')) mode = 'aptitude'; // fallback
            
            // start new conversation in this mode
            createNewConversation(mode);
            alert('Switched mode to ' + mode + '! Starting new conversation.');
        });
    });

    // Init on load
    init();

});
