CREATE VIEW vista_material_disponible AS
SELECT m.titulo, c.codigo_copia, e.nombre AS estado
FROM material m
JOIN copia c ON m.id_material = c.id_material
JOIN estado e ON c.id_estado = e.id_estado
WHERE e.nombre = 'DISPONIBLE';

CREATE VIEW vista_prestamos_activos AS
SELECT u.nombre, m.titulo, p.fecha_prestamo, p.fecha_devolucion_prevista
FROM prestamo p
JOIN usuario u ON p.id_usuario = u.id_usuario
JOIN copia c ON p.id_copia = c.id_copia
JOIN material m ON c.id_material = m.id_material
WHERE p.fecha_devolucion_real IS NULL;
