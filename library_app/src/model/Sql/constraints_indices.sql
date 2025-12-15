-- CHECKS
ALTER TABLE material
ADD CONSTRAINT chk_anio_publicacion
CHECK (año_publicacion >= 1500);

ALTER TABLE prestamo
ADD CONSTRAINT chk_multa
CHECK (multa >= 0);

-- ÍNDICES
CREATE INDEX idx_material_titulo ON material(titulo);
CREATE INDEX idx_prestamo_usuario ON prestamo(id_usuario);
CREATE INDEX idx_copia_estado ON copia(id_estado);
CREATE INDEX idx_reserva_usuario ON reserva(id_usuario);
