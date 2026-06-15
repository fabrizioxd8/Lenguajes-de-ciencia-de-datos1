-- ============================================================
-- schema.sql
-- Script de creación de base de datos para el sistema de
-- detección de crisis en redes sociales.
-- ============================================================

-- Tabla principal de comentarios analizados
CREATE TABLE IF NOT EXISTS comentarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_original   TEXT    NOT NULL,
    texto_original TEXT   NOT NULL,
    texto_limpio   TEXT   NOT NULL,
    usuario        TEXT   NOT NULL DEFAULT '',
    fecha          TEXT   NOT NULL,
    categoria      TEXT   NOT NULL,   -- muy positivo | positivo | neutro | negativo | muy negativo
    puntuacion     REAL   NOT NULL,
    fecha_proceso  TEXT   NOT NULL
);

-- Tabla de alertas generadas por el sistema
CREATE TABLE IF NOT EXISTS alertas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_comentario TEXT    NOT NULL,
    texto         TEXT    NOT NULL,
    usuario       TEXT    NOT NULL DEFAULT '',
    puntuacion    REAL    NOT NULL,
    umbral        REAL    NOT NULL,
    fecha_alerta  TEXT    NOT NULL,
    activa        INTEGER NOT NULL DEFAULT 1   -- 1 = activa, 0 = resuelta
);

-- Índices para optimizar consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_comentarios_categoria   ON comentarios (categoria);
CREATE INDEX IF NOT EXISTS idx_comentarios_fecha       ON comentarios (fecha_proceso);
CREATE INDEX IF NOT EXISTS idx_alertas_activa          ON alertas (activa);
CREATE INDEX IF NOT EXISTS idx_alertas_comentario      ON alertas (id_comentario);
