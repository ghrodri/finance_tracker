SELECT * FROM entries
WHERE (recurring = 1 AND start_month <= ? AND (end_month IS NULL OR end_month >= ?))
   OR (recurring = 0 AND start_month = ?)
ORDER BY kind, id;
