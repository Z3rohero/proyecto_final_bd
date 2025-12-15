from sqlalchemy.orm import Session
from model.models import Copia, Material, Prestamo, Reserva, Estado, Movimiento, Multa
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
    
    def get_all_materials_with_copies(self):
        """Obtiene todos los materiales con copias disponibles y prestadas"""
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        estado_prestado = self.session.query(Estado).filter_by(nombre="prestado").first()
        
        if not estado_disponible or not estado_prestado:
            return []
        
        materiales = self.session.query(Material).all()
        materiales_con_copias = []
        
        for material in materiales:
            copias_disponibles = self.session.query(Copia).filter_by(
                id_material=material.id_material,
                id_estado=estado_disponible.id_estado
            ).count()
            
            copias_prestadas = self.session.query(Copia).filter_by(
                id_material=material.id_material,
                id_estado=estado_prestado.id_estado
            ).count()
            
            if copias_disponibles > 0 or copias_prestadas > 0:
                materiales_con_copias.append({
                    'material': material,
                    'copias_disponibles': copias_disponibles,
                    'copias_prestadas': copias_prestadas
                })
        
        return materiales_con_copias
    
    def search_materials_with_copies(self, search_text: str):
        """Busca materiales por título mostrando disponibles y prestadas"""
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        estado_prestado = self.session.query(Estado).filter_by(nombre="prestado").first()
        
        if not estado_disponible or not estado_prestado:
            return []
        
        materiales = self.session.query(Material).filter(
            Material.titulo.ilike(f"%{search_text}%")
        ).all()
        
        materiales_con_copias = []
        
        for material in materiales:
            copias_disponibles = self.session.query(Copia).filter_by(
                id_material=material.id_material,
                id_estado=estado_disponible.id_estado
            ).count()
            
            copias_prestadas = self.session.query(Copia).filter_by(
                id_material=material.id_material,
                id_estado=estado_prestado.id_estado
            ).count()
            
            if copias_disponibles > 0 or copias_prestadas > 0:
                materiales_con_copias.append({
                    'material': material,
                    'copias_disponibles': copias_disponibles,
                    'copias_prestadas': copias_prestadas
                })
        
        return materiales_con_copias
    
    def create_reservation(self, id_material: int, id_usuario: int):
        """Crea una reserva de una copia prestada"""
        # Verificar si el usuario tiene multas pendientes
        if self.tiene_multas_pendientes(id_usuario):
            raise Exception("No puedes crear reservas. Tienes multas pendientes por pagar.")
        
        # Buscar una copia prestada
        estado_prestado = self.session.query(Estado).filter_by(nombre="prestado").first()
        
        if not estado_prestado:
            raise Exception("No se encontró el estado 'prestado'")
        
        copia = self.session.query(Copia).filter_by(
            id_material=id_material,
            id_estado=estado_prestado.id_estado
        ).first()
        
        if not copia:
            raise Exception("No hay copias prestadas para reservar")
        
        # Verificar si el usuario ya tiene una reserva activa para esta copia
        reserva_existente = self.session.query(Reserva).filter_by(
            id_copia=copia.id_copia,
            id_usuario=id_usuario,
            estado="activa"
        ).first()
        
        if reserva_existente:
            raise Exception("Ya tienes una reserva activa para este material")
        
        # Crear la reserva
        nueva_reserva = Reserva(
            id_copia=copia.id_copia,
            id_usuario=id_usuario,
            estado="activa"
        )
        
        self.session.add(nueva_reserva)
        self.session.commit()
        
        return nueva_reserva

    def request_loan(self, id_material: int, id_usuario: int, dias: int):
        """Crea una solicitud de préstamo con estado reservado"""
        # Verificar si el usuario tiene multas pendientes
        if self.tiene_multas_pendientes(id_usuario):
            raise Exception("No puedes solicitar préstamos. Tienes multas pendientes por pagar.")
        
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
        
        # Cambiar estado de la copia a "reservado"
        estado_reservado = self.session.query(Estado).filter_by(nombre="reservado").first()
        
        if not estado_reservado:
            raise Exception("No se encontró el estado 'reservado'")
        
        # Calcular fecha de devolución
        fecha_devolucion = date.today() + timedelta(days=dias)
        
        # Crear movimiento con estado por defecto id = 3
        nuevo_movimiento = Movimiento(
            id_copia=copia.id_copia,
            id_usuario=id_usuario,
            id_estado=3,
            fecha_devolucion=fecha_devolucion,
            detalle=f"Solicitud de préstamo de usuario {id_usuario} por {dias} días"
        )
        
        copia.id_estado = estado_reservado.id_estado
        
        self.session.add(nuevo_movimiento)
        self.session.commit()
        
        return nuevo_movimiento

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
            
            # Calcular monto de multa según tabla de valores
            monto_multa = self.calcular_multa(dias_retraso)
            
            # Guardar monto en el préstamo
            prestamo.multa = monto_multa
            
            # Crear registro de multa en la tabla Multa
            nueva_multa = Multa(
                id_prestamo=prestamo.id_prestamo,
                id_copia=prestamo.id_copia,
                id_usuario=prestamo.id_usuario,
                dias_atraso=dias_retraso,
                monto=monto_multa,
                estado_pago='pendiente'
            )
            
            self.session.add(nueva_multa)
        
        # Cambiar estado de la copia a disponible
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        if estado_disponible:
            prestamo.copia.id_estado = estado_disponible.id_estado
        
        self.session.commit()
        
        return prestamo
    
    def calcular_multa(self, dias_atraso: int) -> float:
        """
        Calcula el monto de la multa según los días de atraso
        1er día: 1000 COP
        2º al 7º día: 2500 COP
        8º día en adelante: 2500 + 100 COP por cada día adicional
        """
        if dias_atraso == 1:
            return 1000.0
        elif 2 <= dias_atraso <= 7:
            return 2500.0
        else:  # 8 días o más
            # 2500 base + 100 por cada día después del 7mo
            dias_adicionales = dias_atraso - 7
            return 2500.0 + (dias_adicionales * 100.0)
    
    def tiene_multas_pendientes(self, id_usuario: int) -> bool:
        """Verifica si el usuario tiene multas pendientes sin pagar"""
        multas_pendientes = self.session.query(Multa).filter_by(
            id_usuario=id_usuario,
            estado_pago='pendiente'
        ).count()
        
        return multas_pendientes > 0

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
