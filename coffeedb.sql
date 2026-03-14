SELECT 
    cafe_id, 
    cafe_name, 
    ts_rank(search_document, query) AS relevance
FROM 
    coffee_search_index, 
    plainto_tsquery('portuguese', 'Five') AS query
WHERE 
    search_document @@ query
ORDER BY 
    relevance DESC;
