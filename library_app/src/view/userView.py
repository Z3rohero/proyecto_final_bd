import flet as ft
from sqlalchemy.orm import Session
from model.models import Material, Autor, Idioma
from controllers.userControllers import UserController


class UserView(ft.Column):
    def __init__(self, session: Session, page: ft.Page):
        super().__init__()
        self.session = session
        self.page = page
        self.controller = UserController(session)

        # ---- Controles UI ----
        self.search_field = ft.TextField(
            hint_text="Buscar por ID...",
            on_change=self.search_users,
            expand=True
        )

        self.add_btn = ft.ElevatedButton(
            "Nuevo Usuario",
            icon=ft.Icons.ADD,
            on_click=self.open_create_modal
        )


        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Correo")),
                ft.DataColumn(ft.Text("Acciones")),
                
            ],
            rows=[],
            expand=True
        )

        self.controls = [
            ft.Row([self.search_field]),
            ft.Container(self.table, expand=True)
        ]

        self.load_users()

    # ----------------------------------------------------------
    #                  CARGAR USUARIOS
    # ------------------------------------------------------
    def load_users(self):
        usuarios = self.controller.get_all_user()

        self.table.rows = []
        for u in usuarios:
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(u.id_usuario))),
                        ft.DataCell(ft.Text(u.nombre)),
                        ft.DataCell(ft.Text(u.correo)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                tooltip="Ver detalles",
                                on_click=lambda e, usr=u: self.open_detail_modal(usr)
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    # --------------------------------------------------------
    #                  BUSCAR USUARIOS
    # --------------------------------------------------------
    def search_users(self, e):
        text = self.search_field.value
        usuarios = self.controller.search_user(text)

        self.table.rows = []
        for u in usuarios:
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(u.id_usuario))),
                        ft.DataCell(ft.Text(u.nombre)),
                        ft.DataCell(ft.Text(u.correo)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                tooltip="Ver detalles",
                                on_click=lambda e, usr=u: self.open_detail_modal(usr)
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    # --------------------------------------------------------
    #              MODAL PARA DETALLE + EDITAR + BORRAR
    # --------------------------------------------------------
    def open_detail_modal(self, usuario):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Detalles del usuario"),
            content=ft.Column(
                [
                    ft.Text(f"Nombre: {usuario.nombre}"),
                    ft.Text(f"Correo: {usuario.correo}"),
                ],
                scroll="auto",
            ),
            actions=[
                ft.TextButton("Editar", on_click=lambda _: self.edit_user(usuario, dialog)),
                ft.TextButton("Eliminar", on_click=lambda _: self.delete_user(usuario, dialog)),
                ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog(dialog)),
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    # --------------------------------------------------------
    #                    ELIMINAR USUARIO
    # --------------------------------------------------------
    def delete_user(self, usuario, dialog):
        self.controller.delete_user(usuario.id_usuario)
        dialog.open = False
        self.load_users()

    # --------------------------------------------------------
    #                    EDITAR USUARIO
    # --------------------------------------------------------
    def edit_user(self, usuario, dialog):
        dialog.open = False

        nombre = ft.TextField(value=usuario.nombre)
        correo = ft.TextField(value=usuario.correo)

        save_btn = ft.ElevatedButton("Guardar cambios")

        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar usuario"),
            content=ft.Column([nombre, correo]),
            actions=[
                save_btn,
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(edit_dialog))
            ]
        )

        def save_changes(e):
            self.controller.update_user(
                usuario.id_usuario,
                nombre=nombre.value,
                correo=correo.value
            )
            edit_dialog.open = False
            self.load_users()

        save_btn.on_click = save_changes

        self.page.dialog = edit_dialog
        edit_dialog.open = True
        self.page.open(edit_dialog)

    # --------------------------------------------------------
    #             MODAL PARA CREAR NUEVO USUARIO
    # --------------------------------------------------------
    def open_create_modal(self, e):
        nombre = ft.TextField(label="Nombre")
        correo = ft.TextField(label="Correo")
        password = ft.TextField(label="Contraseña", password=True)

        create_btn = ft.ElevatedButton("Crear")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Usuario"),
            content=ft.Column([nombre, correo, password], scroll="auto"),
            actions=[
                create_btn,
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)

        def create_user(e):
            self.controller.create_user(
                nombre=nombre.value,
                correo=correo.value,
                password=password.value
            )
            dialog.open = False
            self.load_users()
            self.page.update()

        create_btn.on_click = create_user

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
            