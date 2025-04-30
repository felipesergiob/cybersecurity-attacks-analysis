SELECT 
    DATE_TRUNC('day', t.timestamp) as "Data",
    at.attack_type as "Tipo de Ataque",
    COUNT(*) as "Total de Ataques"
FROM raw_cybersecurity_attacks r
JOIN dim_attack_type at ON r."Attack Type" = at.attack_type
JOIN dim_timestamp t ON r."Timestamp"::timestamp = t.timestamp
GROUP BY DATE_TRUNC('day', t.timestamp), at.attack_type
ORDER BY "Data";