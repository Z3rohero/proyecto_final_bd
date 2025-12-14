import flet as ft

class RegisterView(ft.View):
    def __init__(self, page, controller, on_register_success, on_back):
        super().__init__(route="/register")
        
        self.page = page
        self.controller = controller
        self.on_register_success = on_register_success
        self.on_back = on_back

        roles = self.controller.get_roles() 

        role_items = [
            ft.dropdown.Option(r.nombre) for r in roles
        ]

        self.username = ft.TextField(
            label="Nuevo usuario", 
            width=300,
            border=ft.InputBorder.UNDERLINE,

            )
        self.password = ft.TextField(
            label="Contraseña", 
            border=ft.InputBorder.UNDERLINE,
            password=True, width=300,
            can_reveal_password=True,
            )
        self.email = ft.TextField(
                        label="Correo", 
                        border=ft.InputBorder.UNDERLINE,
                        width=300)
      
        self.user_type = ft.Dropdown(
            label="Seleccione el rol",
            width=300,
            options=role_items,
        )

        # Botones
        create_btn = ft.ElevatedButton("Crear usuario", on_click=self.register)
        back_btn = ft.TextButton("Volver", on_click=lambda _: self.on_back())

        # Layout
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
    # Lógica de registro
    # ---------------------------
    def register(self, _):
        user = self.username.value
        pwd = self.password.value
        email = self.email.value
        user_type = self.user_type.value

        ok = self.controller.register(user, email, pwd, user_type)

        if ok:
            self.page.snack_bar = ft.SnackBar(ft.Text("Usuario registrado correctamente."))
            self.page.snack_bar.open = True
            self.page.update()
            self.on_register_success()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Error: El usuario ya existe."),
                bgcolor="red"
            )
            self.page.snack_bar.open = True
            self.page.update()

