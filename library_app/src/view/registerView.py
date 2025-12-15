import flet as ft
import re


class RegisterView(ft.View):
    def __init__(self, page, controller, on_register_success, on_back):
        super().__init__(route="/register")

        self.page = page
        self.controller = controller
        self.on_register_success = on_register_success
        self.on_back = on_back

        roles = self.controller.get_roles()

        role_items = [ft.dropdown.Option(r.nombre) for r in roles]

        self.username = ft.TextField(
            label="Nuevo usuario",
            width=300,
            border=ft.InputBorder.UNDERLINE,
        )

        self.password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            border=ft.InputBorder.UNDERLINE,
        )

        self.email = ft.TextField(
            label="Correo",
            width=300,
            border=ft.InputBorder.UNDERLINE,
        )

        self.user_type = ft.Dropdown(
            label="Seleccione el rol",
            width=300,
            options=role_items,
        )

        create_btn = ft.ElevatedButton("Crear usuario", on_click=self.register)
        back_btn = ft.TextButton("Volver", on_click=lambda _: self.on_back())

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [
                                ft.Text("Registro de usuario", size=22, weight="bold"),
                                self.username,
                                self.password,
                                self.email,
                                self.user_type,
                                create_btn,
                                back_btn,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        )
                    ],
                ),
            )
        ]

    # ---------------------------
    # Validaciones
    # ---------------------------
    def valid_email(self, email: str) -> bool:
        return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None

    def valid_password(self, password: str) -> bool:
        
        
        return len(password) >= 6

    # ---------------------------
    # Registro
    # ---------------------------
    def register(self, _):
        user = self.username.value.strip()
        pwd = self.password.value
        email = self.email.value.strip()
        user_type = self.user_type.value

        if not user or not email or not pwd or not user_type:
            self.show_dialog_message(
                "Error",
                "Todos los campos son obligatorios.",
                error=True
            )
            return

        if self.controller.username_exists(user):
            self.show_dialog_message(
                "Usuario existente",
                "El nombre de usuario ya está registrado.",
                error=True
            )
            return
        
        if not self.valid_email(email):
            self.show_dialog_message(
                "Correo inválido",
                "Ingrese un correo válido (usuario@correo.com).",
                error=True
            )
            return

        if not self.valid_password(pwd):
            self.show_dialog_message(
                "Contraseña inválida",
                "La contraseña debe tener al menos 6 caracteres.",
                error=True
            )
            return

        ok = self.controller.register(user, email, pwd, user_type)

        if ok:
            self.show_message("Usuario registrado correctamente.")
            self.on_register_success()
        else:
            self.show_dialog_message(
                "Error",
                "No se pudo registrar el usuario. Puede que ya exista.",
                error=True
            )

    # ---------------------------
    # Mensajes
    # ---------------------------
    def show_message(self, message, error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED if error else ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_dialog_message(self, title, message, error=False):
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
        
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
