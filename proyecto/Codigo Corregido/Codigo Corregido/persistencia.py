"""
persistencia.py
---------------
Módulo de persistencia para el sistema de detección de crisis.
Soporta escritura y lectura en TXT, CSV filtrado, Pickle y SQLite
con operaciones DML completas (INSERT, SELECT, UPDATE, DELETE).
"""

import csv
import os
import pickle
import sqlite3
from datetime import datetime


class GestorPersistencia:
    """
    Gestor centralizado de persistencia de datos del sistema.

    Proporciona métodos para guardar y recuperar comentarios y alertas
    en cuatro formatos: texto plano, CSV filtrado, Pickle y SQLite.

    Attributes (privados):
        __directorio (str): Directorio de salida para archivos generados.
        __db_path (str):    Ruta del archivo de base de datos SQLite.
    """

    # Campos exportados en CSV
    _CAMPOS_CSV = ["id", "usuario", "fecha", "texto", "texto_limpio", "categoria", "puntuacion"]

    def __init__(self, directorio_salida="datos_salida", db_path="crisis.db"):
        """
        Inicializa el gestor creando el directorio de salida y la base de datos.

        Args:
            directorio_salida (str): Carpeta donde se almacenan los archivos.
            db_path (str):           Ruta al archivo SQLite.

        Raises:
            RuntimeError: Si no se puede crear la base de datos.
        """
        self.__directorio = directorio_salida
        self.__db_path = db_path
        self.__crear_directorio()
        self.__inicializar_db()

    # ------------------------------------------------------------------ setup

    def __crear_directorio(self):
        """Crea el directorio de salida si no existe."""
        if not os.path.exists(self.__directorio):
            os.makedirs(self.__directorio)

    def __inicializar_db(self):
        """
        Crea las tablas de la base de datos a partir de schema.sql.
        Si el archivo no existe, aplica un schema mínimo embebido.

        Raises:
            RuntimeError: Si SQLite lanza un error durante la inicialización.
        """
        schema_embebido = """
        CREATE TABLE IF NOT EXISTS comentarios (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            id_original    TEXT    NOT NULL,
            texto_original TEXT    NOT NULL,
            texto_limpio   TEXT    NOT NULL,
            usuario        TEXT    NOT NULL DEFAULT '',
            fecha          TEXT    NOT NULL,
            categoria      TEXT    NOT NULL,
            puntuacion     REAL    NOT NULL,
            fecha_proceso  TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alertas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            id_comentario TEXT    NOT NULL,
            texto         TEXT    NOT NULL,
            usuario       TEXT    NOT NULL DEFAULT '',
            puntuacion    REAL    NOT NULL,
            umbral        REAL    NOT NULL,
            fecha_alerta  TEXT    NOT NULL,
            activa        INTEGER NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_cat   ON comentarios (categoria);
        CREATE INDEX IF NOT EXISTS idx_fecha ON comentarios (fecha_proceso);
        CREATE INDEX IF NOT EXISTS idx_act   ON alertas (activa);
        """

        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            schema_path = "schema.sql"

            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    script = f.read()
            else:
                script = schema_embebido

            conexion.executescript(script)
            conexion.commit()

        except sqlite3.Error as exc:
            raise RuntimeError(f"No se pudo inicializar la base de datos: {exc}")
        finally:
            if conexion:
                conexion.close()

    # ------------------------------------------------------------------ TXT

    def guardar_txt(self, datos, nombre_archivo="comentarios.txt"):
        """
        Guarda todos los comentarios analizados en un archivo de texto.

        Args:
            datos (list[dict]):    Comentarios analizados.
            nombre_archivo (str):  Nombre del archivo de salida.

        Returns:
            str: Ruta absoluta del archivo generado.
        """
        ruta = os.path.join(self.__directorio, nombre_archivo)

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("ANÁLISIS DE SENTIMIENTO — EXPORTACIÓN COMPLETA\n")
            f.write(f"Generado : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total    : {len(datos)} comentarios\n")
            f.write("=" * 72 + "\n\n")

            for idx, item in enumerate(datos, start=1):
                f.write(f"[{idx:04d}] ID: {item.get('id', 'N/A')}\n")
                f.write(f"       Usuario    : {item.get('usuario', '') or 'N/A'}\n")
                f.write(f"       Fecha      : {item.get('fecha', 'N/A')}\n")
                f.write(f"       Texto orig : {item.get('texto', 'N/A')}\n")
                f.write(f"       Texto limpio: {item.get('texto_limpio', 'N/A')}\n")
                f.write(f"       Categoría  : {item.get('categoria', 'N/A').upper()}\n")
                f.write(f"       Puntuación : {item.get('puntuacion', 0):.4f}\n")
                palabras = ", ".join(item.get("palabras_clave", [])) or "(ninguna)"
                f.write(f"       Palabras   : {palabras}\n")
                f.write("-" * 72 + "\n")

        return ruta

    # ------------------------------------------------------------------ CSV filtrado

    def guardar_csv_filtrado(self, datos, categorias_filtro=None,
                              nombre_archivo="negativos.csv"):
        """
        Exporta en CSV solo los comentarios de las categorías indicadas.

        Args:
            datos (list[dict]):          Comentarios analizados.
            categorias_filtro (list):    Categorías a incluir.
                                         Por defecto: ['negativo', 'muy negativo'].
            nombre_archivo (str):        Nombre del archivo CSV.

        Returns:
            str: Ruta absoluta del archivo generado.
        """
        if categorias_filtro is None:
            categorias_filtro = ["negativo", "muy negativo"]

        filtrados = list(filter(
            lambda x: x.get("categoria", "") in categorias_filtro,
            datos
        ))

        ruta = os.path.join(self.__directorio, nombre_archivo)

        # Cada fila se arma con comprensión de diccionario,
        # tomando solo los campos definidos en _CAMPOS_CSV
        filas = [
            {campo: item.get(campo, "") for campo in self._CAMPOS_CSV}
            for item in filtrados
        ]

        with open(ruta, "w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=self._CAMPOS_CSV)
            escritor.writeheader()
            escritor.writerows(filas)

        return ruta

    # ------------------------------------------------------------------ Pickle

    def guardar_pickle(self, datos, nombre_archivo="datos.pkl"):
        """
        Serializa el objeto datos en un archivo Pickle binario.

        Args:
            datos (object):       Cualquier objeto serializable.
            nombre_archivo (str): Nombre del archivo de salida.

        Returns:
            str: Ruta absoluta del archivo generado.
        """
        ruta = os.path.join(self.__directorio, nombre_archivo)

        with open(ruta, "wb") as f:
            pickle.dump(datos, f)

        return ruta

    def cargar_pickle(self, nombre_archivo="datos.pkl"):
        """
        Deserializa y retorna los datos de un archivo Pickle.

        Args:
            nombre_archivo (str): Nombre del archivo Pickle.

        Returns:
            object: Datos deserializados.

        Raises:
            FileNotFoundError: Si el archivo no existe.
        """
        ruta = os.path.join(self.__directorio, nombre_archivo)

        if not os.path.exists(ruta):
            raise FileNotFoundError(f"Archivo Pickle no encontrado: {ruta}")

        with open(ruta, "rb") as f:
            return pickle.load(f)

    # ------------------------------------------------------------------ SQLite INSERT

    def insertar_comentario(self, comentario):
        """
        INSERT: Inserta un único comentario en la tabla 'comentarios'.

        Args:
            comentario (dict): Comentario analizado.

        Returns:
            int: ID generado por SQLite (rowid).

        Raises:
            RuntimeError: Si ocurre un error en la base de datos.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO comentarios
                    (id_original, texto_original, texto_limpio, usuario,
                     fecha, categoria, puntuacion, fecha_proceso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    comentario.get("id", ""),
                    comentario.get("texto", ""),
                    comentario.get("texto_limpio", ""),
                    comentario.get("usuario", ""),
                    comentario.get("fecha", ""),
                    comentario.get("categoria", ""),
                    comentario.get("puntuacion", 0.0),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conexion.commit()
            return cursor.lastrowid

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al insertar comentario: {exc}")
        finally:
            if conexion:
                conexion.close()

    def insertar_lote_comentarios(self, datos):
        """
        INSERT masivo: inserta todos los comentarios del lote en una transacción.

        Args:
            datos (list[dict]): Lista de comentarios analizados.

        Returns:
            int: Número de filas insertadas.

        Raises:
            RuntimeError: Si falla la transacción.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            registros = [
                (
                    item.get("id", ""),
                    item.get("texto", ""),
                    item.get("texto_limpio", ""),
                    item.get("usuario", ""),
                    item.get("fecha", ""),
                    item.get("categoria", ""),
                    item.get("puntuacion", 0.0),
                    ahora,
                )
                for item in datos
            ]

            cursor.executemany(
                """
                INSERT INTO comentarios
                    (id_original, texto_original, texto_limpio, usuario,
                     fecha, categoria, puntuacion, fecha_proceso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                registros,
            )
            conexion.commit()
            return cursor.rowcount

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error en inserción masiva: {exc}")
        finally:
            if conexion:
                conexion.close()

    def insertar_alerta(self, alerta):
        """
        INSERT: Guarda una alerta en la tabla 'alertas'.

        Args:
            alerta (dict): Alerta generada por GestorAlertas.

        Returns:
            int: ID generado por SQLite.

        Raises:
            RuntimeError: Si falla la inserción.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO alertas
                    (id_comentario, texto, usuario, puntuacion, umbral, fecha_alerta, activa)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alerta.get("id_comentario", ""),
                    alerta.get("texto", ""),
                    alerta.get("usuario", ""),
                    alerta.get("puntuacion", 0.0),
                    alerta.get("umbral", 0.0),
                    alerta.get("fecha_alerta",
                               datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    1 if alerta.get("activa", True) else 0,
                ),
            )
            conexion.commit()
            return cursor.lastrowid

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al insertar alerta: {exc}")
        finally:
            if conexion:
                conexion.close()

    # ------------------------------------------------------------------ SQLite SELECT

    def seleccionar_comentarios(self, categoria=None, limite=None):
        """
        SELECT: Recupera comentarios con filtros opcionales.

        Args:
            categoria (str | None): Filtrar por categoría exacta.
            limite (int | None):    Número máximo de filas a retornar.

        Returns:
            list[dict]: Filas como diccionarios (row_factory).

        Raises:
            RuntimeError: Si falla la consulta.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()

            query  = "SELECT * FROM comentarios"
            params = []

            if categoria:
                query += " WHERE categoria = ?"
                params.append(categoria)

            query += " ORDER BY fecha_proceso DESC"

            if limite:
                query += " LIMIT ?"
                params.append(limite)

            cursor.execute(query, params)
            return [dict(fila) for fila in cursor.fetchall()]

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al consultar comentarios: {exc}")
        finally:
            if conexion:
                conexion.close()

    def seleccionar_alertas(self, solo_activas=False):
        """
        SELECT: Recupera alertas almacenadas.

        Args:
            solo_activas (bool): Si True, retorna solo las alertas activas (activa=1).

        Returns:
            list[dict]: Alertas como diccionarios.

        Raises:
            RuntimeError: Si falla la consulta.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()

            if solo_activas:
                cursor.execute(
                    "SELECT * FROM alertas WHERE activa = 1 ORDER BY fecha_alerta DESC"
                )
            else:
                cursor.execute(
                    "SELECT * FROM alertas ORDER BY fecha_alerta DESC"
                )

            return [dict(fila) for fila in cursor.fetchall()]

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al consultar alertas: {exc}")
        finally:
            if conexion:
                conexion.close()

    # ------------------------------------------------------------------ SQLite UPDATE

    def actualizar_categoria(self, id_original, nueva_categoria):
        """
        UPDATE: Cambia la categoría de un comentario por su ID original.

        Args:
            id_original (str):      ID del comentario a modificar.
            nueva_categoria (str):  Nueva etiqueta de categoría.

        Returns:
            int: Número de filas afectadas.

        Raises:
            RuntimeError: Si falla la actualización.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()

            cursor.execute(
                "UPDATE comentarios SET categoria = ? WHERE id_original = ?",
                (nueva_categoria, id_original),
            )
            conexion.commit()
            return cursor.rowcount

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al actualizar comentario: {exc}")
        finally:
            if conexion:
                conexion.close()

    def resolver_alerta(self, id_alerta):
        """
        UPDATE: Marca una alerta como resuelta (activa = 0).

        Args:
            id_alerta (int): ID de la alerta en la tabla 'alertas'.

        Returns:
            int: Número de filas actualizadas.

        Raises:
            RuntimeError: Si falla la actualización.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()

            cursor.execute(
                "UPDATE alertas SET activa = 0 WHERE id = ?",
                (id_alerta,),
            )
            conexion.commit()
            return cursor.rowcount

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al resolver alerta: {exc}")
        finally:
            if conexion:
                conexion.close()

    # ------------------------------------------------------------------ SQLite DELETE

    def eliminar_comentario(self, id_original):
        """
        DELETE: Elimina un comentario por su ID original.

        Args:
            id_original (str): ID del registro a eliminar.

        Returns:
            int: Número de filas eliminadas.

        Raises:
            RuntimeError: Si falla la eliminación.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()

            cursor.execute(
                "DELETE FROM comentarios WHERE id_original = ?",
                (id_original,),
            )
            conexion.commit()
            return cursor.rowcount

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al eliminar comentario: {exc}")
        finally:
            if conexion:
                conexion.close()

    def limpiar_alertas_resueltas(self):
        """
        DELETE: Elimina todas las alertas ya resueltas (activa = 0).

        Returns:
            int: Número de filas eliminadas.

        Raises:
            RuntimeError: Si falla la eliminación.
        """
        conexion = None
        try:
            conexion = sqlite3.connect(self.__db_path)
            cursor = conexion.cursor()

            cursor.execute("DELETE FROM alertas WHERE activa = 0")
            conexion.commit()
            return cursor.rowcount

        except sqlite3.Error as exc:
            raise RuntimeError(f"Error al limpiar alertas: {exc}")
        finally:
            if conexion:
                conexion.close()

    # ------------------------------------------------------------------ operación compuesta

    def guardar_lote_completo(self, datos, alertas):
        """
        Persiste datos y alertas en todos los formatos en una sola llamada.

        Args:
            datos (list[dict]):   Comentarios analizados.
            alertas (list[dict]): Alertas generadas.

        Returns:
            dict: Rutas de archivos generados y conteos de filas insertadas.
        """
        resultado = {}
        resultado["txt"]    = self.guardar_txt(datos)
        resultado["csv"]    = self.guardar_csv_filtrado(datos)
        resultado["pickle"] = self.guardar_pickle({"datos": datos, "alertas": alertas})
        resultado["sqlite_comentarios"] = self.insertar_lote_comentarios(datos)

        n_alertas = 0
        for alerta in alertas:
            try:
                self.insertar_alerta(alerta)
                n_alertas += 1
            except RuntimeError:
                pass
        resultado["sqlite_alertas"] = n_alertas

        return resultado
