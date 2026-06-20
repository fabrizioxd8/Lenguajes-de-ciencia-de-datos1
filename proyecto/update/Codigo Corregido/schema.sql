-- schema.sql — Esquema MySQL del sistema Crisis Monitor
-- Uso opcional: el sistema crea la base y las tablas automáticamente al iniciar.
-- Para crearlas a mano:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS crisis_monitor CHARACTER SET utf8mb4;
USE crisis_monitor;

CREATE TABLE IF NOT EXISTS comentarios (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    id_original    VARCHAR(64)  NOT NULL,
    texto_original TEXT         NOT NULL,
    texto_limpio   TEXT         NOT NULL,
    usuario        VARCHAR(120) NOT NULL DEFAULT '',
    fecha          VARCHAR(40)  NOT NULL,
    categoria      VARCHAR(20)  NOT NULL,
    puntuacion     FLOAT        NOT NULL,
    fecha_proceso  VARCHAR(20)  NOT NULL,
    INDEX idx_cat   (categoria),
    INDEX idx_fecha (fecha_proceso)
);

CREATE TABLE IF NOT EXISTS alertas (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    id_comentario VARCHAR(64)  NOT NULL,
    texto         TEXT         NOT NULL,
    usuario       VARCHAR(120) NOT NULL DEFAULT '',
    puntuacion    FLOAT        NOT NULL,
    umbral        FLOAT        NOT NULL,
    fecha_alerta  VARCHAR(20)  NOT NULL,
    activa        TINYINT      NOT NULL DEFAULT 1,
    INDEX idx_act (activa)
);
