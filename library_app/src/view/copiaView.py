import flet as ft
from model.models import Copia, Material, Estado
from sqlalchemy.orm import Session
from controllers.copiaController import CopiaController

class CopiaView(ft.Column):

    def __init__(self, session: Session, page: ft.Page):
        super().__init__()
        self.session = session
        self.page = page
        self.controller = CopiaController(session)


         # ---- Controles UI ----
         
        self.search_field = ft.TextField(
            hint_text="Buscar por título...",
            #on_change=self.search_materials,
            expand=True
        )
        

        self.add_btn = ft.ElevatedButton(
            "Nuevo Material",
            icon=ft.Icons.ADD,
            on_click=self.open_create_dialog
        )

        # Tabla
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Material")),
                ft.DataColumn(ft.Text("ISBN")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Colección")),
                ft.DataColumn(ft.Text("Ubicación")),
                ft.DataColumn(ft.Text("Formato")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            expand=True

        )

        self.controls = [
            ft.Row([self.search_field, self.add_btn]),
            ft.Container(self.table, expand=True)
        ]

        self.load_data()

  

    # ----------------------------
    # Cargar tabla
    # ----------------------------
    def load_data(self):
        self.table.rows.clear()

        copias = self.controller.get_all_copias()

        for c in copias:
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(c.id_copia))),
                        ft.DataCell(ft.Text(c.codigo_copia)),
                        ft.DataCell(ft.Text(self.controller.get_copia_material_title(c))),
                        ft.DataCell(ft.Text(self.controller.get_copia_material_isbn(c))),
                        ft.DataCell(ft.Text(self.controller.get_copia_estado_nombre(c))),
                        ft.DataCell(ft.Text(c.coleccion or "")),
                        ft.DataCell(ft.Text(c.ubicacion or "")),
                        ft.DataCell(ft.Text(c.formato)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT, on_click=lambda _, cid=c.id_copia: self.open_edit_dialog(cid)),
                                ft.IconButton(ft.Icons.DELETE, on_click=lambda _, cop=c: self.delete_item(cop)),
                            ])
                        ),
                    ]
                )
            )

        self.page.update()

    # ----------------------------
    # Crear copia
    # ----------------------------
    def open_create_dialog(self, e):
        materiales = self.controller.get_all_materiales()
        estado_all = self.controller.get_all_estados()

        material_dd = ft.Dropdown(
            label="Material",
            options=[
                ft.dropdown.Option(str(m.id_material), f"{m.titulo} — {m.isbn}")
                for m in materiales
            ],
            width=300
        )

        codigo = ft.TextField(label="Código de copia")
        ubicacion = ft.TextField(label="Ubicación")
        coleccion = ft.TextField(label="Colección")

        estado = ft.Dropdown(
            label="Estado",
            width=300,
            options=[
                ft.dropdown.Option(str(e.id_estado), e.nombre)
                for e in estado_all
            ]
        )

        formato = ft.Dropdown(
            label="Formato",   
            width=300,
            options=[
                ft.dropdown.Option("fisico"),
                ft.dropdown.Option("digital"),
            ]
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Crear copia"),
            content=ft.Column([
                material_dd,
                codigo,
                ubicacion,
                coleccion,
                estado,
                formato,
            ]),
            actions=[
                ft.ElevatedButton("Guardar"),
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )

        def save(_):
            self.controller.create_copia(
                id_material=int(material_dd.value),
                codigo_copia=codigo.value,
                ubicacion=ubicacion.value,
                coleccion=coleccion.value,
                id_estado=int(estado.value),
                formato=formato.value
            )
            
            dialog.open = False
            self.load_data()
            self.page.update()
        
        dialog.actions[0].on_click = save
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)



    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    # ----------------------------
    # Editar copia
    # ----------------------------
    def open_edit_dialog(self, copia_id):
        copia = self.controller.get_copia_by_id(copia_id)
        if not copia:
            return

        materiales = self.controller.get_all_materiales()
        estado_all = self.controller.get_all_estados()

        material_dd = ft.Dropdown(
            label="Material",
            value=str(copia.id_material),
            options=[
                ft.dropdown.Option(str(m.id_material), f"{m.titulo} — {m.isbn}")
                for m in materiales
            ],
            width=300
        )

        codigo = ft.TextField(label="Código de copia", value=copia.codigo_copia)
        ubicacion = ft.TextField(label="Ubicación", value=copia.ubicacion or "")
        coleccion = ft.TextField(label="Colección", value=copia.coleccion or "")

        estado = ft.Dropdown(
            label="Estado",
            value=str(copia.id_estado),
            width=300,
            options=[
                ft.dropdown.Option(str(e.id_estado), e.nombre)
                for e in estado_all
            ]
        )

        formato = ft.Dropdown(
            label="Formato",
            value=copia.formato,
            width=300,
            options=[
                ft.dropdown.Option("fisico"),
                ft.dropdown.Option("digital"),
            ]
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Editar copia"),
            content=ft.Column([
                material_dd,
                codigo,
                ubicacion,
                coleccion,
                estado,
                formato,
            ]),
            actions=[
                ft.ElevatedButton("Guardar cambios"),
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog))
            ]
        )

        def save(_):
            self.controller.update_copia(
                copia_id=copia_id,
                id_material=int(material_dd.value),
                codigo_copia=codigo.value,
                ubicacion=ubicacion.value,
                coleccion=coleccion.value,
                id_estado=int(estado.value),
                formato=formato.value
            )
            
            dialog.open = False
            self.load_data()
            self.page.update()
        
        dialog.actions[0].on_click = save
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.open(dialog)

    def delete_item(self, copia):
        self.controller.delete_copia(copia.id_copia)
        self.load_data()