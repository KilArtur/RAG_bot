import scrapy
from urllib.parse import urlparse

class UniversitySpider(scrapy.Spider):
    name = "university_links"
    start_urls = ["https://guap.ru/"]  # Замените на URL вашего университета
    allowed_domains = ["guap.ru"]    # Ограничение домена
    pages_file = "pages_links.txt"
    files_file = "files_links.txt"
    processed_links = set()  # Множество для уникальных ссылок

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Очищаем файлы перед записью новых ссылок
        open(self.pages_file, "w").close()
        open(self.files_file, "w").close()

    def parse(self, response):

        # Обрабатываем все ссылки на странице
        for link in response.css("a::attr(href)").getall():
            absolute_link = response.urljoin(link)

            if absolute_link in self.processed_links:
                continue  # Пропускаем уже обработанные ссылки

            if self.should_exclude_link(absolute_link):
                continue  # Пропускаем ссылки с якорями или почтовые адреса

            self.processed_links.add(absolute_link)  # Добавляем в обработанные ссылки

            if self.is_document(absolute_link):
                self.save_link(absolute_link, self.files_file)
            elif self.is_internal_link(absolute_link):
                self.save_link(absolute_link, self.pages_file)
                # Продолжаем сканирование внутренних ссылок
                yield scrapy.Request(absolute_link, callback=self.parse)

    def save_link(self, link, filename):
        """Сохраняем ссылку в указанный файл."""
        with open(filename, "a", encoding="utf-8") as f:
            f.write(link + "\n")
        self.log(f"Ссылка сохранена: {link} -> {filename}")

    def is_internal_link(self, link):
        """Проверяем, что ссылка ведёт на тот же домен."""
        return urlparse(link).netloc == self.allowed_domains[0]

    def is_document(self, link):
        """Проверяем, что ссылка ведёт на документ."""
        extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]
        return any(link.lower().endswith(ext) for ext in extensions)

    def should_exclude_link(self, link):
        """Проверяем, нужно ли исключить ссылку."""
        # Исключаем ссылки с якорями (#) и почтовыми адресами (mailto:)
        return "#" in link or "mailto:" in link
