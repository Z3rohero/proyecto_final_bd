from sqlalchemy.orm import Session
from model.models import Copia, Material, Prestamo, Reserva, Estado
from datetime import date, timedelta


class StudentController:
    def __init__(self, session: Session):
        self.session = session

    # ========================================
    # MÉTODOS PARA CATÁLOGO
    # ========================================
    
    def get_available_materials(self):
        """Obtiene todos los materiales con copias disponibles"""
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        if not estado_disponible:
            return []
        
        materiales = self.session.query(Material).all()
        materiales_disponibles = []
        
        for material in materiales:
            copias_count = self.count_available_copies(material.id_material)
            if copias_count > 0:
                materiales_disponibles.append({
                    'material': material,
                    'copias_disponibles': copias_count
                })
        
        return materiales_disponibles

    def search_available_materials(self, search_text: str):
        """Busca materiales disponibles por título"""
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        if not estado_disponible:
            return []
        
        materiales = self.session.query(Material).filter(
            Material.titulo.ilike(f"%{search_text}%")
        ).all()
        
        materiales_disponibles = []
        
        for material in materiales:
            copias_count = self.count_available_copies(material.id_material)
            if copias_count > 0:
                materiales_disponibles.append({
                    'material': material,
                    'copias_disponibles': copias_count
                })
        
        return materiales_disponibles

    def count_available_copies(self, id_material: int):
        """Cuenta las copias disponibles de un material"""
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        if not estado_disponible:
            return 0
        
        return self.session.query(Copia).filter_by(
            id_material=id_material,
            id_estado=estado_disponible.id_estado
        ).count()

    def get_material_authors(self, material: Material):
        """Obtiene los autores de un material"""
        return ", ".join([ma.autor.nombre for ma in material.autores])

    def request_loan(self, id_material: int, id_usuario: int, dias: int):
        """Crea una solicitud de préstamo"""
        # Buscar una copia disponible
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        if not estado_disponible:
            raise Exception("No se encontró el estado 'disponible'")
        
        copia = self.session.query(Copia).filter_by(
            id_material=id_material,
            id_estado=estado_disponible.id_estado
        ).first()
        
        if not copia:
            raise Exception("No hay copias disponibles")
        
        # Cambiar estado de la copia a "prestado"
        estado_prestado = self.session.query(Estado).filter_by(nombre="prestado").first()
        
        if not estado_prestado:
            raise Exception("No se encontró el estado 'prestado'")
        
        # Crear préstamo
        nuevo_prestamo = Prestamo(
            id_copia=copia.id_copia,
            id_usuario=id_usuario,
            fecha_prestamo=date.today(),
            fecha_devolucion_prevista=date.today() + timedelta(days=dias),
            estado="activo",
            multa=0
        )
        
        copia.id_estado = estado_prestado.id_estado
        
        self.session.add(nuevo_prestamo)
        self.session.commit()
        
        return nuevo_prestamo

    # ========================================
    # MÉTODOS PARA PRÉSTAMOS
    # ========================================
    
    def get_user_loans(self, id_usuario: int):
        """Obtiene todos los préstamos de un usuario"""
        return self.session.query(Prestamo).filter_by(
            id_usuario=id_usuario
        ).order_by(Prestamo.fecha_prestamo.desc()).all()

    def return_loan(self, prestamo: Prestamo):
        """Procesa la devolución de un préstamo"""
        # Cambiar estado del préstamo
        prestamo.estado = "devuelto"
        prestamo.fecha_devolucion_real = date.today()
        
        # Calcular multa si hay retraso
        if prestamo.fecha_devolucion_real > prestamo.fecha_devolucion_prevista:
            dias_retraso = (prestamo.fecha_devolucion_real - prestamo.fecha_devolucion_prevista).days
            prestamo.multa = dias_retraso * 5  # $5 por día de retraso
        
        # Cambiar estado de la copia a disponible
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        if estado_disponible:
            prestamo.copia.id_estado = estado_disponible.id_estado
        
        self.session.commit()
        
        return prestamo

    # ========================================
    # MÉTODOS PARA RESERVAS
    # ========================================
    
    def get_user_reservations(self, id_usuario: int):
        """Obtiene todas las reservas de un usuario"""
        return self.session.query(Reserva).filter_by(
            id_usuario=id_usuario
        ).order_by(Reserva.fecha_reserva.desc()).all()

    def cancel_reservation(self, reserva: Reserva):
        """Cancela una reserva"""
        reserva.estado = "cancelada"
        
        # Liberar la copia si estaba reservada
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        estado_reservado = self.session.query(Estado).filter_by(nombre="reservado").first()
        
        if estado_disponible and estado_reservado:
            if reserva.copia.id_estado == estado_reservado.id_estado:
                reserva.copia.id_estado = estado_disponible.id_estado
        
        self.session.commit()
        
        return reserva
