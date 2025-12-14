import flet as ft
from dotenv import load_dotenv
from controllers.authControllers import AuthController
from view.loginView import LoginView
from view.registerView import RegisterView
from view.librarianView import LibrarianView
from view.studentView import StudentView
from sqlalchemy.orm import sessionmaker
from model.db import engine


def main(page: ft.Page):

    # Configuración de la ventana principal
    page.title = "Biblioteca App"
    page.window_width = 900
    page.window_height = 600
    page.horizontal_alignment = "center"
    page.scroll = "auto"
    page.snack = ft.SnackBar(
    content=ft.Container(
        padding=15,
        border_radius=20,
        bgcolor="white",
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
        ),
    ),
    open=False,
    margin=ft.Margin(0, 0, 0, 30), 
    )
    page.overlay.append(page.snack)

    # SQLAlchemy
    Session = sessionmaker(bind=engine)
    session = Session()

    auth_controller = AuthController(session)

    # ----------- Navegación -----------

    def go_to(view_name):
        page.views.clear()

        if view_name == "login":
            page.views.append(
                LoginView(
                    page,
                    auth_controller,
                    on_login_success,
                    on_open_register
                )
            )

        elif view_name == "register":
            page.views.append(
                RegisterView(
                    page,
                    auth_controller,
                    on_register_success,
                    on_back_to_login
                )
            )


        elif view_name == "admin":
            page.views.append(
                LibrarianView(
                    page,
                    auth_controller,
                    on_logout
                )
            )

        elif view_name == "home":
            page.views.append(
                StudentView(
                    page,
                    auth_controller,
                    on_logout
                )
            )

        page.update()

    # ----------- Callbacks -----------

   
    def on_login_success():
        #user = auth_controller.get_current_user()

        # Bibliotecario
        if auth_controller.user_has_role("bibliotecario"):
            go_to("admin")

        # Profesor o estudiante
        else:
            go_to("home")


    def on_logout():
        go_to("login")

    def on_register_success():
        page.snack_bar = ft.SnackBar(
            ft.Text("Registro exitoso. Ahora puedes iniciar sesión.")
        )
        page.snack_bar.open = True
        page.update()
        go_to("login")

    def on_open_register():
        go_to("register")

    def on_back_to_login():
        go_to("login")

    # ----------- Vista inicial -----------

    go_to("login")


if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.WEB_BROWSER,  
        host="0.0.0.0",       
        port=8550              
    )
