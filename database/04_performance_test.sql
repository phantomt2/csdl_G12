USE mini_netflix;

EXPLAIN
SELECT content_id, title, release_year, rating_age
FROM content
WHERE title LIKE 'Inception%';