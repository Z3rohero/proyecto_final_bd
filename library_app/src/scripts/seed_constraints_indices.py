import sys
import os
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Ajustar path base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from model.db import engine

Session = sessionmaker(bind=engine)
session = Session()

sql_statements = [

    # ======================
    # CHECK CONSTRAINTS
    # ======================
    """
    ALTER TABLE material
    ADD CONSTRAINT chk_anio_publicacion
    CHECK (año_publicacion >= 1500);
    """,

    """
    ALTER TABLE prestamo
    ADD CONSTRAINT chk_multa
    CHECK (multa >= 0);
    """,

    # ======================
    # ÍNDICES
    # ======================
    "CREATE INDEX IF NOT EXISTS idx_material_titulo ON material(titulo);",
    "CREATE INDEX IF NOT EXISTS idx_prestamo_usuario ON prestamo(id_usuario);",
    "CREATE INDEX IF NOT EXISTS idx_copia_estado ON copia(id_estado);",
    "CREATE INDEX IF NOT EXISTS idx_reserva_usuario ON reserva(id_usuario);",

    # ======================
    # VIEWS
    # ======================
    """
    CREATE OR REPLACE VIEW vista_material_disponible AS
    SELECT
        m.titulo,
        c.codigo_copia,
        e.nombre AS estado
    FROM material m
    JOIN copia c ON m.id_material = c.id_material
    JOIN estado e ON c.id_estado = e.id_estado
    WHERE e.nombre = 'disponible';
    """,

    """
    CREATE OR REPLACE VIEW vista_prestamos_activos AS
    SELECT
        u.nombre,
        m.titulo,
        p.fecha_prestamo,
        p.fecha_devolucion_prevista
    FROM prestamo p
    JOIN usuario u ON p.id_usuario = u.id_usuario
    JOIN copia c ON p.id_copia = c.id_copia
    JOIN material m ON c.id_material = m.id_material
    WHERE p.fecha_devolucion_real IS NULL;
    """
]

for stmt in sql_statements:
    try:
        session.execute(text(stmt))
        session.commit()
    except Exception as e:
        session.rollback()
        print(f" Saltando (ya existe o no aplica): {e}")

print(" Constraints, índices y vistas creadas correctamente")
