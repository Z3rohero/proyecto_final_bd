# models.py
import hashlib
import bcrypt
from sqlalchemy import (
    create_engine, Column, Integer, String, Date, DateTime, Text,
    ForeignKey, Numeric, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

from model.base import Base


class Idioma(Base):
    __tablename__ = 'idioma'
    id_idioma = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)


class Rol(Base):
    __tablename__ = 'rol'
    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)

    usuarios = relationship(
        "Usuario",
        secondary="usuario_rol",
        back_populates="roles"
    )


class UsuarioRol(Base):
    __tablename__ = 'usuario_rol'
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario', ondelete='CASCADE'), primary_key=True)
    id_rol = Column(Integer, ForeignKey('rol.id_rol', ondelete='CASCADE'), primary_key=True)

class Autor(Base):
    __tablename__ = 'autor'
    id_autor = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)

class Material(Base):
    __tablename__ = 'material'
    id_material = Column(Integer, primary_key=True)
    titulo = Column(String(300), nullable=False, index=True)
    descripcion = Column(Text)
    id_idioma = Column(Integer, ForeignKey('idioma.id_idioma', ondelete='SET NULL'))
    tipo_material = Column(String(50), nullable=False)
    año_publicacion = Column(Integer)
    isbn = Column(String(30))

    autores = relationship(
        "MaterialAutor",
        cascade="all, delete-orphan",
        back_populates="material"
    )    
    copias = relationship("Copia",
            cascade="all, delete-orphan",
     back_populates="material")


class MaterialAutor(Base):
    __tablename__ = 'material_autor'
    id_material = Column(Integer, ForeignKey('material.id_material', ondelete='CASCADE'), primary_key=True)
    id_autor = Column(Integer, ForeignKey('autor.id_autor', ondelete='CASCADE'), primary_key=True)
    orden = Column(Integer, default=1)

    material = relationship("Material", back_populates="autores")
    autor = relationship("Autor")

class Estado(Base):
    __tablename__ = 'estado'
    id_estado = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)

    copias = relationship("Copia", back_populates="estado_rel")
    movimientos = relationship("Movimiento", back_populates="estado")



class Copia(Base):
    __tablename__ = 'copia'

    id_copia = Column(Integer, primary_key=True)
    
    id_material = Column(Integer, ForeignKey('material.id_material', ondelete='CASCADE'), nullable=False)
    id_estado = Column(Integer, ForeignKey('estado.id_estado'), nullable=False)

    codigo_copia = Column(String(50), unique=True, nullable=False)
    ubicacion = Column(String(200))
    coleccion = Column(String(100), nullable=True)
    formato = Column(String(30), default='fisico')
    fecha_adquisicion = Column(Date, server_default=func.current_date())

    # relaciones
    material = relationship("Material", back_populates="copias")
    estado_rel = relationship("Estado", back_populates="copias")
    prestamos = relationship("Prestamo", back_populates="copia")
    reservas = relationship("Reserva", back_populates="copia")
    movimientos = relationship("Movimiento", back_populates="copia_rel")




class Prestamo(Base):
    __tablename__ = 'prestamo'
    id_prestamo = Column(Integer, primary_key=True)
    id_copia = Column(Integer, ForeignKey('copia.id_copia', ondelete='RESTRICT'))
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario', ondelete='RESTRICT'))
    fecha_prestamo = Column(Date, server_default=func.current_date())
    fecha_devolucion_prevista = Column(Date, nullable=False)
    fecha_devolucion_real = Column(Date, nullable=True)
    estado = Column(String(20), nullable=False)
    multa = Column(Numeric(8,2), default=0)

    copia = relationship("Copia", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")

class Reserva(Base):
    __tablename__ = 'reserva'
    id_reserva = Column(Integer, primary_key=True)
    id_copia = Column(Integer, ForeignKey('copia.id_copia', ondelete='RESTRICT'))
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario', ondelete='RESTRICT'))
    fecha_reserva = Column(DateTime, server_default=func.now())
    estado = Column(String(20), nullable=False)

    copia = relationship("Copia", back_populates="reservas")
    usuario = relationship("Usuario", back_populates="reservas")

class Movimiento(Base):
    __tablename__ = 'movimiento'
    id_movimiento = Column(Integer, primary_key=True)
    id_copia = Column(Integer, ForeignKey('copia.id_copia', ondelete='SET NULL'), nullable=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario', ondelete='SET NULL'), nullable=True)
    id_estado = Column(Integer, ForeignKey('estado.id_estado'), nullable=False)
    fecha_solicitud = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_devolucion = Column(Date, nullable=False)
    detalle = Column(Text)
    
    # relaciones
    estado = relationship("Estado", back_populates="movimientos")
    copia_rel = relationship("Copia", back_populates="movimientos")
    usuario = relationship("Usuario")

class Multa(Base):
    __tablename__ = 'multa'
    id_multa = Column(Integer, primary_key=True)
    id_prestamo = Column(Integer, ForeignKey('prestamo.id_prestamo', ondelete='RESTRICT'), nullable=False)
    id_copia = Column(Integer, ForeignKey('copia.id_copia', ondelete='RESTRICT'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario', ondelete='RESTRICT'), nullable=False)
    dias_atraso = Column(Integer, nullable=False)
    monto = Column(Numeric(10,2), nullable=False)
    fecha_generacion = Column(DateTime, server_default=func.now(), nullable=False)
    estado_pago = Column(String(20), nullable=False, default='pendiente')  # pendiente, pagada
    fecha_pago = Column(DateTime, nullable=True)
    
    # relaciones
    prestamo = relationship("Prestamo")
    copia_rel = relationship("Copia")
    usuario = relationship("Usuario")

# helper to create engine/session externally
def get_engine(connection_string):
    return create_engine(connection_string, echo=False, future=True)

def get_session(engine):
    return sessionmaker(bind=engine, autoflush=False, future=True)()

