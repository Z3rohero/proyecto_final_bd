import flet as ft
from view.materialView import MaterialView
from view.copiaView import CopiaView
from view.prestamoView import PrestamoView
from view.userView import UserView
from view.reservaView import ReservaView

class LibrarianView(ft.View):
    def __init__(self, page, auth_controller, on_logout):
        super().__init__(route="/admin")

        self.page = page
        self.auth = auth_controller
        self.on_logout = on_logout

        self.controls = [
            ft.Row(
                [
                    ft.Text(
                        f"Panel Administrativo - {self.auth.current_user.nombre}",
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
                    ft.Tab(text="Usuarios"),
                    ft.Tab(text="Materiales"),
                    ft.Tab(text="Copias"),
                    ft.Tab(text="Préstamos"),
                    ft.Tab(text="Reservas"),
                    ft.Tab(text="Dashboard"),
                ],
                selected_index=0,
                on_change=self.tab_change
            )
        ]
        
        self.content_area = ft.Container(
            expand=True
        )
        self.controls.append(self.content_area)
        
        # Cargar la primera pestaña por defecto
        self.content_area.content = UserView(
            session=self.auth.session,
            page=self.page
        )
        
    
    # ---------------------------
    # Cambiar contenido segun tab
    # ---------------------------
    def tab_change(self, e):
        
        index = e.control.selected_index or 0
        
        
        if index == 0:
             self.content_area.content = UserView(
            session=self.auth.session,
                page=self.page
            )
        elif index == 1:
            self.content_area.content = MaterialView(
            session=self.auth.session,
                page=self.page
            )
        elif index == 2:
            self.content_area.content = CopiaView(
            session=self.auth.session,
                page=self.page
            )
        elif index == 3:
            self.content_area.content = PrestamoView(
                session=self.auth.session,
                page=self.page
            )
        elif index == 4:
            self.content_area.content = ReservaView(
                session=self.auth.session,
                page=self.page
            )


        self.page.update()

    def logout(self, e):
        self.auth.logout()
        self.on_logout()
