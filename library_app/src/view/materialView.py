import flet as ft
from sqlalchemy.orm import Session
from model.models import Material, Autor, Idioma
from controllers.materialController import MaterialController


class MaterialView(ft.Column):
    def __init__(self, session: Session, page: ft.Page):
        super().__init__()
        self.session = session
        self.page = page
        self.controller = MaterialController(session)

        # ---- Controles UI ----
        self.search_field = ft.TextField(
            hint_text="Buscar por título...",
            on_change=self.search_materials,
            expand=True
        )

        self.add_btn = ft.ElevatedButton(
            "Nuevo Material",
            icon=ft.Icons.ADD,
            on_click=self.open_create_modal
        )

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("Idioma")),
                ft.DataColumn(ft.Text("Año")),
                ft.DataColumn(ft.Text("Autores")),
                ft.DataColumn(ft.Text("ISBN")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            expand=True
        )

        self.controls = [
            ft.Row([self.search_field, self.add_btn]),
            ft.Container(self.table, expand=True)
        ]

        self.load_materials()

    # --------------------------------------------------------
    #                  CARGAR MATERIALES
    # --------------------------------------------------------
    def load_materials(self):
        materiales = self.controller.get_all_materials()

        self.table.rows = []
        for m in materiales:
            autores = self.controller.get_material_authors(m)
            
            # Obtener idioma si existe
            idiomas = self.controller.get_all_idiomas()
            idioma_nombre = ""
            if m.id_idioma:
                idioma = next((i for i in idiomas if i.id_idioma == m.id_idioma), None)
                idioma_nombre = idioma.nombre if idioma else ""

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(m.id_material))),
                        ft.DataCell(ft.Text(m.titulo)),
                        ft.DataCell(ft.Text(idioma_nombre)),
                        ft.DataCell(ft.Text(str(m.año_publicacion or ""))),
                        ft.DataCell(ft.Text(autores)),
                        ft.DataCell(ft.Text(m.isbn or "")),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                tooltip="Ver detalles",
                                on_click=lambda e, mat=m: self.open_detail_modal(mat)
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    # --------------------------------------------------------
    #                  BUSCAR MATERIALES
    # --------------------------------------------------------
    def search_materials(self, e):
        text = self.search_field.value

        materiales = self.controller.search_materials(text)

        self.table.rows = []
        for m in materiales:
            autores = self.controller.get_material_authors(m)
            
            # Obtener idioma si existe
            idiomas = self.controller.get_all_idiomas()
            idioma_nombre = ""
            if m.id_idioma:
                idioma = next((i for i in idiomas if i.id_idioma == m.id_idioma), None)
                idioma_nombre = idioma.nombre if idioma else ""
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(m.id_material))),
                        ft.DataCell(ft.Text(m.titulo)),
                        ft.DataCell(ft.Text(idioma_nombre)),
                        ft.DataCell(ft.Text(str(m.año_publicacion or ""))),
                        ft.DataCell(ft.Text(autores)),
                        ft.DataCell(ft.Text(m.isbn or "")),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                tooltip="Ver detalles",
                                on_click=lambda e, mat=m: self.open_detail_modal(mat)
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    # --------------------------------------------------------
    #              MODAL PARA DETALLE + EDITAR + BORRAR
    # --------------------------------------------------------
    def open_detail_modal(self, material):
        autores = self.controller.get_material_authors(material)
        
        # Obtener idioma si existe
        idiomas = self.controller.get_all_idiomas()
        idioma_nombre = "Desconocido"
        if material.id_idioma:
            idioma = next((i for i in idiomas if i.id_idioma == material.id_idioma), None)
            idioma_nombre = idioma.nombre if idioma else "Desconocido"

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Detalles del material"),
            content=ft.Column(
                [
                    ft.Text(f"Título: {material.titulo}"),
                    ft.Text(f"Idioma: {idioma_nombre}"),
                    ft.Text(f"Año: {material.año_publicacion}"),
                    ft.Text(f"Descripción: {material.descripcion}"),
                    ft.Text(f"Autores: {autores}")
                ],
                scroll="auto",
            ),
            actions=[
                ft.TextButton("Editar", on_click=lambda _: self.edit_material(material, dialog)),
                ft.TextButton("Eliminar", on_click=lambda _: self.delete_material(material, dialog)),
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
    #                    ELIMINAR MATERIAL
    # --------------------------------------------------------
    def delete_material(self, material, dialog):
        self.controller.delete_material(material.id_material)
        dialog.open = False
        self.load_materials()

    # --------------------------------------------------------
    #                    EDITAR MATERIAL
    # --------------------------------------------------------
    def edit_material(self, material, dialog):
        dialog.open = False

        titulo = ft.TextField(value=material.titulo)
        anio = ft.TextField(value=str(material.año_publicacion or ""))
        descripcion = ft.TextField(value=material.descripcion or "", multiline=True)

        save_btn = ft.ElevatedButton("Guardar cambios")

        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar material"),
            content=ft.Column(
                [
                    titulo,
                    descripcion,
                    anio
                ],
                scroll="auto"
            ),
            actions=[
                save_btn,
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(edit_dialog))
            ]
        )

        def save_changes(e):
            año = int(anio.value) if anio.value.isdigit() else None
            
            self.controller.update_material(
                material.id_material,
                titulo=titulo.value,
                descripcion=descripcion.value,
                año_publicacion=año
            )
            
            edit_dialog.open = False
            self.load_materials()

        save_btn.on_click = save_changes

        self.page.dialog = edit_dialog
        edit_dialog.open = True
        self.page.open(edit_dialog)

    # --------------------------------------------------------
    #             MODAL PARA CREAR NUEVO MATERIAL
    # --------------------------------------------------------
    def open_create_modal(self, e):

        autores = self.session.query(Autor).order_by(Autor.nombre).all()
        idiomas = self.session.query(Idioma).order_by(Idioma.nombre).all()
        autor_dropdown = ft.Dropdown(
            label="Autor",
            width=300,
            options=[
                ft.dropdown.Option(str(a.id_autor), a.nombre)
                for a in autores
            ],
        )
        idioma_dropdown = ft.Dropdown(
            label="Idioma",
            width=300,
            options=[
                ft.dropdown.Option(str(i.id_idioma), i.nombre)
                for i in idiomas
            ],
        )


        titulo = ft.TextField(label="Título")
        descripcion = ft.TextField(label="Descripción", multiline=True)
        anio = ft.TextField(label="Año publicación")
        idioma = idioma_dropdown
        isbn = ft.TextField(label="ISBN")


        create_btn = ft.ElevatedButton("Crear")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Material"),
            content=ft.Column([titulo, descripcion, anio, idioma
            , isbn, autor_dropdown
            ], scroll="auto"),
            actions=[
                create_btn,
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)

        def create_material(e):
            año = int(anio.value) if anio.value.isdigit() else None
            id_idioma = int(idioma.value) if idioma.value else None
            
            from model.models import MaterialAutor
            
            nuevo = self.controller.create_material(
                titulo=titulo.value,
                descripcion=descripcion.value,
                año_publicacion=año,
                id_idioma=id_idioma,
                tipo_material="Libro",
                isbn=isbn.value
            )

            if autor_dropdown.value:
                relacion = MaterialAutor(
                    id_material=nuevo.id_material,
                    id_autor=int(autor_dropdown.value),
                )
                self.session.add(relacion)
                self.session.commit()

            dialog.open = False
            self.load_materials()
            self.page.update()

        create_btn.on_click = create_material

       
