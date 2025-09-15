class ChatApp {
    constructor() {
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        
        this.initEventListeners();
        this.showWelcomeMessage();
    }

    initEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
        });

        this.newChatBtn.addEventListener('click', () => this.clearChat());
    }

    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
    }

    showWelcomeMessage() {
        this.addMessage('assistant', 'Hello! I am RAG-bot ready to answer your questions about the book. Ask any question!');
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        
        this.setLoading(true);
        
        try {
            const response = await this.callAPI(message);
            this.addMessage('assistant', response);
        } catch (error) {
            this.addMessage('assistant', 'Sorry, there was an error processing your request. Please try again.');
            console.error('API Error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    async callAPI(question) {
        const response = await fetch(`/api/v1/question?question=${encodeURIComponent(question)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data["response: "] || data.response || 'No response from server';
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? 'Вы' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    setLoading(isLoading) {
        if (isLoading) {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant loading-message';
            loadingDiv.innerHTML = `
                <div class="message-avatar">AI</div>
                <div class="message-content loading">Thinking...</div>
            `;
            this.messagesContainer.appendChild(loadingDiv);
        } else {
            const loadingMessage = this.messagesContainer.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }
        
        this.sendBtn.disabled = isLoading;
        this.messageInput.disabled = isLoading;
        this.scrollToBottom();
    }

    clearChat() {
        this.messagesContainer.innerHTML = '';
        this.showWelcomeMessage();
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});