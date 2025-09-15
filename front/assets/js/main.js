import ChatComponent from '../../components/ChatComponent.js?v=1.2';

class App {
    constructor() {
        this.chat = null;
        this.init();
    }

    /**
     * Инициализация приложения
     */
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }

    /**
     * Обработчик готовности DOM
     */
    onDOMReady() {
        try {
            this.chat = new ChatComponent();

            this.setupGlobalEventListeners();

            this.chat.focus();
            
            console.log('RAG Bot initialized successfully');
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showErrorMessage('Application initialization error');
        }
    }

    /**
     * Настройка глобальных обработчиков событий
     */
    setupGlobalEventListeners() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.handleGlobalError(event.error);
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });

        window.addEventListener('resize', this.debounce(() => {
            this.handleWindowResize();
        }, 250));

        window.addEventListener('offline', () => {
            this.showConnectionStatus(false);
        });

        window.addEventListener('online', () => {
            this.showConnectionStatus(true);
        });

        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
    }

    /**
     * Обработчик глобальных ошибок
     * @param {Error} error - Объект ошибки
     */
    handleGlobalError(error) {
        if (process?.env?.NODE_ENV !== 'production') {
            console.error('Global error handled:', error);
        }
    }

    /**
     * Обработчик изменения размера окна
     */
    handleWindowResize() {
        if (this.chat && this.chat.messagesContainer) {
            setTimeout(() => {
                this.chat.messagesContainer.scrollTop = this.chat.messagesContainer.scrollHeight;
            }, 100);
        }
    }

    /**
     * Показывает статус соединения
     * @param {boolean} isOnline - Статус соединения
     */
    showConnectionStatus(isOnline) {
        this.showNotification(
            isOnline ? 'Connection restored' : 'No internet connection',
            isOnline ? 'success' : 'error',
            3000
        );
    }

    /**
     * Обработчик клавиатурных сокращений
     * @param {KeyboardEvent} event - Событие клавиатуры
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K - очистить чат
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            if (this.chat) {
                this.chat.clearChat();
            }
        }

        // Escape - фокус на поле ввода
        if (event.key === 'Escape') {
            if (this.chat) {
                this.chat.focus();
            }
        }
    }

    /**
     * Показывает уведомление пользователю
     * @param {string} message - Текст уведомления
     * @param {string} type - Тип уведомления (success, error, info)
     * @param {number} duration - Длительность показа в мс
     */
    showNotification(message, type = 'info', duration = 3000) {
        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.textContent = message;
        
        // Добавляем стили
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: '9999',
            opacity: '0',
            transform: 'translateY(-20px)',
            transition: 'all 0.3s ease',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });

        // Цвета для разных типов уведомлений
        const colors = {
            success: '#2ed573',
            error: '#ff4757',
            info: '#10a37f',
            warning: '#ffa502'
        };

        notification.style.backgroundColor = colors[type] || colors.info;

        // Добавляем в DOM
        document.body.appendChild(notification);

        // Анимация появления
        requestAnimationFrame(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        });

        // Автоматическое удаление
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }

    /**
     * Показывает сообщение об ошибке
     * @param {string} message - Текст ошибки
     */
    showErrorMessage(message) {
        this.showNotification(message, 'error', 5000);
    }

    /**
     * Debounce утилита
     * @param {Function} func - Функция для выполнения
     * @param {number} wait - Задержка в миллисекундах
     * @returns {Function} - Debounced функция
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Запуск приложения
new App();