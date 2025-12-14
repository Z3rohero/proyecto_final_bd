from sqlalchemy.orm import Session
from model.usuario import Usuario


class UserController:
    def __init__(self, session: Session):
        self.session = session

    def get_all_user(self):
        """Obtiene todos los usuarios"""
        return self.session.query(Usuario).all()

    def search_user(self, search_text: str):
        """Buscar usuario por nombre o correo"""
        query = self.session.query(Usuario)
        
        if not search_text:
            return self.get_all_user()
    
        search_text = search_text.strip()
        query = self.session.query(Usuario)
    
        if search_text.isdigit():
            return query.filter(Usuario.id_usuario == int(search_text)).all()
        
        return query.filter(
            (Usuario.nombre.ilike(f"%{search_text}%")) |
            (Usuario.correo.ilike(f"%{search_text}%"))
        ).all()
    
    #Usuuarios
    def get_user_by_id(self, user_id: int):
        """Obtiene un usuario por ID"""
        return (
            self.session.query(Usuario).filter_by(id_usuario=user_id).first()
        )

    #Busqueda de usuarios
    def create_user(self, nombre: str, correo: str, password: str = None):
        """Crea un nuevo usuario"""
        nuevo_usuario = Usuario(nombre=nombre,correo=correo)

        if password:
            nuevo_usuario.set_password(password)

        self.session.add(nuevo_usuario)
        self.session.commit()
        return nuevo_usuario

    #Modificar usuarios
    def update_user(self, user_id: int, nombre: str = None, correo: str = None):
        """Actualiza un usuario existente"""
        usuario = self.get_user_by_id(user_id)
        if not usuario:
            return None

        if nombre is not None:
            usuario.nombre = nombre
        if correo is not None:
            usuario.correo = correo

        self.session.commit()
        return usuario
    
    #Eliminacion de usuarioo
    def delete_user(self, user_id: int):
        """Elimina un usuario"""
        usuario = self.get_user_by_id(user_id)
        if usuario:
            self.session.delete(usuario)
            self.session.commit()
            return True
            
        return False
