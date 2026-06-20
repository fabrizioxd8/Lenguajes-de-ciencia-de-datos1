"""
ingesta.py
----------
Módulo de ingesta de datos para el sistema de detección de crisis.
Lee archivos CSV con columnas id/texto/fecha, limpia el texto y detecta duplicados.
"""

import csv
import re
import os

# Longitud mínima del texto limpio para considerarlo un comentario real.
# Textos más cortos ("·", "AD", etc.) se descartan como ruido.
LONGITUD_MINIMA = 3


def _leer_con_codificacion(ruta_archivo, codificacion):
    """
    Lee el CSV con una codificación específica y valida sus columnas.

    Función auxiliar de leer_csv() para no repetir el mismo bloque
    de lectura con cada codificación.

    Args:
        ruta_archivo (str): Ruta al archivo CSV.
        codificacion (str): Codificación del archivo ('utf-8' o 'latin-1').

    Returns:
        list[dict]: Lista de registros con claves 'id', 'texto', 'fecha'.

    Raises:
        ValueError: Si el CSV no posee las columnas requeridas.
    """
    columnas_requeridas = {"id", "texto", "fecha"}
    datos = []

    with open(ruta_archivo, "r", encoding=codificacion) as archivo:
        lector = csv.DictReader(archivo)

        encabezados = set(lector.fieldnames or [])
        if not columnas_requeridas.issubset(encabezados):
            faltantes = columnas_requeridas - encabezados
            raise ValueError(
                f"Columnas faltantes en el CSV: {faltantes}. "
                f"Columnas encontradas: {encabezados}"
            )

        for fila in lector:
            registro = {
                "id":      fila["id"].strip(),
                "texto":   fila["texto"].strip(),
                "fecha":   fila["fecha"].strip(),
                # La columna usuario es opcional: si no existe, queda vacía
                "usuario": (fila.get("usuario") or "").strip(),
            }
            # Descartar filas completamente vacías
            if any(registro.values()):
                datos.append(registro)

    return datos


def leer_csv(ruta_archivo):
    """
    Lee un archivo CSV y retorna una lista de diccionarios.

    El archivo debe contener al menos las columnas: id, texto, fecha.
    Intenta primero con utf-8; si falla, reintenta con latin-1.

    Args:
        ruta_archivo (str): Ruta al archivo CSV.

    Returns:
        list[dict]: Lista de registros con claves 'id', 'texto', 'fecha'.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
        ValueError: Si el CSV no posee las columnas requeridas.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

    try:
        datos = _leer_con_codificacion(ruta_archivo, "utf-8")
    except UnicodeDecodeError:
        # Reintentar con latin-1 si utf-8 falla
        datos = _leer_con_codificacion(ruta_archivo, "latin-1")

    return datos


def limpiar_texto(texto):
    """
    Limpia un texto para el análisis de sentimiento.

    Pasos aplicados:
        1. Conversión a minúsculas.
        2. Eliminación de URLs y @menciones (no aportan sentimiento y, al
           contar como palabras, diluirían la puntuación normalizada).
        3. Conservación de la palabra de cada hashtag (se quita solo el '#').
        4. Eliminación de caracteres especiales (conserva letras acentuadas,
           ñ, dígitos y espacios).
        5. Colapso de espacios múltiples.

    Args:
        texto (str): Texto sin procesar.

    Returns:
        str: Texto normalizado y limpio.
    """
    if not isinstance(texto, str):
        texto = str(texto)

    texto = texto.lower()
    texto = re.sub(r"http\S+|www\.\S+", " ", texto)   # elimina URLs
    texto = re.sub(r"@\w+", " ", texto)               # elimina @menciones
    texto = re.sub(r"#(\w+)", r"\1", texto)           # conserva la palabra del hashtag
    # Conservar letras del español (incluyendo acentos y ñ), dígitos y espacios
    texto = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", texto, flags=re.UNICODE)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def detectar_duplicados(datos):
    """
    Detecta y separa registros duplicados basándose en el texto limpio.

    Dos comentarios se consideran duplicados si producen el mismo texto
    al aplicar limpiar_texto(), independientemente de su ID o fecha.

    Args:
        datos (list[dict]): Lista de registros con al menos la clave 'texto'.

    Returns:
        tuple[list[dict], list[dict]]:
            - datos_unicos: registros sin duplicados, con clave 'texto_limpio' añadida.
            - duplicados: registros que eran copia de uno anterior.
    """
    vistos = {}       # texto_limpio -> id del primer registro visto
    datos_unicos = []
    duplicados = []

    for item in datos:
        clave = limpiar_texto(item["texto"])

        if clave in vistos:
            duplicados.append(item)
        else:
            vistos[clave] = item["id"]
            registro = dict(item)               # copia del registro original
            registro["texto_limpio"] = clave    # agrega el texto normalizado
            datos_unicos.append(registro)

    return datos_unicos, duplicados


def procesar_datos(ruta_archivo):
    """
    Pipeline completo de ingesta: lectura → limpieza → deduplicación → filtro de ruido.

    Args:
        ruta_archivo (str): Ruta al archivo CSV de entrada.

    Returns:
        tuple[list[dict], dict]:
            - datos_procesados: lista de registros únicos con 'texto_limpio'.
            - estadisticas: dict con 'total_original', 'total_unicos',
              'total_duplicados', 'duplicados_ids' y 'total_ruido'.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el CSV no tiene las columnas requeridas.
    """
    datos_crudos = leer_csv(ruta_archivo)
    total_original = len(datos_crudos)

    datos_unicos, duplicados = detectar_duplicados(datos_crudos)

    # Filtrar ruido con filter() + lambda: se descartan registros cuyo
    # texto limpio es demasiado corto para ser un comentario real
    datos_validos = list(filter(
        lambda item: len(item["texto_limpio"]) >= LONGITUD_MINIMA,
        datos_unicos
    ))
    total_ruido = len(datos_unicos) - len(datos_validos)

    estadisticas = {
        "total_original":   total_original,
        "total_unicos":     len(datos_validos),
        "total_duplicados": len(duplicados),
        "duplicados_ids":   [d["id"] for d in duplicados],
        "total_ruido":      total_ruido,
    }

    return datos_validos, estadisticas
