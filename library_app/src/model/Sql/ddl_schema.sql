CREATE TABLE idioma (
    id_idioma SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE rol (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE usuario_rol (
    id_usuario INT REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    id_rol INT REFERENCES rol(id_rol) ON DELETE CASCADE,
    PRIMARY KEY (id_usuario, id_rol)
);

CREATE TABLE autor (
    id_autor SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL
);

CREATE TABLE material (
    id_material SERIAL PRIMARY KEY,
    titulo VARCHAR(300) NOT NULL,
    descripcion TEXT,
    id_idioma INT REFERENCES idioma(id_idioma) ON DELETE SET NULL,
    tipo_material VARCHAR(50) NOT NULL,
    año_publicacion INT,
    isbn VARCHAR(30)
);

CREATE TABLE material_autor (
    id_material INT REFERENCES material(id_material) ON DELETE CASCADE,
    id_autor INT REFERENCES autor(id_autor) ON DELETE CASCADE,
    orden INT DEFAULT 1,
    PRIMARY KEY (id_material, id_autor)
);

CREATE TABLE estado (
    id_estado SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE copia (
    id_copia SERIAL PRIMARY KEY,
    id_material INT NOT NULL REFERENCES material(id_material) ON DELETE CASCADE,
    id_estado INT NOT NULL REFERENCES estado(id_estado),
    codigo_copia VARCHAR(50) UNIQUE NOT NULL,
    ubicacion VARCHAR(200),
    coleccion VARCHAR(100),
    formato VARCHAR(30) DEFAULT 'fisico',
    fecha_adquisicion DATE DEFAULT CURRENT_DATE
);

CREATE TABLE prestamo (
    id_prestamo SERIAL PRIMARY KEY,
    id_copia INT REFERENCES copia(id_copia) ON DELETE RESTRICT,
    id_usuario INT REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    fecha_prestamo DATE DEFAULT CURRENT_DATE,
    fecha_devolucion_prevista DATE NOT NULL,
    fecha_devolucion_real DATE,
    estado VARCHAR(20) NOT NULL,
    multa NUMERIC(8,2) DEFAULT 0
);

CREATE TABLE reserva (
    id_reserva SERIAL PRIMARY KEY,
    id_copia INT REFERENCES copia(id_copia) ON DELETE RESTRICT,
    id_usuario INT REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL
);

CREATE TABLE movimiento (
    id_movimiento SERIAL PRIMARY KEY,
    id_copia INT REFERENCES copia(id_copia) ON DELETE SET NULL,
    id_usuario INT REFERENCES usuario(id_usuario) ON DELETE SET NULL,
    id_estado INT NOT NULL REFERENCES estado(id_estado),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion DATE NOT NULL,
    detalle TEXT
);
