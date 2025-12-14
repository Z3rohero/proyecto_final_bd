
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from model.models import (
Base, Idioma, Rol, Autor, Material, MaterialAutor, Copia,
get_engine
)
from model.usuario import *


# Cargar env
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")


if not DB_URL:
    raise RuntimeError("ERROR: No se pudo construir la URL de la base de datos")

engine = get_engine(DB_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
