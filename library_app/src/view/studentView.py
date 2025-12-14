import flet as ft
from sqlalchemy.orm import Session
from model.models import Copia, Material, Prestamo, Reserva, Estado
from datetime import date, timedelta
from controllers.studentController import StudentController


class StudentView(ft.View):
    def __init__(self, page: ft.Page, auth_controller, on_logout):
        super().__init__(route="/student")
        
        self.page = page
        self.auth = auth_controller
        self.session = auth_controller.session
        self.on_logout = on_logout
        
        self.controls = [
            ft.Row(
                [
                    ft.Text(
                        f"Panel de Usuario - {self.auth.current_user.nombre}",
                        size=22,
                        weight="bold"
                    ),
                    ft.ElevatedButton(
                        "Cerrar sesión",
                        color="white",
                        bgcolor="red",
                        on_click=self.logout
                    )
                ],
                alignment="spaceBetween"
            ),
            ft.Tabs(
                tabs=[
                    ft.Tab(text="Catálogo"),
                    ft.Tab(text="Mis Préstamos"),
                    ft.Tab(text="Mis Reservas"),
                ],
                selected_index=0,
                on_change=self.tab_change
            )
        ]
        
        self.content_area = ft.Container(expand=True)
        self.controls.append(self.content_area)
        
        # Cargar la primera pestaña por defecto
        self.load_catalog()
    
    def tab_change(self, e):
        index = e.control.selected_index
        
        if index == 0:
            self.load_catalog()
        elif index == 1:
            self.load_my_loans()
        elif index == 2:
            self.load_my_reservations()
        
        self.page.update()
    
    # ========================================
    # PESTAÑA: CATÁLOGO DE MATERIALES
    # ========================================
    def load_catalog(self):
        self.content_area.content = CatalogView(self.session, self.page, self.auth.current_user)
    
    # ========================================
    # PESTAÑA: MIS PRÉSTAMOS
    # ========================================
    def load_my_loans(self):
        self.content_area.content = MyLoansView(self.session, self.page, self.auth.current_user)
    
    # ========================================
    # PESTAÑA: MIS RESERVAS
    # ========================================
    def load_my_reservations(self):
        self.content_area.content = MyReservationsView(self.session, self.page, self.auth.current_user)
    
    def logout(self, e):
        self.auth.logout()
        self.on_logout()


# ========================================
# VISTA DEL CATÁLOGO
# ========================================
class CatalogView(ft.Column):
    def __init__(self, session: Session, page: ft.Page, user):
        super().__init__()
        self.session = session
        self.page = page
        self.user = user
        self.controller = StudentController(session)
        
        # Controles de búsqueda
        self.search_field = ft.TextField(
            hint_text="Buscar por título o autor...",
            on_change=self.search_materials,
            expand=True
        )
        
        # Tabla de resultados
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("Autor(es)")),
                ft.DataColumn(ft.Text("ISBN")),
                ft.DataColumn(ft.Text("Año")),
                ft.DataColumn(ft.Text("Disponibles")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )
        
        self.controls = [
            ft.Row([self.search_field]),
            ft.Container(
                content=ft.Column([self.table], scroll="auto"),
                expand=True
            )
        ]
        
        self.load_available_materials()
    
    def load_available_materials(self):
        """Carga todos los materiales que tienen al menos una copia disponible"""
        self.table.rows.clear()
        
        materiales_info = self.controller.get_available_materials()
        
        for item in materiales_info:
            material = item['material']
            copias_disponibles = item['copias_disponibles']
            autores = self.controller.get_material_authors(material)
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(material.titulo)),
                        ft.DataCell(ft.Text(autores or "N/A")),
                        ft.DataCell(ft.Text(material.isbn or "N/A")),
                        ft.DataCell(ft.Text(str(material.año_publicacion or "N/A"))),
                        ft.DataCell(ft.Text(str(copias_disponibles))),
                        ft.DataCell(
                            ft.TextButton(
                                "Solicitar",
                                icon=ft.Icons.ADD_CIRCLE,
                                on_click=lambda e, m=material: self.request_loan(m)
                            )
                        ),
                    ]
                )
            )
        
        self.page.update()
    
    def search_materials(self, e):
        """Busca materiales por título o autor"""
        text = self.search_field.value
        
        if not text:
            self.load_available_materials()
            return
        
        self.table.rows.clear()
        
        materiales_info = self.controller.search_available_materials(text)
        
        for item in materiales_info:
            material = item['material']
            copias_disponibles = item['copias_disponibles']
            autores = self.controller.get_material_authors(material)
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(material.titulo)),
                        ft.DataCell(ft.Text(autores or "N/A")),
                        ft.DataCell(ft.Text(material.isbn or "N/A")),
                        ft.DataCell(ft.Text(str(material.año_publicacion or "N/A"))),
                        ft.DataCell(ft.Text(str(copias_disponibles))),
                        ft.DataCell(
                            ft.TextButton(
                                "Solicitar",
                                icon=ft.Icons.ADD_CIRCLE,
                                on_click=lambda e, m=material: self.request_loan(m)
                            )
                        ),
                    ]
                )
            )
        
        self.page.update()
    
    def request_loan(self, material: Material):
        """Solicita un préstamo de una copia disponible del material"""
        
        # Buscar una copia disponible
        estado_disponible = self.session.query(Estado).filter_by(nombre="disponible").first()
        
        copia = self.session.query(Copia).filter_by(
            id_material=material.id_material,
            id_estado=estado_disponible.id_estado
        ).first()
        
        if not copia:
            self.show_message("No hay copias disponibles", error=True)
            return
        
        # Mostrar diálogo de confirmación
        dias_prestamo = ft.TextField(
            label="Días de préstamo",
            value="14",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Solicitar Préstamo"),
            content=ft.Column([
                ft.Text(f"Material: {material.titulo}"),
                ft.Text(f"Código de copia: {copia.codigo_copia}"),
                ft.Text(f"Ubicación: {copia.ubicacion or 'N/A'}"),
                ft.Divider(),
                dias_prestamo,
            ], tight=True),
            actions=[
                ft.ElevatedButton("Confirmar"),
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )
        
        def confirm_loan(e):
            try:
                dias = int(dias_prestamo.value)
                if dias <= 0:
                    self.show_message("Los días deben ser mayor a 0", error=True)
                    return
                
                # Usar el controlador para crear el préstamo
                self.controller.request_loan(
                    id_material=material.id_material,
                    id_usuario=self.user.id_usuario,
                    dias=dias
                )
                
                dialog.open = False
                self.show_message("Préstamo solicitado exitosamente")
                self.load_available_materials()
                
            except ValueError:
                self.show_message("Ingrese un número válido de días", error=True)
            except Exception as ex:
                self.show_message(f"Error al crear préstamo: {str(ex)}", error=True)
        
        dialog.actions[0].on_click = confirm_loan
        
        self.page.dialog = dialog
        dialog.open = True
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


# ========================================
# VISTA DE MIS PRÉSTAMOS
# ========================================
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


# ========================================
# VISTA DE MIS RESERVAS
# ========================================
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
