from sqlalchemy.orm import Session
from model.models import Movimiento, Prestamo, Copia, Estado
from datetime import date


class PrestamoController:
    def __init__(self, session: Session):
        self.session = session
    
    def get_movimientos_pendientes(self):
        """Obtiene todos los movimientos pendientes (estado = 3 - reservado)"""
        movimientos = self.session.query(Movimiento).filter_by(
            id_estado=3
        ).order_by(Movimiento.fecha_solicitud.desc()).all()
        
        return movimientos
    
    def aprobar_prestamo(self, id_movimiento: int):
        """
        Cambia el estado de reservado a prestado y crea un registro en la tabla Prestamo
        """
        # Buscar el movimiento
        movimiento = self.session.query(Movimiento).filter_by(
            id_movimiento=id_movimiento
        ).first()
        
        if not movimiento:
            raise Exception("Movimiento no encontrado")
        
        # Verificar que tenga una copia asociada
        if not movimiento.id_copia:
            raise Exception("El movimiento no tiene una copia asociada")
        
        # Buscar la copia
        copia = self.session.query(Copia).filter_by(
            id_copia=movimiento.id_copia
        ).first()
        
        if not copia:
            raise Exception("Copia no encontrada")
        
        # Buscar estado "prestado"
        estado_prestado = self.session.query(Estado).filter_by(
            nombre="prestado"
        ).first()
        
        if not estado_prestado:
            raise Exception("No se encontró el estado 'prestado'")
        
        # Obtener id_usuario del movimiento
        id_usuario = movimiento.id_usuario
        
        if not id_usuario:
            raise Exception("El movimiento no tiene un usuario asociado")
        
        # Crear el préstamo
        nuevo_prestamo = Prestamo(
            id_copia=copia.id_copia,
            id_usuario=id_usuario,
            fecha_prestamo=date.today(),
            fecha_devolucion_prevista=movimiento.fecha_devolucion,
            estado="activo",
            multa=0
        )
        
        # Cambiar estado de la copia a "prestado"
        copia.id_estado = estado_prestado.id_estado
        
        # Actualizar el estado del movimiento a prestado (id_estado = estado_prestado.id_estado)
        movimiento.id_estado = estado_prestado.id_estado
        
        # Guardar cambios
        self.session.add(nuevo_prestamo)
        self.session.commit()
        
        return nuevo_prestamo
    
    def rechazar_solicitud(self, id_movimiento: int):
        """
        Rechaza una solicitud de préstamo, devuelve la copia a estado disponible
        """
        # Buscar el movimiento
        movimiento = self.session.query(Movimiento).filter_by(
            id_movimiento=id_movimiento
        ).first()
        
        if not movimiento:
            raise Exception("Movimiento no encontrado")
        
        # Buscar la copia
        if movimiento.id_copia:
            copia = self.session.query(Copia).filter_by(
                id_copia=movimiento.id_copia
            ).first()
            
            if copia:
                # Buscar estado "disponible"
                estado_disponible = self.session.query(Estado).filter_by(
                    nombre="disponible"
                ).first()
                
                if estado_disponible:
                    copia.id_estado = estado_disponible.id_estado
        
        # Eliminar o marcar el movimiento como rechazado
        # Por ahora lo eliminamos, pero podrías crear un estado "rechazado"
        self.session.delete(movimiento)
        self.session.commit()
    
    def get_prestamos_activos(self):
        """Obtiene todos los préstamos activos"""
        return self.session.query(Prestamo).filter_by(
            estado="activo"
        ).order_by(Prestamo.fecha_prestamo.desc()).all()
    
    def get_all_prestamos(self):
        """Obtiene todos los préstamos"""
        return self.session.query(Prestamo).order_by(
            Prestamo.fecha_prestamo.desc()
        ).all()
