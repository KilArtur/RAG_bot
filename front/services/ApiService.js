class ApiService {
    constructor() {
        // Определяем среду и настраиваем baseUrl
        const hostname = window.location.hostname;
        const port = window.location.port;
        
        if (hostname === 'deeplogix.io' || hostname.includes('deeplogix.io')) {
            // Продакшен на deeplogix.io - используем относительный путь с префиксом
            this.baseUrl = '/rag/api';
        } else if (port === '7001' || hostname === '54.88.62.150') {
            // Запуск через nginx на порту 7001 (локальный или продакшен)
            this.baseUrl = '/api';
        } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
            // Локальная разработка - прямое подключение к бэкенду
            this.baseUrl = 'http://localhost:7000/api';
        } else {
            // Fallback для других случаев
            this.baseUrl = '/api';
        }
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
        this.userId = localStorage.getItem('user_id') || null;
    }

    async askQuestion(question, retryCount = 0) {
        const maxRetries = 2;
        
        try {
            const url = `${this.baseUrl}/v1/question`;
            const requestData = {
                question: question,
                user_id: this.userId
            };
            
            console.log(`Отправка POST запроса к: ${url} (попытка ${retryCount + 1})`);
            const startTime = Date.now();
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    ...this.defaultHeaders,
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                },
                body: JSON.stringify(requestData)
            });

            const endTime = Date.now();
            console.log(`Запрос выполнен за ${endTime - startTime}ms`);
            console.log('Received HTTP response:', response.status, response.statusText);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('HTTP error response body:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorText.substring(0, 200)}`);
            }

            const data = await response.json();
            console.log('JSON data parsed successfully, response size:', data.response ? data.response.length : 0);

            if (data.user_id && data.user_id !== this.userId) {
                this.userId = data.user_id;
                localStorage.setItem('user_id', this.userId);
            }
            
            return {
                response: data.response || data["response: "] || 'Нет ответа от сервера',
                scenario_active: data.scenario_active || false,
                scenario_name: data.scenario_name || null,
                scenario_completed: data.scenario_completed || false,
                source: data.source || 'rag'
            };
        } catch (error) {
            console.error('API Error details:', {
                name: error.name,
                message: error.message,
                stack: error.stack,
                type: typeof error,
                constructor: error.constructor.name
            });
            
            if (error.name === 'AbortError') {
                throw new Error('Request timed out (2 minutes). Generating a complex response took too long.');
            }

            if (error instanceof TypeError && retryCount < maxRetries) {
                console.log(`NetworkError обнаружена, повторяем попытку ${retryCount + 1}/${maxRetries}`);
                if (error.message.includes('fetch') || error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    return this.askQuestion(question, retryCount + 1);
                }
            }

            if (error instanceof TypeError) {
                console.error('TypeError details:', error.message);
                if (error.message.includes('fetch') || error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                    throw new Error(`Network error after ${maxRetries + 1} attempts: ${error.message}. The request may be taking too long. Try asking a simpler question or check if the server is running.`);
                }
            }

            if (error.message.includes('HTTP error')) {
                throw new Error(`Ошибка сервера: ${error.message}. Попробуйте позже.`);
            }

            throw new Error(`Произошла ошибка: ${error.message}. Попробуйте обновить страницу.`);
        }
    }

    async checkHealth() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: this.defaultHeaders,
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
}

export default ApiService;