SELECT 
    at.attack_type as "Tipo de Ataque",
    s.severity as "Nível de Severidade",
    COUNT(*) as "Total de Ataques"
FROM raw_cybersecurity_attacks r
JOIN dim_attack_type at ON r."Attack Type" = at.attack_type
JOIN dim_severity s ON r."Severity Level" = s.severity
GROUP BY at.attack_type, s.severity
ORDER BY COUNT(*) DESC;