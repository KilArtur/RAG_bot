CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE texts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(1024)
);

-- Добавить колонку для полнотекстового поиска
ALTER TABLE texts ADD COLUMN tsv tsvector;

-- Инициализировать tsvector на основе текстового поля
UPDATE texts SET tsv = to_tsvector('english', text);

-- Создать индекс для ускорения поиска
CREATE INDEX tsv_idx ON texts USING GIN (tsv);
