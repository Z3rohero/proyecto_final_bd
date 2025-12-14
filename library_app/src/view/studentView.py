import flet as ft
from view.catalogView import CatalogView
from view.myLoansView import MyLoansView
from view.myReservationsView import MyReservationsView
from sqlalchemy.orm import Session



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

