START TRANSACTION;
-- Index for books on status, title?, and author id
ALTER TABLE books
    ADD INDEX idx_books_author (author_id),
    ADD INDEX idx_books_title (title),
    ADD INDEX idx_books_status (status);

-- Index for keywords words
ALTER TABLE keywords
    ADD INDEX idx_keywords_word (word);

ALTER TABLE book_keywords
    ADD INDEX idx_book_keywords_book_id (book_id),
    ADD INDEX idx_book_keywords_keyword_id (keyword_id);

-- Index for author name
ALTER TABLE authors
    ADD INDEX idx_authors_name (name);

-- Index for orders user_id and payment_status
ALTER TABLE orders
    ADD INDEX idx_orders_user_id (user_id),
    ADD INDEX idx_orders_payment_status (payment_status);