from sqlalchemy.orm import Session
from model.models import Reserva, Copia, Estado
from datetime import datetime


class ReservaController:
    def __init__(self, session: Session):
        self.session = session
    
    def get_reservas_activas(self):
        """Obtiene todas las reservas activas"""
        return self.session.query(Reserva).filter_by(
            estado="activa"
        ).order_by(Reserva.fecha_reserva.desc()).all()
    
    def get_all_reservas(self):
        """Obtiene todas las reservas"""
        return self.session.query(Reserva).order_by(
            Reserva.fecha_reserva.desc()
        ).all()
    
    def cancelar_reserva(self, id_reserva: int):
        """Cancela una reserva"""
        reserva = self.session.query(Reserva).filter_by(
            id_reserva=id_reserva
        ).first()
        
        if not reserva:
            raise Exception("Reserva no encontrada")
        
        reserva.estado = "cancelada"
        self.session.commit()
        
        return reserva
    
    def completar_reserva(self, id_reserva: int):
        """Marca una reserva como completada (el usuario recogió el libro)"""
        reserva = self.session.query(Reserva).filter_by(
            id_reserva=id_reserva
        ).first()
        
        if not reserva:
            raise Exception("Reserva no encontrada")
        
        reserva.estado = "completada"
        self.session.commit()
        
        return reserva
    
    def liberar_copia_para_reserva(self, id_copia: int):
        """
        Cuando una copia es devuelta, verifica si hay reservas activas
        y notifica al primer usuario en la lista
        """
        # Buscar reservas activas para esta copia
        reserva = self.session.query(Reserva).filter_by(
            id_copia=id_copia,
            estado="activa"
        ).order_by(Reserva.fecha_reserva.asc()).first()
        
        if reserva:
            # Cambiar estado de la copia a "reservado" para el usuario
            estado_reservado = self.session.query(Estado).filter_by(
                nombre="reservado"
            ).first()
            
            if estado_reservado and reserva.copia:
                reserva.copia.id_estado = estado_reservado.id_estado
                self.session.commit()
                
            return reserva
        
        return None
