import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from sqlalchemy.orm import Session
from model.db import engine
from model.models import Idioma,MaterialAutor,Autor,Material



def seed_materiales():
    session = Session(bind=engine)

    try:
        # ---------------------------------------------------------
        # 1. IDIOMAS
        # ---------------------------------------------------------
        idiomas_data = ["Español", "Inglés", "Francés"]

        idiomas = {}
        for nombre in idiomas_data:
            idioma = session.query(Idioma).filter_by(nombre=nombre).first()
            if not idioma:
                idioma = Idioma(nombre=nombre)
                session.add(idioma)
                session.flush()
            idiomas[nombre] = idioma

        # ---------------------------------------------------------
        # 2. AUTORES
        # ---------------------------------------------------------
        autores_data = [
            "Gabriel García Márquez",
            "Robert C. Martin",
            "Antoine de Saint-Exupéry",
            "Michael T. Goodrich",
        ]

        autores = {}
        for nombre in autores_data:
            autor = session.query(Autor).filter_by(nombre=nombre).first()
            if not autor:
                autor = Autor(nombre=nombre)
                session.add(autor)
                session.flush()
            autores[nombre] = autor

        # ---------------------------------------------------------
        # 3. MATERIALES
        # ---------------------------------------------------------
        materiales_data = [
            {
                "titulo": "Cien años de soledad",
                "descripcion": "Obra maestra del realismo mágico.",
                "idioma": "Español",
                "tipo_material": "Libro",
                "año_publicacion": 1967,
                "isbn": "9780307474728",
                "autores": ["Gabriel García Márquez"]
            },
            {
                "titulo": "Clean Code",
                "descripcion": "Guía indispensable de buenas prácticas.",
                "idioma": "Inglés",
                "tipo_material": "Libro",
                "año_publicacion": 2008,
                "isbn": "9780132350884",
                "autores": ["Robert C. Martin"]
            },
            {
                "titulo": "El Principito",
                "descripcion": "Clásico universal con enseñanzas profundas.",
                "idioma": "Francés",
                "tipo_material": "Libro",
                "año_publicacion": 1943,
                "isbn": "9780156013987",
                "autores": ["Antoine de Saint-Exupéry"]
            },
            {
                "titulo": "Estructuras de Datos y Algoritmos en Python",
                "descripcion": "Libro moderno sobre estructuras de datos.",
                "idioma": "Español",
                "tipo_material": "Libro",
                "año_publicacion": 2019,
                "isbn": "9781118290279",
                "autores": ["Michael T. Goodrich"]
            }
        ]

        for item in materiales_data:
            existente = session.query(Material).filter_by(titulo=item["titulo"]).first()
            if existente:
                continue

            material = Material(
                titulo=item["titulo"],
                descripcion=item["descripcion"],
                id_idioma=idiomas[item["idioma"]].id_idioma,
                tipo_material=item["tipo_material"],
                año_publicacion=item["año_publicacion"],
                isbn=item["isbn"]
            )
            session.add(material)
            session.flush()

            # ---------------------------------------------------------
            # 4. RELACIONES Material ↔ Autor
            # ---------------------------------------------------------
            for idx, autor_nombre in enumerate(item["autores"], start=1):
                rel = MaterialAutor(
                    id_material=material.id_material,
                    id_autor=autores[autor_nombre].id_autor,
                    orden=idx
                )
                session.add(rel)

        session.commit()
        print("Seed de materiales ejecutado correctamente.")

    except Exception as e:
        session.rollback()
        print("ERROR en seed:", e)

    finally:
        session.close()


if __name__ == "__main__":
    seed_materiales()
