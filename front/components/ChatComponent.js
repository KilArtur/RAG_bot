import MessageComponent from './MessageComponent.js?v=1.2';
import ApiService from '../services/ApiService.js?v=1.2';
import { debounce, scrollToBottom } from '../utils/helpers.js?v=1.2';

class ChatComponent {
    constructor() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messageForm = document.getElementById('messageForm');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.loadingOverlay = document.getElementById('loadingIndicator');

        this.apiService = new ApiService();
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showWelcomeMessage();
        this.checkServerHealth();
    }

    setupEventListeners() {
        this.messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSendMessage();
        });

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        this.messageInput.addEventListener('input', debounce(() => {
            this.adjustTextareaHeight();
            this.updateSendButtonState();
        }, 100));

        this.newChatBtn.addEventListener('click', () => {
            this.clearChat();
        });

        this.messageInput.addEventListener('focus', () => {
            scrollToBottom(this.messagesContainer);
        });
    }

    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        const newHeight = Math.min(this.messageInput.scrollHeight, 200);
        this.messageInput.style.height = newHeight + 'px';
    }

    updateSendButtonState() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText || this.isLoading;
    }

    showWelcomeMessage() {
        const welcomeText = 'Hello, I can help you with any question';
        const welcomeMessage = MessageComponent.createWelcomeMessage(welcomeText);
        this.messagesContainer.appendChild(welcomeMessage);
        scrollToBottom(this.messagesContainer);
    }

    async checkServerHealth() {
        try {
            const isHealthy = await this.apiService.checkHealth();
            if (!isHealthy) {
                this.showServerErrorMessage();
            }
        } catch (error) {
            console.warn('Health check failed:', error);
        }
    }

    showServerErrorMessage() {
        const errorText = 'Warning: the server may be unavailable. If you encounter issues sending messages, try reloading the page.';
        const errorMessage = MessageComponent.createErrorMessage(errorText);
        this.messagesContainer.appendChild(errorMessage);
        scrollToBottom(this.messagesContainer);
    }

    async handleSendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        this.addUserMessage(message);
        this.clearInput();
        const loadingMessage = this.showLoadingMessage();
        
        // Обновляем сообщение загрузки через 10 секунд
        const updateTimeout = setTimeout(() => {
            const loadingContent = loadingMessage.querySelector('.message__content');
            if (loadingContent && this.isLoading) {
                loadingContent.innerHTML = `
                    <div class="typing-indicator">
                        <div class="typing-indicator__dot"></div>
                        <div class="typing-indicator__dot"></div>
                        <div class="typing-indicator__dot"></div>
                    </div>
                    <span style="margin-left: 8px;">Generating complex answer... Please wait...</span>
                `;
            }
        }, 10000);
        
        try {
            this.setLoadingState(true);
            const responseData = await this.apiService.askQuestion(message);
            clearTimeout(updateTimeout);
            this.hideLoadingMessage(loadingMessage);
            this.addAssistantMessage(responseData.response, responseData);
            
        } catch (error) {
            console.error('Error sending message:', error);
            clearTimeout(updateTimeout);
            this.hideLoadingMessage(loadingMessage);
            this.addErrorMessage(error.message || 'An error occurred while processing the request');
            
        } finally {
            this.setLoadingState(false);
        }
    }

    addUserMessage(content) {
        const userMessage = MessageComponent.create('user', content);
        this.messagesContainer.appendChild(userMessage);
        scrollToBottom(this.messagesContainer);
    }

    addAssistantMessage(content, metadata = {}) {
        const formattedContent = MessageComponent.formatText(content);
        const assistantMessage = MessageComponent.create('assistant', formattedContent);
        
        // Добавляем специальный класс для завершенных сценариев для полной ширины
        if (metadata.scenario_completed) {
            assistantMessage.classList.add('message--scenario-completed');
        }

        // Добавляем индикатор для активных сценариев (но НЕ для завершенных)
        if (metadata.scenario_active && !metadata.scenario_completed) {
            const scenarioIndicator = document.createElement('div');
            scenarioIndicator.className = 'scenario-indicator';
            scenarioIndicator.textContent = `📋 Scenario: ${metadata.scenario_name}`;
            scenarioIndicator.style.cssText = `
                font-size: 12px;
                color: #666;
                margin-bottom: 8px;
                padding: 4px 8px;
                background: #f0f0f0;
                border-radius: 12px;
                display: inline-block;
            `;

            assistantMessage.insertBefore(scenarioIndicator, assistantMessage.firstChild);
        }
        
        this.messagesContainer.appendChild(assistantMessage);
        scrollToBottom(this.messagesContainer);
    }

    addErrorMessage(content) {
        const errorMessage = MessageComponent.createErrorMessage(content);
        this.messagesContainer.appendChild(errorMessage);
        scrollToBottom(this.messagesContainer);
    }

    showLoadingMessage() {
        const loadingMessage = MessageComponent.createLoadingMessage();
        this.messagesContainer.appendChild(loadingMessage);
        scrollToBottom(this.messagesContainer);
        return loadingMessage;
    }

    hideLoadingMessage(loadingMessage) {
        if (loadingMessage && loadingMessage.parentNode) {
            loadingMessage.remove();
        }
    }

    setLoadingState(isLoading) {
        this.isLoading = isLoading;
        this.messageInput.disabled = isLoading;
        this.updateSendButtonState();
    }

    clearInput() {
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        this.updateSendButtonState();
        this.messageInput.focus();
    }

    clearChat() {
        while (this.messagesContainer.firstChild) {
            this.messagesContainer.removeChild(this.messagesContainer.firstChild);
        }
        
        // Сбрасываем user_id для новой сессии
        localStorage.removeItem('user_id');
        this.apiService.userId = null;
        
        this.showWelcomeMessage();
        this.clearInput();
    }

    focus() {
        this.messageInput.focus();
    }
}

export default ChatComponent;