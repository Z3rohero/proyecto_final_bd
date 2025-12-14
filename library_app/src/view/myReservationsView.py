import flet as ft
from sqlalchemy.orm import Session
from model.models import Reserva
from controllers.studentController import StudentController


class MyReservationsView(ft.Column):
    def __init__(self, session: Session, page: ft.Page, user):
        super().__init__()
        self.session = session
        self.page = page
        self.user = user
        self.controller = StudentController(session)
        
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Material")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Fecha Reserva")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )
        
        self.controls = [
            ft.Text("Mis Reservas", size=20, weight="bold"),
            ft.Container(
                content=ft.Column([self.table], scroll="auto"),
                expand=True
            )
        ]
        
        self.load_reservations()
    
    def load_reservations(self):
        """Carga las reservas del usuario"""
        self.table.rows.clear()
        
        reservas = self.controller.get_user_reservations(self.user.id_usuario)
        
        for reserva in reservas:
            material_titulo = reserva.copia.material.titulo if reserva.copia and reserva.copia.material else "N/A"
            
            acciones = ft.Row([])
            
            if reserva.estado == "activa":
                acciones.controls.append(
                    ft.TextButton(
                        "Cancelar",
                        icon=ft.Icons.CANCEL,
                        on_click=lambda e, r=reserva: self.cancel_reservation(r)
                    )
                )
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(material_titulo)),
                        ft.DataCell(ft.Text(reserva.copia.codigo_copia if reserva.copia else "N/A")),
                        ft.DataCell(ft.Text(str(reserva.fecha_reserva))),
                        ft.DataCell(ft.Text(reserva.estado)),
                        ft.DataCell(acciones),
                    ]
                )
            )
        
        self.page.update()
    
    def cancel_reservation(self, reserva: Reserva):
        """Cancela una reserva"""
        try:
            self.controller.cancel_reservation(reserva)
            self.show_message("Reserva cancelada")
            self.load_reservations()
            
        except Exception as ex:
            self.show_message(f"Error al cancelar: {str(ex)}", error=True)
    
    def show_message(self, message, error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED if error else ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
