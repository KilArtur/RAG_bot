CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS texts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(1024),
    tsv TSVECTOR,
    link TEXT
);

-- Инициализировать tsvector на основе текстового поля
UPDATE texts SET tsv = to_tsvector('russian', text);

-- Создать индекс для полнотекстового поиска
CREATE INDEX IF NOT EXISTS tsv_idx ON texts USING GIN (tsv);

-- Создать индекс для ускорения поиска BM25
CREATE INDEX IF NOT EXISTS bm25_idx ON texts USING GIN (to_tsvector('russian', text));
