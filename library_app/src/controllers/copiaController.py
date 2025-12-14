from sqlalchemy.orm import Session
from model.models import Copia, Material, Estado


class CopiaController:
    def __init__(self, session: Session):
        self.session = session

    def get_all_copias(self):
        """Obtiene todas las copias"""
        return self.session.query(Copia).all()

    def get_copia_by_id(self, copia_id: int):
        """Obtiene una copia por ID"""
        return self.session.query(Copia).filter_by(id_copia=copia_id).first()

    def search_copias(self, search_text: str):
        """Busca copias por título del material"""
        return (
            self.session.query(Copia)
            .join(Material)
            .filter(Material.titulo.ilike(f"%{search_text}%"))
            .all()
        )

    def create_copia(self, id_material: int, codigo_copia: str, 
                    ubicacion: str = None, coleccion: str = None,
                    id_estado: int = None, formato: str = "fisico"):
        """Crea una nueva copia"""
        nueva_copia = Copia(
            id_material=id_material,
            codigo_copia=codigo_copia,
            ubicacion=ubicacion,
            coleccion=coleccion,
            id_estado=id_estado,
            formato=formato
        )
        self.session.add(nueva_copia)
        self.session.commit()
        return nueva_copia

    def update_copia(self, copia_id: int, id_material: int = None,
                    codigo_copia: str = None, ubicacion: str = None,
                    coleccion: str = None, id_estado: int = None,
                    formato: str = None):
        """Actualiza una copia existente"""
        copia = self.get_copia_by_id(copia_id)
        if not copia:
            return None

        if id_material is not None:
            copia.id_material = id_material
        if codigo_copia is not None:
            copia.codigo_copia = codigo_copia
        if ubicacion is not None:
            copia.ubicacion = ubicacion
        if coleccion is not None:
            copia.coleccion = coleccion
        if id_estado is not None:
            copia.id_estado = id_estado
        if formato is not None:
            copia.formato = formato

        self.session.commit()
        return copia

    def delete_copia(self, copia_id: int):
        """Elimina una copia"""
        copia = self.get_copia_by_id(copia_id)
        if copia:
            self.session.delete(copia)
            self.session.commit()
            return True
        return False

    def get_all_materiales(self):
        """Obtiene todos los materiales para el dropdown"""
        return self.session.query(Material).all()

    def get_all_estados(self):
        """Obtiene todos los estados disponibles"""
        return self.session.query(Estado).order_by(Estado.nombre).all()

    def get_copia_material_title(self, copia: Copia):
        """Obtiene el título del material de una copia"""
        return copia.material.titulo if copia.material else ""

    def get_copia_material_isbn(self, copia: Copia):
        """Obtiene el ISBN del material de una copia"""
        return copia.material.isbn if copia.material else ""

    def get_copia_estado_nombre(self, copia: Copia):
        """Obtiene el nombre del estado de una copia"""
        return copia.estado_rel.nombre if copia.estado_rel else ""
