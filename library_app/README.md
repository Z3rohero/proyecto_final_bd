# Biblioteca

Sistema de gestión de biblioteca con Flet y PostgreSQL.

## Requisitos

- Python 3.10+
- Docker y Docker Compose (para ejecución con contenedores)
- PostgreSQL 15 (si ejecutas sin Docker)

## Instalación y Ejecución

### Opción 1: Con Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio y navegar al directorio
cd library_app

# 2. Crear archivo .env desde el ejemplo
cp .env.example .env

# 3. Construir y ejecutar con Docker Compose
docker-compose up --build

# La aplicación estará disponible en http://localhost:8550
# PostgreSQL estará en localhost:5433
```

Para detener los servicios:
```bash
docker-compose down
```

Para detener y eliminar los datos:
```bash
docker-compose down -v
```

### Opción 2: Instalación Manual

```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate  # En Linux/Mac
# venv\Scripts\activate  # En Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar base de datos con Docker
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

### Modo Desarrollo

```bash
# Ejecutar con recarga automática
flet run -r src/app.py
```

## Comandos Útiles de Docker

```bash
# Ver logs de la aplicación
docker-compose logs -f app

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Acceder a la base de datos
docker exec -it postgres-biblioteca psql -U usuario -d biblioteca_demo

# Reiniciar solo la aplicación
docker-compose restart app

# Reconstruir la aplicación
docker-compose up --build app
<<<<<<< HEAD

#Eliminar informacion de volumen

docker-compose down -v
=======
>>>>>>> master
```

## Usuarios por Defecto

Después de ejecutar los scripts de inicialización, puedes crear usuarios con diferentes roles:

- **Bibliotecario**: Acceso completo al panel administrativo
- **Estudiante/Profesor**: Acceso al catálogo y gestión de préstamos

## Configuración

Edita el archivo `.env` para cambiar la configuración de la base de datos:

```env
DATABASE_URL=postgresql://usuario:password@localhost:5433/biblioteca_demo
DB_HOST=localhost
DB_PORT=5433
DB_NAME=biblioteca_demo
DB_USER=usuario
DB_PASSWORD=password
```
