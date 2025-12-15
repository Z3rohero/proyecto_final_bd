CREATE ROLE admin LOGIN PASSWORD 'admin123';
CREATE ROLE bibliotecario LOGIN PASSWORD 'biblio123';
CREATE ROLE lector LOGIN PASSWORD 'lector123';

-- ADMIN
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;

-- BIBLIOTECARIO
GRANT SELECT, INSERT, UPDATE ON
material, copia, prestamo, reserva, movimiento TO bibliotecario;

-- LECTOR
GRANT SELECT ON
material, autor, idioma, copia TO lector;
