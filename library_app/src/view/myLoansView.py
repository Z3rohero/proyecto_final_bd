import flet as ft
from sqlalchemy.orm import Session
from model.models import Prestamo
from controllers.studentController import StudentController


class MyLoansView(ft.Column):
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
                ft.DataColumn(ft.Text("Fecha Préstamo")),
                ft.DataColumn(ft.Text("Fecha Devolución")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Multa")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )
        
        self.controls = [
            ft.Text("Mis Préstamos", size=20, weight="bold"),
            ft.Container(
                content=ft.Column([self.table], scroll="auto"),
                expand=True
            )
        ]
        
        self.load_loans()
    
    def load_loans(self):
        """Carga los préstamos del usuario"""
        self.table.rows.clear()
        
        prestamos = self.controller.get_user_loans(self.user.id_usuario)
        
        for prestamo in prestamos:
            material_titulo = prestamo.copia.material.titulo if prestamo.copia and prestamo.copia.material else "N/A"
            
            acciones = ft.Row([])
            
            # Solo mostrar botón devolver si está activo
            if prestamo.estado == "activo":
                acciones.controls.append(
                    ft.TextButton(
                        "Devolver",
                        icon=ft.Icons.ASSIGNMENT_RETURN,
                        on_click=lambda e, p=prestamo: self.return_loan(p)
                    )
                )
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(material_titulo)),
                        ft.DataCell(ft.Text(prestamo.copia.codigo_copia if prestamo.copia else "N/A")),
                        ft.DataCell(ft.Text(str(prestamo.fecha_prestamo))),
                        ft.DataCell(ft.Text(str(prestamo.fecha_devolucion_prevista))),
                        ft.DataCell(ft.Text(prestamo.estado)),
                        ft.DataCell(ft.Text(f"${prestamo.multa or 0}")),
                        ft.DataCell(acciones),
                    ]
                )
            )
        
        self.page.update()
    
    def return_loan(self, prestamo: Prestamo):
        """Devuelve un préstamo"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Devolución"),
            content=ft.Text(f"¿Desea devolver el material '{prestamo.copia.material.titulo}'?"),
            actions=[
                ft.ElevatedButton("Confirmar"),
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )
        
        def confirm_return(e):
            try:
                self.controller.return_loan(prestamo)
                
                dialog.open = False
                self.show_message("Material devuelto exitosamente")
                self.load_loans()
                
            except Exception as ex:
                self.show_message(f"Error al devolver: {str(ex)}", error=True)
        
        dialog.actions[0].on_click = confirm_return
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)
    
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
