export function debounce(func, wait, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

export function scrollToBottom(container, smooth = true) {
    if (!container) return;
    
    const scrollOptions = {
        top: container.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
    };

    requestAnimationFrame(() => {
        container.scrollTo(scrollOptions);
    });
}

export function isScrolledToBottom(container, threshold = 50) {
    if (!container) return false;
    
    const { scrollTop, scrollHeight, clientHeight } = container;
    return scrollTop + clientHeight >= scrollHeight - threshold;
}


export function formatFileSize(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}


export function formatTime(date, options = {}) {
    const defaultOptions = {
        hour: '2-digit',
        minute: '2-digit',
        ...options
    };
    
    try {
        const dateObj = date instanceof Date ? date : new Date(date);
        return dateObj.toLocaleTimeString('ru-RU', defaultOptions);
    } catch (error) {
        console.error('Error formatting time:', error);
        return '';
    }
}


export function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        ...options
    };
    
    try {
        const dateObj = date instanceof Date ? date : new Date(date);
        return dateObj.toLocaleDateString('ru-RU', defaultOptions);
    } catch (error) {
        console.error('Error formatting date:', error);
        return '';
    }
}


export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


export function stripHtml(html) {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
}


export function isLocalStorageSupported() {
    try {
        const testKey = '__localStorage_test__';
        localStorage.setItem(testKey, 'test');
        localStorage.removeItem(testKey);
        return true;
    } catch (error) {
        return false;
    }
}


export function setLocalStorage(key, value) {
    if (!isLocalStorageSupported()) return false;
    
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        return false;
    }
}


export function getLocalStorage(key, defaultValue = null) {
    if (!isLocalStorageSupported()) return defaultValue;
    
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return defaultValue;
    }
}


export function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}


export async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return true;
        } else {
            // Fallback для старых браузеров
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            return success;
        }
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        return false;
    }
}


export function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}


export function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}


export function addEventListenerOnce(element, event, handler, options = {}) {
    const onceHandler = (e) => {
        handler(e);
        element.removeEventListener(event, onceHandler, options);
    };
    element.addEventListener(event, onceHandler, options);
}