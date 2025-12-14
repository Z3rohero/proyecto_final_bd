import flet as ft

class LoginView(ft.View):
    def __init__(self, page, controller, on_login_success, on_open_register):
        super().__init__(route="/login")

        self.page = page
        self.controller = controller
        self.on_login_success = on_login_success
        self.on_open_register = on_open_register

        # Campos con validación
        self.username = ft.TextField(
            label="Usuario",
            width=300,
            on_change=self.validate_form,
            border=ft.InputBorder.UNDERLINE,

        )

        self.password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            border=ft.InputBorder.UNDERLINE,
            on_change=self.validate_form
        )

        self.login_btn = ft.ElevatedButton(
            "Ingresar",
            on_click=self.login,
            width=300,
            height=40,
            disabled=True
        )

        register_btn = ft.TextButton(
            "Registrar usuario",
            on_click=lambda _: self.on_open_register()
        )

        # Layout
                # Layout centrado real
        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [
                                ft.Text("Inicio de sesión", size=22, weight="bold"),
                                self.username,
                                self.password,
                                self.login_btn,
                                register_btn
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        )
                    ],
                ),
            )
        ]



    def validate_form(self, _):
        user_ok = len(self.username.value.strip()) > 0
        pwd_ok = len(self.password.value) > 0

        self.login_btn.disabled = not (user_ok and pwd_ok)
        self.page.update()

    # ---------------------------
    # LOGIN
    # ---------------------------
    def login(self, _):
        user = self.username.value.strip()
        pwd = self.password.value.strip()

        ok = self.controller.login(user, pwd)

        if ok:
            self.page.snack.content = ft.Text("Inicio de sesión correcto.")
            self.page.snack.bgcolor = "green"
            self.page.snack.open = True
            self.page.update()
            self.on_login_success()

        else:
            self.page.snack.content = ft.Text("Usuario o contraseña incorrectos.")
            self.page.snack.bgcolor = "red"
            self.page.snack.open = True
            self.page.update()
