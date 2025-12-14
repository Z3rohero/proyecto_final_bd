import flet as ft
from sqlalchemy.orm import Session
from controllers.prestamoController import PrestamoController
from model.models import Movimiento


class PrestamoView(ft.Column):
    def __init__(self, session: Session, page: ft.Page):
        super().__init__()
        self.session = session
        self.page = page
        self.controller = PrestamoController(session)
        
        # Tabla de solicitudes pendientes
        self.table_solicitudes = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Material")),
                ft.DataColumn(ft.Text("Código Copia")),
                ft.DataColumn(ft.Text("Usuario")),
                ft.DataColumn(ft.Text("Fecha Solicitud")),
                ft.DataColumn(ft.Text("Fecha Devolución")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )
        
        # Tabla de préstamos activos
        self.table_prestamos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Préstamo")),
                ft.DataColumn(ft.Text("Material")),
                ft.DataColumn(ft.Text("Código Copia")),
                ft.DataColumn(ft.Text("Usuario")),
                ft.DataColumn(ft.Text("Fecha Préstamo")),
                ft.DataColumn(ft.Text("Fecha Devolución")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Multa")),
            ],
            rows=[],
        )
        
        self.controls = [
            ft.Text("Gestión de Préstamos", size=24, weight="bold"),
            ft.Divider(),
            
            ft.Text("Solicitudes Pendientes de Aprobación", size=18, weight="bold"),
            ft.Container(
                content=ft.Column([self.table_solicitudes], scroll="auto"),
                height=300
            ),
            
            ft.Divider(),
            
            ft.Text("Préstamos Activos", size=18, weight="bold"),
            ft.Container(
                content=ft.Column([self.table_prestamos], scroll="auto"),
                expand=True
            )
        ]
        
        self.load_solicitudes()
        self.load_prestamos()
    
    def load_solicitudes(self):
        """Carga las solicitudes pendientes (movimientos con estado reservado)"""
        self.table_solicitudes.rows.clear()
        
        movimientos = self.controller.get_movimientos_pendientes()
        
        for mov in movimientos:
            # Obtener información del material a través de la copia
            material_titulo = "N/A"
            codigo_copia = "N/A"
            estado_nombre = "N/A"
            usuario_nombre = "N/A"
            
            if mov.copia_rel:
                codigo_copia = mov.copia_rel.codigo_copia
                if mov.copia_rel.material:
                    material_titulo = mov.copia_rel.material.titulo
            
            if mov.estado:
                estado_nombre = mov.estado.nombre
            
            if mov.usuario:
                usuario_nombre = mov.usuario.nombre
            
            self.table_solicitudes.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(mov.id_movimiento))),
                        ft.DataCell(ft.Text(material_titulo)),
                        ft.DataCell(ft.Text(codigo_copia)),
                        ft.DataCell(ft.Text(usuario_nombre)),
                        ft.DataCell(ft.Text(str(mov.fecha_solicitud.strftime("%Y-%m-%d %H:%M") if mov.fecha_solicitud else "N/A"))),
                        ft.DataCell(ft.Text(str(mov.fecha_devolucion))),
                        ft.DataCell(ft.Text(estado_nombre)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    icon_color="green",
                                    tooltip="Aprobar préstamo",
                                    on_click=lambda e, m=mov: self.aprobar_prestamo(m)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CANCEL,
                                    icon_color="red",
                                    tooltip="Rechazar solicitud",
                                    on_click=lambda e, m=mov: self.rechazar_solicitud(m)
                                ),
                            ])
                        ),
                    ]
                )
            )
        
        self.page.update()
    
    def load_prestamos(self):
        """Carga los préstamos activos"""
        self.table_prestamos.rows.clear()
        
        prestamos = self.controller.get_prestamos_activos()
        
        for prestamo in prestamos:
            material_titulo = "N/A"
            codigo_copia = "N/A"
            usuario_nombre = "N/A"
            
            if prestamo.copia and prestamo.copia.material:
                material_titulo = prestamo.copia.material.titulo
                codigo_copia = prestamo.copia.codigo_copia
            
            if prestamo.usuario:
                usuario_nombre = prestamo.usuario.nombre
            
            self.table_prestamos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(prestamo.id_prestamo))),
                        ft.DataCell(ft.Text(material_titulo)),
                        ft.DataCell(ft.Text(codigo_copia)),
                        ft.DataCell(ft.Text(usuario_nombre)),
                        ft.DataCell(ft.Text(str(prestamo.fecha_prestamo))),
                        ft.DataCell(ft.Text(str(prestamo.fecha_devolucion_prevista))),
                        ft.DataCell(ft.Text(prestamo.estado)),
                        ft.DataCell(ft.Text(f"${prestamo.multa or 0}")),
                    ]
                )
            )
        
        self.page.update()
    
    def aprobar_prestamo(self, movimiento: Movimiento):
        """Aprueba un préstamo, cambia el estado y crea el registro en Prestamo"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Aprobación"),
            content=ft.Text(f"¿Desea aprobar este préstamo?\n\nMaterial: {movimiento.copia_rel.material.titulo if movimiento.copia_rel and movimiento.copia_rel.material else 'N/A'}"),
            actions=[
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=lambda _: self.confirmar_aprobacion(dialog, movimiento)
                ),
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.close_dialog(dialog)
                )
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)
    
    def confirmar_aprobacion(self, dialog, movimiento: Movimiento):
        try:
            self.controller.aprobar_prestamo(movimiento.id_movimiento)
            
            dialog.open = False
            self.show_dialog_message("Préstamo Aprobado", "El préstamo ha sido aprobado correctamente.")
            
            # Recargar las tablas
            self.load_solicitudes()
            self.load_prestamos()
            
        except Exception as ex:
            self.show_dialog_message("Error al Aprobar Préstamo", f"Error al aprobar el préstamo: {str(ex)}", error=True)
        
        self.page.update()
    
    def rechazar_solicitud(self, movimiento: Movimiento):
        """Rechaza una solicitud de préstamo"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Rechazo"),
            content=ft.Text(f"¿Desea rechazar esta solicitud?\n\nMaterial: {movimiento.copia_rel.material.titulo if movimiento.copia_rel and movimiento.copia_rel.material else 'N/A'}"),
            actions=[
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=lambda _: self.confirmar_rechazo(dialog, movimiento)
                ),
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.close_dialog(dialog)
                )
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)
    
    def confirmar_rechazo(self, dialog, movimiento: Movimiento):
        try:
            self.controller.rechazar_solicitud(movimiento.id_movimiento)
            
            dialog.open = False
            self.show_dialog_message("Solicitud Rechazada", "La solicitud ha sido rechazada correctamente.", error=True)
            
            # Recargar las tablas
            self.load_solicitudes()
            self.load_prestamos()
            
        except Exception as ex:
            self.show_dialog_message("Error al Rechazar Solicitud", f"Error al rechazar la solicitud: {str(ex)}", error=True)
        
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_message(self, message, error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED if error else ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()

       
    def show_dialog_message(self, title, message, error=False):
        """Muestra un diálogo modal con un mensaje"""
        dialog = ft.AlertDialog(
            title=ft.Text(title, color=ft.Colors.RED if error else ft.Colors.GREEN),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)

