import flet as ft
from sqlalchemy.orm import Session
from controllers.reservaController import ReservaController
from model.models import Reserva


class ReservaView(ft.Column):
    def __init__(self, session: Session, page: ft.Page):
        super().__init__()
        self.session = session
        self.page = page
        self.controller = ReservaController(session)
        
        # Tabla de reservas activas
        self.table_activas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Material")),
                ft.DataColumn(ft.Text("Código Copia")),
                ft.DataColumn(ft.Text("Usuario")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Fecha Reserva")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )
        
        # Tabla de todas las reservas
        self.table_todas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Material")),
                ft.DataColumn(ft.Text("Código Copia")),
                ft.DataColumn(ft.Text("Usuario")),
                ft.DataColumn(ft.Text("Fecha Reserva")),
                ft.DataColumn(ft.Text("Estado")),
            ],
            rows=[],
        )
        
        self.controls = [
            ft.Text("Gestión de Reservas", size=24, weight="bold"),
            ft.Divider(),
            
            ft.Text("Reservas Activas", size=18, weight="bold"),
            ft.Container(
                content=ft.Column([self.table_activas], scroll="auto"),
                height=300
            ),
            
            ft.Divider(),
            
            ft.Text("Historial de Reservas", size=18, weight="bold"),
            ft.Container(
                content=ft.Column([self.table_todas], scroll="auto"),
                expand=True
            )
        ]
        
        self.load_reservas_activas()
        self.load_todas_reservas()
    
    def load_reservas_activas(self):
        """Carga las reservas activas"""
        self.table_activas.rows.clear()
        
        reservas = self.controller.get_reservas_activas()
        
        for reserva in reservas:
            material_titulo = "N/A"
            codigo_copia = "N/A"
            usuario_nombre = "N/A"
            usuario_email = "N/A"
            
            if reserva.copia:
                codigo_copia = reserva.copia.codigo_copia
                if reserva.copia.material:
                    material_titulo = reserva.copia.material.titulo
            
            if reserva.usuario:
                usuario_nombre = reserva.usuario.nombre
                usuario_email = reserva.usuario.correo or "N/A"
            
            self.table_activas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(reserva.id_reserva))),
                        ft.DataCell(ft.Text(material_titulo, max_lines=2)),
                        ft.DataCell(ft.Text(codigo_copia)),
                        ft.DataCell(ft.Text(usuario_nombre)),
                        ft.DataCell(ft.Text(usuario_email)),
                        ft.DataCell(ft.Text(str(reserva.fecha_reserva.strftime("%Y-%m-%d %H:%M") if reserva.fecha_reserva else "N/A"))),
                        ft.DataCell(ft.Text(reserva.estado)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    icon_color="green",
                                    tooltip="Completar reserva",
                                    on_click=lambda e, r=reserva: self.completar_reserva(r)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CANCEL,
                                    icon_color="red",
                                    tooltip="Cancelar reserva",
                                    on_click=lambda e, r=reserva: self.cancelar_reserva(r)
                                ),
                            ])
                        ),
                    ]
                )
            )
        
        self.page.update()
    
    def load_todas_reservas(self):
        """Carga todas las reservas"""
        self.table_todas.rows.clear()
        
        reservas = self.controller.get_all_reservas()
        
        for reserva in reservas:
            material_titulo = "N/A"
            codigo_copia = "N/A"
            usuario_nombre = "N/A"
            
            if reserva.copia:
                codigo_copia = reserva.copia.codigo_copia
                if reserva.copia.material:
                    material_titulo = reserva.copia.material.titulo
            
            if reserva.usuario:
                usuario_nombre = reserva.usuario.nombre
            
            self.table_todas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(reserva.id_reserva))),
                        ft.DataCell(ft.Text(material_titulo, max_lines=2)),
                        ft.DataCell(ft.Text(codigo_copia)),
                        ft.DataCell(ft.Text(usuario_nombre)),
                        ft.DataCell(ft.Text(str(reserva.fecha_reserva.strftime("%Y-%m-%d %H:%M") if reserva.fecha_reserva else "N/A"))),
                        ft.DataCell(ft.Text(reserva.estado)),
                    ]
                )
            )
        
        self.page.update()
    
    def completar_reserva(self, reserva: Reserva):
        """Completa una reserva"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Completar Reserva"),
            content=ft.Text(
                f"¿El usuario {reserva.usuario.nombre if reserva.usuario else 'N/A'} "
                f"ha recogido el material?\n\n"
                f"Material: {reserva.copia.material.titulo if reserva.copia and reserva.copia.material else 'N/A'}"
            ),
            actions=[
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=lambda _: self.confirmar_completar(dialog, reserva)
                ),
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.close_dialog(dialog)
                )
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def confirmar_completar(self, dialog, reserva: Reserva):
        try:
            self.controller.completar_reserva(reserva.id_reserva)
            
            dialog.open = False
            self.show_message("Reserva completada exitosamente")
            
            # Recargar las tablas
            self.load_reservas_activas()
            self.load_todas_reservas()
            
        except Exception as ex:
            self.show_message(f"Error al completar reserva: {str(ex)}", error=True)
        
        self.page.update()
    
    def cancelar_reserva(self, reserva: Reserva):
        """Cancela una reserva"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Cancelación"),
            content=ft.Text(
                f"¿Desea cancelar esta reserva?\n\n"
                f"Usuario: {reserva.usuario.nombre if reserva.usuario else 'N/A'}\n"
                f"Material: {reserva.copia.material.titulo if reserva.copia and reserva.copia.material else 'N/A'}"
            ),
            actions=[
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=lambda _: self.confirmar_cancelar(dialog, reserva)
                ),
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.close_dialog(dialog)
                )
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def confirmar_cancelar(self, dialog, reserva: Reserva):
        try:
            self.controller.cancelar_reserva(reserva.id_reserva)
            
            dialog.open = False
            self.show_message("Reserva cancelada")
            
            # Recargar las tablas
            self.load_reservas_activas()
            self.load_todas_reservas()
            
        except Exception as ex:
            self.show_message(f"Error al cancelar reserva: {str(ex)}", error=True)
        
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
