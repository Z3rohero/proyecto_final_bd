import flet as ft
from sqlalchemy.orm import Session
from model.models import Copia, Material, Estado
from controllers.studentController import StudentController


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
                ft.DataColumn(ft.Text("Prestadas")),
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
        """Carga todos los materiales que tienen copias disponibles o prestadas"""
        self.table.rows.clear()
        
        materiales_info = self.controller.get_all_materials_with_copies()
        
        for item in materiales_info:
            material = item['material']
            copias_disponibles = item['copias_disponibles']
            copias_prestadas = item['copias_prestadas']
            autores = self.controller.get_material_authors(material)
            
            # Crear botones de acción
            acciones = ft.Row([], spacing=5)
            
            # Botón solicitar si hay disponibles
            if copias_disponibles > 0:
                acciones.controls.append(
                    ft.TextButton(
                        "Solicitar",
                        icon=ft.Icons.ADD_CIRCLE,
                        on_click=lambda e, m=material: self.request_loan(m)
                    )
                )
            
            # Botón reservar si hay prestadas
            if copias_prestadas > 0:
                acciones.controls.append(
                    ft.TextButton(
                        "Reservar",
                        icon=ft.Icons.BOOKMARK_ADD,
                        on_click=lambda e, m=material: self.request_reservation(m)
                    )
                )
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(material.titulo)),
                        ft.DataCell(ft.Text(autores or "N/A")),
                        ft.DataCell(ft.Text(material.isbn or "N/A")),
                        ft.DataCell(ft.Text(str(material.año_publicacion or "N/A"))),
                        ft.DataCell(ft.Text(str(copias_disponibles))),
                        ft.DataCell(ft.Text(str(copias_prestadas))),
                        ft.DataCell(acciones),
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
        
        materiales_info = self.controller.search_materials_with_copies(text)
        
        for item in materiales_info:
            material = item['material']
            copias_disponibles = item['copias_disponibles']
            copias_prestadas = item['copias_prestadas']
            autores = self.controller.get_material_authors(material)
            
            # Crear botones de acción
            acciones = ft.Row([], spacing=5)
            
            # Botón solicitar si hay disponibles
            if copias_disponibles > 0:
                acciones.controls.append(
                    ft.TextButton(
                        "Solicitar",
                        icon=ft.Icons.ADD_CIRCLE,
                        on_click=lambda e, m=material: self.request_loan(m)
                    )
                )
            
            # Botón reservar si hay prestadas
            if copias_prestadas > 0:
                acciones.controls.append(
                    ft.TextButton(
                        "Reservar",
                        icon=ft.Icons.BOOKMARK_ADD,
                        on_click=lambda e, m=material: self.request_reservation(m)
                    )
                )
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(material.titulo)),
                        ft.DataCell(ft.Text(autores or "N/A")),
                        ft.DataCell(ft.Text(material.isbn or "N/A")),
                        ft.DataCell(ft.Text(str(material.año_publicacion or "N/A"))),
                        ft.DataCell(ft.Text(str(copias_disponibles))),
                        ft.DataCell(ft.Text(str(copias_prestadas))),
                        ft.DataCell(acciones),
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
            self.show_dialog_message("Error", "No hay copias disponibles", error=True)
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
                self.show_dialog_message("Error de validación", "Ingrese un número válido de días", error=True)
            except Exception as ex:
                self.show_dialog_message("Error", f"Error al crear préstamo: {str(ex)}", error=True)
        
        dialog.actions[0].on_click = confirm_loan
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)
    
    def request_reservation(self, material: Material):
        """Solicita una reserva de una copia prestada del material"""
        
        # Buscar una copia prestada
        estado_prestado = self.session.query(Estado).filter_by(nombre="prestado").first()
        
        copia = self.session.query(Copia).filter_by(
            id_material=material.id_material,
            id_estado=estado_prestado.id_estado
        ).first()
        
        if not copia:
            self.show_dialog_message("Error", "No hay copias prestadas para reservar", error=True)
            return
        
        # Mostrar diálogo de confirmación
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Reserva"),
            content=ft.Column([
                ft.Text(f"Material: {material.titulo}"),
                ft.Text(f"Código de copia: {copia.codigo_copia}"),
                ft.Text(f"Ubicación: {copia.ubicacion or 'N/A'}"),
                ft.Divider(),
                ft.Text("Esta copia está prestada. Se creará una reserva."),
            ], tight=True),
            actions=[
                ft.ElevatedButton("Confirmar"),
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )
        
        def confirm_reservation(e):
            try:
                # Usar el controlador para crear la reserva
                self.controller.create_reservation(
                    id_material=material.id_material,
                    id_usuario=self.user.id_usuario
                )
                
                dialog.open = False
                self.show_message("Reserva creada exitosamente")
                self.load_available_materials()
                
            except Exception as ex:
                self.show_dialog_message("Error", f"Error al crear reserva: {str(ex)}", error=True)
        
        dialog.actions[0].on_click = confirm_reservation
        
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
