-- Eliminamos la BD si existe y la creamos de nuevo
DROP DATABASE IF EXISTS turnos;
CREATE DATABASE turnos CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE turnos;

-- ==========================
-- TABLA: negocio
-- ==========================
CREATE TABLE negocio (
    id_negocio   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    direccion    VARCHAR(150),
    telefono     VARCHAR(30)
) ENGINE=InnoDB;

-- ==========================
-- TABLA: usuario
-- ==========================
CREATE TABLE usuario (
    id_usuario   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    correo       VARCHAR(150) NOT NULL,
    contraseña   VARCHAR(255) NOT NULL,
    id_negocio   INT UNSIGNED NULL,
    
    CONSTRAINT fk_usuario_negocio
        FOREIGN KEY (id_negocio)
        REFERENCES negocio(id_negocio)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT uq_usuario_correo UNIQUE (correo)
) ENGINE=InnoDB;

-- ==========================
-- TABLA: profesional
-- ==========================
CREATE TABLE profesional (
    id_profesional INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    id_negocio     INT UNSIGNED NOT NULL,
    
    CONSTRAINT fk_profesional_negocio
        FOREIGN KEY (id_negocio)
        REFERENCES negocio(id_negocio)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================
-- TABLA: servicio
-- ==========================
CREATE TABLE servicio (
    id_servicio      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    duracion_minutos INT UNSIGNED NOT NULL,
    id_negocio       INT UNSIGNED NOT NULL,
    
    CONSTRAINT fk_servicio_negocio
        FOREIGN KEY (id_negocio)
        REFERENCES negocio(id_negocio)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================
-- TABLA: cliente
-- ==========================
CREATE TABLE cliente (
    id_cliente  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    telefono    VARCHAR(30),
    id_negocio  INT UNSIGNED NOT NULL,
    
    CONSTRAINT fk_cliente_negocio
        FOREIGN KEY (id_negocio)
        REFERENCES negocio(id_negocio)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================
-- TABLA: disponibilidad
-- ==========================
CREATE TABLE disponibilidad (
    id_disponibilidad INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_profesional    INT UNSIGNED NOT NULL,
    dia_semana        TINYINT UNSIGNED NOT NULL,  -- 1-7 por ejemplo
    hora_inicio       TIME NOT NULL,
    hora_fin          TIME NOT NULL,
    
    CONSTRAINT fk_disponibilidad_profesional
        FOREIGN KEY (id_profesional)
        REFERENCES profesional(id_profesional)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================
-- TABLA: turno
-- ==========================
CREATE TABLE turno (
    id_turno      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_profesional INT UNSIGNED NOT NULL,
    id_cliente     INT UNSIGNED NOT NULL,
    id_servicio    INT UNSIGNED NOT NULL,
    fecha          DATE NOT NULL,
    hora           TIME NOT NULL,
    estado         VARCHAR(50) NOT NULL,  -- p.ej.: 'pendiente', 'confirmado', 'cancelado'
    
    CONSTRAINT fk_turno_profesional
        FOREIGN KEY (id_profesional)
        REFERENCES profesional(id_profesional)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_turno_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_turno_servicio
        FOREIGN KEY (id_servicio)
        REFERENCES servicio(id_servicio)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
