SELECT * FROM transactions
WHERE date >= ? AND date <= ?
ORDER BY date DESC, id DESC;
