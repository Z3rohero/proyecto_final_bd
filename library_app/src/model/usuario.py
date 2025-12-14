
from sqlalchemy import *
from sqlalchemy.orm import  relationship, sessionmaker
from sqlalchemy.sql import func
from model.base import Base

import bcrypt


class Usuario(Base):
    __tablename__ = 'usuario'
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False, unique=True)
    fecha_registro = Column(Date, server_default=func.current_date())
    password_hash = Column(String(200), nullable=True)
    prestamos = relationship("Prestamo", back_populates="usuario")
    reservas = relationship("Reserva", back_populates="usuario")    


    # Relación many-to-many con roles
    roles = relationship(
        "Rol",
        secondary="usuario_rol",
        back_populates="usuarios"
    )


    def set_password(self, password: str):
        """Genera un hash seguro con bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verifica la contraseña usando bcrypt."""
        if not self.password_hash:
            return False

        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
