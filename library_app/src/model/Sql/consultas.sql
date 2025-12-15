-- 1. Materiales que tienen más de una copia
SELECT titulo
FROM material
WHERE id_material IN (
    SELECT id_material
    FROM copia
    GROUP BY id_material
    HAVING COUNT(*) > 1
);

-- 2. Usuarios con préstamos vencidos
SELECT nombre
FROM usuario
WHERE id_usuario IN (
    SELECT id_usuario
    FROM prestamo
    WHERE fecha_devolucion_real IS NULL
      AND fecha_devolucion_prevista < CURRENT_DATE
);

-- 3. Total de multas acumuladas por usuario
SELECT u.nombre, SUM(p.multa) AS total_multa
FROM usuario u
JOIN prestamo p ON u.id_usuario = p.id_usuario
GROUP BY u.nombre;