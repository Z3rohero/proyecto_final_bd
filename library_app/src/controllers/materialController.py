from sqlalchemy.orm import Session
from model.models import Material, Autor, MaterialAutor, Idioma


class MaterialController:
    def __init__(self, session: Session):
        self.session = session

    def get_all_materials(self):
        """Obtiene todos los materiales"""
        return self.session.query(Material).all()

    def search_materials(self, search_text: str):
        """Busca materiales por título"""
        return (
            self.session.query(Material)
            .filter(Material.titulo.ilike(f"%{search_text}%"))
            .all()
        )

    def get_material_by_id(self, material_id: int):
        """Obtiene un material por ID"""
        return self.session.query(Material).filter_by(id_material=material_id).first()

    def create_material(self, titulo: str, descripcion: str = None, 
                       año_publicacion: int = None, id_idioma: int = None,
                       tipo_material: str = "libro", isbn: str = None):
        """Crea un nuevo material"""
        nuevo_material = Material(
            titulo=titulo,
            descripcion=descripcion,
            año_publicacion=año_publicacion,
            id_idioma=id_idioma,
            tipo_material=tipo_material,
            isbn=isbn
        )
        self.session.add(nuevo_material)
        self.session.commit()
        return nuevo_material

    def update_material(self, material_id: int, titulo: str = None, 
                       descripcion: str = None, año_publicacion: int = None):
        """Actualiza un material existente"""
        material = self.get_material_by_id(material_id)
        if not material:
            return None

        if titulo is not None:
            material.titulo = titulo
        if descripcion is not None:
            material.descripcion = descripcion
        if año_publicacion is not None:
            material.año_publicacion = año_publicacion

        self.session.commit()
        return material

    def delete_material(self, material_id: int):
        """Elimina un material"""
        material = self.get_material_by_id(material_id)
        if material:
            self.session.delete(material)
            self.session.commit()
            return True
        return False

    def get_material_authors(self, material: Material):
        """Obtiene los autores de un material como string"""
        return ", ".join([ma.autor.nombre for ma in material.autores])

    def get_all_idiomas(self):
        """Obtiene todos los idiomas"""
        return self.session.query(Idioma).all()
