class MarkdownRenderer {
    static render(markdown) {
        if (!markdown || typeof markdown !== 'string') {
            return '';
        }

        let html = markdown;

        html = this.escapeHtml(html);

        html = html.replace(/^### (.+$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.+$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.+$)/gim, '<h1>$1</h1>');

        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.*?)_/g, '<em>$1</em>');

        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        html = html.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');

        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

        html = html.replace(/^\* (.+$)/gim, '<li>$1</li>');
        html = html.replace(/^- (.+$)/gim, '<li>$1</li>');
        
        html = html.replace(/^\d+\. (.+$)/gim, '<li>$1</li>');

        html = this.wrapListItems(html);

        html = html.replace(/^---$/gim, '<hr>');

        // Обработка таблиц
        html = this.renderTables(html);

        html = html.replace(/^> (.+$)/gim, '<blockquote>$1</blockquote>');

        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');

        if (!html.match(/<(h[1-6]|div|p|ul|ol|blockquote|pre|hr)/)) {
            html = `<p>${html}</p>`;
        } else if (html.match(/^[^<]/)) {
            html = `<p>${html}`;
        }

        html = this.cleanupHtml(html);

        return html;
    }

    static escapeHtml(html) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
        };
        
        return html.replace(/[&<>"']/g, (match) => map[match]);
    }

    static wrapListItems(html) {
        html = html.replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/gs, (match) => {
            return `<ul>${match}</ul>`;
        });

        return html;
    }

    static renderTables(html) {
        // Ищем таблицы в формате markdown
        const tableRegex = /(\|[^\n]*\|\n)+(\|[-:\s\|]*\|\n)(\|[^\n]*\|\n)*/g;
        
        return html.replace(tableRegex, (tableMatch) => {
            const lines = tableMatch.trim().split('\n');
            if (lines.length < 2) return tableMatch;
            
            // Первая строка - заголовки
            const headerLine = lines[0];
            // Вторая строка - разделитель (игнорируем)
            // Остальные строки - данные
            const dataLines = lines.slice(2);
            
            // Парсим заголовки
            const headers = headerLine.split('|')
                .map(cell => cell.trim())
                .filter(cell => cell !== '');
            
            // Парсим данные
            const rows = dataLines.map(line => 
                line.split('|')
                    .map(cell => cell.trim())
                    .filter(cell => cell !== '')
            ).filter(row => row.length > 0);
            
            // Генерируем HTML таблицу
            let tableHtml = '<table class="markdown-table">';
            
            // Заголовок
            if (headers.length > 0) {
                tableHtml += '<thead><tr>';
                headers.forEach(header => {
                    tableHtml += `<th>${header}</th>`;
                });
                tableHtml += '</tr></thead>';
            }
            
            // Данные
            if (rows.length > 0) {
                tableHtml += '<tbody>';
                rows.forEach(row => {
                    tableHtml += '<tr>';
                    row.forEach((cell, index) => {
                        // Ограничиваем количество колонок заголовками
                        if (index < headers.length) {
                            tableHtml += `<td>${cell}</td>`;
                        }
                    });
                    tableHtml += '</tr>';
                });
                tableHtml += '</tbody>';
            }
            
            tableHtml += '</table>';
            return tableHtml;
        });
    }

    static cleanupHtml(html) {
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p><br>/g, '<p>');
        html = html.replace(/<br><\/p>/g, '</p>');
        html = html.replace(/\s+/g, ' ');
        
        return html.trim();
    }

    static renderToElement(element, markdown) {
        if (!element || !markdown) {
            return;
        }

        const html = this.render(markdown);
        element.innerHTML = html;
        
        element.classList.add('markdown-content');
    }

    static createElement(markdown, tagName = 'div') {
        const element = document.createElement(tagName);
        this.renderToElement(element, markdown);
        return element;
    }
}

export default MarkdownRenderer;