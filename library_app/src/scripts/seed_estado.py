import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from sqlalchemy.orm import sessionmaker
from model.db import engine
from model.models import Estado  

Session = sessionmaker(bind=engine)
session = Session()

estados = [
    {"nombre": "disponible"},
    {"nombre": "prestado"},
    {"nombre": "reservado"},
    {"nombre": "dañado"},
]

for e in estados:
    exists = session.query(Estado).filter_by(nombre=e["nombre"]).first()
    if not exists:
        estado = Estado(nombre=e["nombre"])
        session.add(estado)
session.commit()
print("Estados creados correctamente")