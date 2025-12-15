
from model.models import (
    get_engine, get_session, Material, Copia, Prestamo, Reserva
)
from model.usuario import Usuario
from model.models import Rol, UsuarioRol
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class AuthController:
    def __init__(self, session: Session):
        self.session = session
        self.current_user = None

  
    def login(self, usuario: str, password: str) -> bool:
        if not usuario or not password:
            return False

        user = (
            self.session.query(Usuario)
            .filter(Usuario.nombre == usuario)
            .first()
        )

        if user and user.check_password(password):
            self.current_user = user
            return True

        return False



    def register(self, nombre: str, correo: str, password: str, role_name="estudiante"):
        """Registra un usuario nuevo con contraseña encriptada."""
        print("Registrando usuario:", nombre, correo, "con rol:", role_name)
        role = self.session.query(Rol).filter_by(nombre=role_name).first()
        print("ROL ENCONTRADO:", role)


        if not role:
            print("Rol no encontrado:", role_name)
            return False
           
        
        nuevo = Usuario(
            nombre=nombre,
            correo=correo,
        )
        nuevo.set_password(password)

        try:
            self.session.add(nuevo)
            self.session.flush()  
        
            print("Usuario creado con ID:", nuevo.id_usuario)
            nuevo.roles.append(role)


            self.session.commit()
            return True
        except IntegrityError as e:
            print("ERROR SQL:", e.orig)       
            print("DETAIL:", e.args)  
            self.session.rollback()
            return False


    def user_has_role(self, role_name):
        if not self.current_user:
            return False
        return any(r.nombre == role_name for r in self.current_user.roles)

    def logout(self):
        self.current_user = None

    def get_current_user(self):
        return self.current_user
    
    def get_roles(self):
        return self.session.query(Rol).all()
    
    def email_exists(self, email: str) -> bool:
        return (
        self.session.query(Usuario)
        .filter(Usuario.correo == email)
        .first()
        is not None
    )

    def username_exists(self, username: str) -> bool:
        return (
        self.session.query(Usuario)
        .filter(Usuario.nombre == username)
        .first()
        is not None
    )


