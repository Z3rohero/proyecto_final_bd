# 📚 Sistema de Gestión de Biblioteca

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flet](https://img.shields.io/badge/Flet-0.24.1-purple.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)

Sistema integral de gestión bibliotecaria desarrollado con Flet (framework Python para aplicaciones multiplataforma) y PostgreSQL, implementando arquitectura MVC con gestión completa de préstamos, reservas y multas.

</div>


## ✨ Características

### Para Bibliotecarios (Administradores)
- ✅ **Gestión de Usuarios**: CRUD completo de usuarios con roles
- ✅ **Gestión de Materiales**: Alta, modificación y eliminación de materiales bibliográficos
- ✅ **Gestión de Copias**: Control de ejemplares físicos por ubicación y estado
- ✅ **Gestión de Préstamos**: Aprobación y seguimiento de solicitudes
- ✅ **Gestión de Reservas**: Administración de reservas activas

### Para Estudiantes/Profesores
- 📖 **Catálogo Digital**: Búsqueda y consulta de materiales disponibles
- 📝 **Solicitud de Préstamos**: Solicitud de prestamo bibliografico
- 🔖 **Sistema de Reservas**: Reserva de materiales prestados
- 📊 **Mis Préstamos**: Seguimiento de préstamos activos e históricos

### Características Técnicas
- 🔐 **Autenticación segura** con bcrypt
- 🎯 **Control de acceso basado en roles** (RBAC)
- 💰 **Sistema de multas automático** con cálculo progresivo
- 📧 **Validación de usuarios** con correo electrónico único
- 🔄 **Gestión de estados** (disponible, prestado, reservado)
- 📅 **Control de fechas** y plazos de devolución

---

## 🛠 Tecnologías

| Categoría | Tecnología | Versión |
|-----------|-----------|---------|
| **Frontend/UI** | Flet | 0.24.1 |
| **Backend** | Python | 3.10+ |
| **Base de Datos** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Containerización** | Docker & Docker Compose | Latest |
| **Seguridad** | bcrypt | Latest |

---

## 🏗 Arquitectura

El proyecto implementa el patrón **MVC (Model-View-Controller)**:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│    View     │ ───> │  Controller  │ ───> │    Model    │
│  (Flet UI)  │ <─── │   (Logic)    │ <─── │ (SQLAlchemy)│
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │ PostgreSQL  │
                                            └─────────────┘
```

---

## 📦 Requisitos Previos

- **Python** 3.10 o superior
- **Docker** y **Docker Compose** (para ejecución en contenedores)
- **PostgreSQL** 15 (si se ejecuta sin Docker)
- **Git** para clonar el repositorio

---

## 🚀 Instalación

### Opción 1: Con Docker Compose (⭐ Recomendado)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd proyecto_final_bd/library_app


# 2. Construir y ejecutar los servicios
docker-compose up --build

# ✅ La aplicación estará disponible en http://localhost:8550
# ✅ PostgreSQL estará en localhost:5433
```
**Eliminar datos (reinicio completo):**
```bash
docker-compose down -v
```

### Opción 2: Instalación Local

```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar PostgreSQL con Docker
docker run -d \
  --name postgres-biblioteca \
  -e POSTGRES_USER=usuario \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=biblioteca_demo \
  -p 5433:5432 \
  postgres:15

# 5. Ejecutar scripts de inicialización
python src/scripts/seed_roles.py
python src/scripts/seed_estado.py
python src/scripts/seed_material.py

# 6. Ejecutar la aplicación
cd src
python app.py
```

### Modo Desarrollo (con recarga automática)

```bash
flet run -r src/app.py
```

---

## ⚙️ Configuración

### Variables de Entorno

Edita el archivo `.env` para personalizar la configuración:

```env
# Configuración de Base de Datos
DATABASE_URL=postgresql://usuario:password@localhost:5433/biblioteca_demo
DB_HOST=localhost
DB_PORT=5433
DB_NAME=biblioteca_demo
DB_USER=usuario
DB_PASSWORD=password

# Puerto de la Aplicación
APP_PORT=8550
```


## 📜 Reglas de Negocio

### Sistema de Multas

Las multas se calculan automáticamente según los días de atraso:

| Días de Atraso | Multa |
|----------------|-------|
| 1er día | $1,000 COP |
| 2º - 7º día | $2,500 COP |
| 8º día en adelante | $2,500 COP + $100 COP por cada día adicional |

**Restricciones:**
- ⛔ Usuarios con multas pendientes **NO** pueden solicitar préstamos
- ⛔ Usuarios con multas pendientes **NO** pueden crear reservas
- ✅ Las multas se generan automáticamente al devolver con atraso

### Estados de Copias

1. **Disponible**: Puede ser solicitada en préstamo
2. **Prestado**: En poder de un usuario (permite reservas)
3. **Reservado**: En proceso de aprobación de préstamo

### Flujo de Préstamos

```
Solicitud → Reservado → Aprobación → Prestado → Devolución → Disponible
                ↓           ↓            ↓
            Movimiento   Prestamo    Multa (si aplica)
```

---



### PostgreSQL

```sql
-- Ver todas las tablas
\dt

-- Describir tabla
\d nombre_tabla

-- Consultar usuarios
SELECT * FROM usuario;

---



