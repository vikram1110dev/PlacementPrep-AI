document.addEventListener("DOMContentLoaded", function () {
    
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMsgBtn');
    const chatMessages = document.getElementById('chatMessages');
    const suggestedChips = document.querySelectorAll('.suggested-chip');

    // Function to get current time formatted
    function getCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; 
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return hours + ':' + minutes + ' ' + ampm;
    }

    // Function to add user message
    function addUserMessage(text) {
        if(!text.trim()) return;

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
        scrollToBottom();
        chatInput.value = '';

        // Trigger AI Response
        showTypingIndicator();
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const typingHTML = `
            <div class="chat-msg-row ai" id="${typingId}">
                <div class="chat-avatar ai"><i class="bi bi-robot"></i></div>
                <div>
                    <div class="chat-bubble chat-ai-bubble">
                        <div class="typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', typingHTML);
        scrollToBottom();

        // Simulate network delay then respond
        setTimeout(() => {
            const typingEl = document.getElementById(typingId);
            if(typingEl) typingEl.remove();
            
            // Random mock response
            const responses = [
                "That's a great question! Based on your current progress, I suggest focusing on Dynamic Programming before jumping into that.",
                "Here is a generated study plan tailored for you. Focus on solving 2 Medium level DSA problems every day.",
                "I've analyzed your resume. Your ATS score is currently 75%. Try incorporating more action verbs like 'Developed', 'Engineered', and 'Architected'.",
                "Binary Search is a divide and conquer algorithm. It requires a sorted array and operates in O(log n) time complexity. Shall I give you a practice problem?",
                "I recommend reviewing the 'Systems Design' module next. Most product-based companies like Amazon emphasize scalable architectures."
            ];
            const randomRes = responses[Math.floor(Math.random() * responses.length)];
            addAIMessage(randomRes);
        }, 1500);
    }

    // Function to add AI message
    function addAIMessage(text) {
        const time = getCurrentTime();
        const msgHTML = `
            <div class="chat-msg-row ai">
                <div class="chat-avatar ai"><i class="bi bi-robot"></i></div>
                <div>
                    <div class="chat-bubble chat-ai-bubble">${text}</div>
                    <span class="chat-time">${time}</span>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHTML);
        scrollToBottom();
    }

    // Scroll to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event Listeners
    sendBtn.addEventListener('click', () => {
        addUserMessage(chatInput.value);
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addUserMessage(chatInput.value);
        }
    });

    // Suggested Chips click
    suggestedChips.forEach(chip => {
        chip.addEventListener('click', function() {
            addUserMessage(this.textContent.trim());
        });
    });

    // Action Cards Mock Click
    const actionCards = document.querySelectorAll('.ai-action-card, .action-pill');
    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const actionText = this.textContent.trim();
            // Simulate the action being sent to AI
            chatInput.value = "I need help with: " + actionText.replace(/[\n\r]+|[\s]{2,}/g, ' ').substring(0, 50);
            chatInput.focus();
        });
    });

});
