import MarkdownRenderer from '../utils/MarkdownRenderer.js?v=1.1';

class MessageComponent {
    static create(role, content, options = {}) {
        const messageElement = document.createElement('div');
        messageElement.className = `message message--${role}`;
        
        if (options.isWelcome) {
            messageElement.classList.add('message--welcome');
        }
        
        if (options.isError) {
            messageElement.classList.add('message--error');
        }
        
        if (options.isLoading) {
            messageElement.classList.add('message--loading');
        }

        const avatar = this.createAvatar(role);
        const messageContent = this.createContent(content, { ...options, role });

        messageElement.appendChild(avatar);
        messageElement.appendChild(messageContent);

        requestAnimationFrame(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });

        return messageElement;
    }

    static createAvatar(role) {
        const avatar = document.createElement('div');
        avatar.className = 'message__avatar';
        
        if (role === 'user') {
            avatar.textContent = '';
        } else {
            avatar.textContent = 'AI';
        }

        return avatar;
    }

    static createContent(content, options = {}) {
        const messageContent = document.createElement('div');
        messageContent.className = 'message__content';

        if (options.isLoading) {
            messageContent.innerHTML = this.createLoadingContent();
        } else if (options.role === 'assistant' && content) {
            MarkdownRenderer.renderToElement(messageContent, content);
        } else {
            messageContent.textContent = content;
        }

        return messageContent;
    }

    static createLoadingContent() {
        return `
            <div class="typing-indicator">
                <div class="typing-indicator__dot"></div>
                <div class="typing-indicator__dot"></div>
                <div class="typing-indicator__dot"></div>
            </div>
            <span style="margin-left: 8px;">Генерирую подробный ответ... (это может занять до 2 минут)</span>
        `;
    }

    static createLoadingMessage() {
        return this.create('assistant', '', { 
            isLoading: true 
        });
    }

    static createWelcomeMessage(content) {
        return this.create('assistant', content, { 
            isWelcome: true 
        });
    }

    static createErrorMessage(content) {
        return this.create('assistant', content, { 
            isError: true 
        });
    }

    static updateContent(messageElement, newContent) {
        const contentElement = messageElement.querySelector('.message__content');
        if (contentElement) {
            const isAssistant = messageElement.classList.contains('message--assistant');
            
            if (isAssistant && newContent) {
                MarkdownRenderer.renderToElement(contentElement, newContent);
            } else {
                contentElement.textContent = newContent;
            }
            
            messageElement.classList.remove('message--loading');
        }
    }

    static formatText(text) {
        return text
            .trim()
            .replace(/\n\s*\n/g, '\n\n')
            .replace(/^\s+/gm, '');
    }

    static isLoadingMessage(element) {
        return element && element.classList.contains('message--loading');
    }
}

export default MessageComponent;