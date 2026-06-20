"""
limpiar.py
----------
Utilidad para construir comentarios_x.csv a partir de exportaciones
de X (Twitter) en dos formatos posibles:

  Formato A — CSV exportado por herramientas como TwCommentExport:
      Columnas: ID, Name, Handle, TweetText, TweetCreateTime, ...
      Codificación: UTF-8, UTF-8-BOM o CP1252 (Windows-1252)
      Extensión habitual: .txt o .csv

      Particularidad: el archivo usa cinco tabulaciones seguidas de CRLF
      (\\t\\t\\t\\t\\t\\r\\n) como separador de fin de registro. Los tweets con
      saltos de línea internos se fragmentan en varios bloques físicos.
      El script reconstruye cada registro completo antes de parsearlo.

  Formato B — Texto crudo simple (formato original):
      Un comentario por línea, sin estructura CSV.
      El script descarta líneas de ruido (menciones aisladas,
      encabezados de fecha, líneas vacías, puntos sueltos, etc.)

El script detecta automáticamente el formato y la codificación.

Salida:
    comentarios_x.csv con columnas id, texto, fecha, usuario.

Uso:
    python limpiar.py                        # lee raw.txt por defecto
    python limpiar.py mi_export.txt          # archivo personalizado
    python limpiar.py export.csv salida.csv  # entrada y salida custom
"""

import csv
import io
import os
import re
import sys
from datetime import datetime

# ── Configuración ─────────────────────────────────────────────────────────────
ARCHIVO_ENTRADA = "raw.txt"
ARCHIVO_SALIDA  = "comentarios_x.csv"
FECHA_DEMO      = datetime.now().strftime("%Y-%m-%d")
LONGITUD_MINIMA = 5

# Columnas que identifican un CSV de Formato A
COLUMNAS_FORMATO_A = {"ID", "TweetText", "TweetCreateTime", "Handle"}

# Separador de fin de registro que usa TwCommentExport
_SEP_REGISTRO = "\t\t\t\t\t\r\n"

# Patrón de ID real de tweet de X (18-19 dígitos)
_ID_TWEET = re.compile(r"^\d{18,19}$")

# Inicio de bloque: puede venir entre comillas externas
_INICIO_BLOQUE = re.compile(r'^\"?(\d{18,19}),')

# Patrón para extraer la fecha de publicación del registro completo
_FECHA_RE = re.compile(r"(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}")


# ── Lectura ───────────────────────────────────────────────────────────────────

def _mejor_decodificacion(raw):
    """
    Elige entre CP850 y CP1252 la decodificación correcta de un texto DOS/Windows.

    Ambas codificaciones decodifican cualquier byte sin lanzar error, por lo que
    un try/except no las distingue. Los exports de X en español pueden venir en
    CP850 (consola DOS) o CP1252 (Windows); decodificar con la equivocada corrompe
    los acentos (ó→¢, ñ→¤…). Se decide por cuál produce más letras acentuadas del
    español legítimas y menos caracteres de reemplazo.

    Args:
        raw (bytes): Contenido binario del archivo.

    Returns:
        str: Texto decodificado con la codificación más plausible.
    """
    acentos = set("áéíóúüñ¿¡ÁÉÍÓÚÜÑ")
    mejor_texto, mejor_puntaje = None, -1
    for codificacion in ("cp850", "cp1252"):
        texto = raw.decode(codificacion, errors="replace")
        puntaje = sum(1 for c in texto if c in acentos) - texto.count("\ufffd")
        if puntaje > mejor_puntaje:
            mejor_texto, mejor_puntaje = texto, puntaje
    return mejor_texto


def _leer_archivo(ruta):
    """
    Lee el archivo en binario y lo decodifica con la codificación adecuada.

    Orden de intento: UTF-8 con BOM → UTF-8 → la mejor entre CP850 y CP1252.
    Los exports de TwCommentExport con caracteres en español pueden venir en
    CP850 (consola DOS) o CP1252 (Windows); se elige automáticamente la correcta.

    Args:
        ruta (str): Ruta al archivo.

    Returns:
        str: Contenido decodificado en Unicode.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    with open(ruta, "rb") as f:
        raw = f.read()

    # UTF-8 con BOM (export limpio, sin caracteres corruptos)
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")

    # UTF-8 puro
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass

    # CP850 o CP1252 — se elige la que recupera mejor los acentos del español
    return _mejor_decodificacion(raw)


# ── Detección de formato ──────────────────────────────────────────────────────

def _es_formato_a(contenido):
    """
    Determina si el contenido es un CSV exportado (Formato A).

    Comprueba que la primera línea contenga las columnas clave del export.

    Args:
        contenido (str): Contenido completo del archivo.

    Returns:
        bool: True si es Formato A.
    """
    primera = contenido.split("\n")[0].split("\r")[0]
    columnas = {c.strip().strip('"') for c in primera.split(",")}
    return COLUMNAS_FORMATO_A.issubset(columnas)


# ── Limpieza de texto ─────────────────────────────────────────────────────────

def _limpiar_texto(texto):
    """
    Limpia el texto de un tweet para dejarlo legible como comentario.

    Pasos:
        1. Elimina menciones (@usuario).
        2. Elimina URLs (http/https).
        3. Colapsa saltos de línea y tabulaciones en espacios.
        4. Colapsa espacios múltiples y recorta extremos.

    Args:
        texto (str): Texto crudo del tweet.

    Returns:
        str: Texto limpio.
    """
    texto = re.sub(r"@\w+", "", texto)
    texto = re.sub(r"https?://\S+", "", texto)
    texto = re.sub(r"[\r\n\t]+", " ", texto)
    texto = re.sub(r"\s{2,}", " ", texto)
    return texto.strip()


# ── Formato A: CSV exportado con separador de tabulaciones ───────────────────

def _reconstruir_registros(contenido):
    """
    Reconstruye registros completos de tweet a partir del contenido.

    TwCommentExport separa cada registro con \\t\\t\\t\\t\\t\\r\\n.
    Los tweets con saltos de línea internos generan múltiples bloques
    físicos que se reúnen hasta encontrar el inicio del siguiente tweet
    (bloque que comienza con un ID de 18-19 dígitos).

    Args:
        contenido (str): Contenido completo del archivo.

    Returns:
        list[str]: Registros completos (header + tweets) listos para parsear.
    """
    bloques   = contenido.split(_SEP_REGISTRO)
    registros = []
    buffer    = []

    for bloque in bloques:
        bs = bloque.strip()
        if not bs:
            continue
        if _INICIO_BLOQUE.match(bs) and buffer:
            registros.append("\n".join(buffer))
            buffer = [bs]
        else:
            buffer.append(bs)

    if buffer:
        registros.append("\n".join(buffer))

    return registros


def _parsear_registro(raw):
    """
    Parsea un registro completo como fila CSV.

    Maneja la envoltura en comillas dobles externas que usa el export
    (patrón: "ID,Name,...,bio"") y des-escapa comillas internas.

    Args:
        raw (str): String del registro completo (posiblemente multi-línea).

    Returns:
        list[str] | None: Lista de campos, o None si el parse falla.
    """
    # Quitar comilla externa y des-escapar comillas internas
    if raw.startswith('"'):
        raw = raw[1:]
        if raw.endswith('"'):
            raw = raw[:-1]
        raw = raw.replace('""', '"')

    try:
        return next(csv.reader(io.StringIO(raw, newline="")))
    except (StopIteration, csv.Error):
        return None


def _usa_separador_tabs(contenido):
    """
    Detecta si el archivo usa el separador de tabulaciones de TwCommentExport.
    """
    return _SEP_REGISTRO in contenido


def _procesar_formato_a_normal(contenido):
    """
    Extrae tweets de un CSV estándar UTF-8 (sin separador de tabulaciones).
    """
    reader = csv.reader(io.StringIO(contenido))
    filas  = list(reader)
    header = filas[0] if filas else []

    try:
        idx_id     = header.index("ID")
        idx_texto  = header.index("TweetText")
        idx_fecha  = header.index("TweetCreateTime")
        idx_handle = header.index("Handle")
    except ValueError as exc:
        raise ValueError(f"Columna faltante en el CSV exportado: {exc}")

    registros  = []
    desc_id    = 0
    desc_texto = 0

    for fila in filas[1:]:
        tweet_id = fila[idx_id].strip() if idx_id < len(fila) else ""
        if not _ID_TWEET.match(tweet_id):
            desc_id += 1
            continue

        texto = fila[idx_texto].strip() if idx_texto < len(fila) else ""
        texto = _limpiar_texto(texto)
        if len(texto) < LONGITUD_MINIMA:
            desc_texto += 1
            continue

        fecha   = fila[idx_fecha][:10] if idx_fecha < len(fila) and fila[idx_fecha] else FECHA_DEMO
        usuario = fila[idx_handle].strip() if idx_handle < len(fila) else ""
        registros.append({"id": tweet_id, "texto": texto, "fecha": fecha, "usuario": usuario})

    return registros, {
        "total_leidas": len(filas) - 1,
        "total_validas": len(registros),
        "total_descartadas": desc_id + desc_texto,
        "detalle_descarte": {"id_invalido_o_corto": desc_id, "texto_corto": desc_texto},
        "formato": "A (CSV estándar UTF-8)",
    }


def _procesar_formato_a(contenido):
    """
    Extrae tweets de un CSV exportado por TwCommentExport (Formato A).

    Detecta automáticamente si usa el separador de tabulaciones (raw.txt,
    CP1252) o es un CSV estándar (UTF-8) y aplica la estrategia adecuada.

    Para archivos con separador de tabulaciones:
        - ID     → fila[0]  (validado como 18-19 dígitos)
        - Handle → fila[2]
        - Texto  → fila[3]
        - Fecha  → extraída con regex del registro completo

    Args:
        contenido (str): Contenido completo del archivo.

    Returns:
        tuple[list[dict], dict]: (registros, estadísticas)
    """
    if not _usa_separador_tabs(contenido):
        return _procesar_formato_a_normal(contenido)

    registros_raw = _reconstruir_registros(contenido)

    registros  = []
    desc_id    = 0
    desc_texto = 0
    desc_parse = 0

    for raw in registros_raw[1:]:   # saltar header
        fila = _parsear_registro(raw)

        if fila is None or len(fila) < 3:
            desc_parse += 1
            continue

        tweet_id = fila[0].strip()
        if not _ID_TWEET.match(tweet_id):
            desc_id += 1
            continue

        texto = fila[3].strip() if len(fila) > 3 else ""
        texto = _limpiar_texto(texto)

        if len(texto) < LONGITUD_MINIMA:
            desc_texto += 1
            continue

        # Extraer fecha con regex del registro completo (más robusto que índice fijo)
        m_fecha = _FECHA_RE.search(raw)
        fecha   = m_fecha.group(1) if m_fecha else FECHA_DEMO

        usuario = fila[2].strip() if len(fila) > 2 else ""

        registros.append({
            "id":      tweet_id,
            "texto":   texto,
            "fecha":   fecha,
            "usuario": usuario,
        })

    estadisticas = {
        "total_leidas":      len(registros_raw) - 1,
        "total_validas":     len(registros),
        "total_descartadas": desc_id + desc_texto + desc_parse,
        "detalle_descarte": {
            "id_invalido": desc_id,
            "texto_corto": desc_texto,
            "parse_error": desc_parse,
        },
        "formato": "A (CSV exportado con separador de tabulaciones)",
    }
    return registros, estadisticas


# ── Formato B: texto crudo simple ─────────────────────────────────────────────

_RUIDO_B = [
    re.compile(r"^@\w+\s*$"),                    # mención aislada
    re.compile(r"^\d{1,2}\s+\w{3,9}\.?\s*$"),    # encabezado de fecha (ej: "16 abr")
    re.compile(r"^[·•.\-_*]+\s*$"),               # puntos o guiones solos
    re.compile(r"^https?://\S+\s*$"),              # URL sola
    re.compile(r"^\s*$"),                          # línea en blanco
    re.compile(r"^[\w\s]{1,4}\s*$"),               # texto de ≤4 caracteres
]


def _es_ruido_b(linea):
    """Determina si una línea de Formato B es ruido a descartar."""
    return any(p.match(linea) for p in _RUIDO_B)


def _procesar_formato_b(contenido):
    """
    Extrae comentarios de un archivo de texto crudo simple (Formato B).

    Asigna IDs secuenciales y la fecha del día de proceso.

    Args:
        contenido (str): Contenido completo del archivo.

    Returns:
        tuple[list[dict], dict]: (registros, estadísticas)
    """
    lineas      = contenido.splitlines()
    registros   = []
    descartadas = 0

    for linea in lineas:
        # Blindaje: si una fila de cabecera del export (o una fila cruda con sus
        # columnas) llega hasta aquí, no debe entrar como comentario.
        if "TweetText" in linea or linea.lower().startswith(
            ("id,name", "id,texto", "id,handle", '"id')
        ):
            descartadas += 1
            continue

        texto = _limpiar_texto(linea.strip())
        if _es_ruido_b(texto) or len(texto) < LONGITUD_MINIMA:
            descartadas += 1
            continue

        registros.append({
            "id":      str(len(registros) + 1),
            "texto":   texto,
            "fecha":   FECHA_DEMO,
            "usuario": "",
        })

    estadisticas = {
        "total_leidas":      len(lineas),
        "total_validas":     len(registros),
        "total_descartadas": descartadas,
        "detalle_descarte":  {"ruido_o_corto": descartadas},
        "formato":           "B (texto crudo simple)",
    }
    return registros, estadisticas


# ── Formato A2: export sin cabecera (filas que empiezan por ID de tweet) ──────

# Una línea de registro empieza por el ID de tweet seguido de tab, coma o ';'.
_INICIO_TSV = re.compile(r'^"?\d{18,19}[\t,;]')

# Igual, pero capturando el delimitador que sigue al ID.
_DELIM_TRAS_ID = re.compile(r'^"?\d{18,19}([\t,;])')


def _es_tsv_sin_cabecera(contenido):
    """
    Detecta el export sin fila de cabecera de TwCommentExport (tab, coma o punto y coma).

    Cada registro es: ID‹sep›Name‹sep›Handle‹sep›TweetText‹sep›TweetCreateTime…
    donde ‹sep› es tabulador o coma, y los tweets con saltos de línea internos
    se reparten en varias líneas físicas. No hay header ni el separador de cinco
    tabulaciones, por lo que ni _es_formato_a ni _usa_separador_tabs lo reconocen.
    Aquí se detecta por la presencia de varias líneas que empiezan con un ID de
    tweet de 18-19 dígitos seguido de un separador.

    Args:
        contenido (str): Contenido completo del archivo.

    Returns:
        bool: True si parece un export de tweets sin cabecera.
    """
    lineas = contenido.splitlines()
    con_id = sum(1 for l in lineas if _INICIO_TSV.match(l))
    return con_id >= 3



def _procesar_formato_tsv(contenido):
    """
    Extrae tweets de un export sin cabecera (tab, coma o punto y coma), detectando el separador.

    csv.reader maneja correctamente los campos entre comillas con saltos de línea
    internos, de modo que cada tweet queda en un solo registro lógico. Solo se
    conservan las filas cuyo primer campo es un ID de tweet válido; las líneas de
    continuación (bios, metadatos) no empiezan con ID y se ignoran.

        - ID     → fila[0]  (validado como 18-19 dígitos)
        - Name   → fila[1]  (se descarta: no forma parte del comentario)
        - Handle → fila[2]
        - Texto  → fila[3]  (TweetText, único contenido del comentario)
        - Fecha  → primer campo con formato AAAA-MM-DD entre fila[4] y fila[7]

    Args:
        contenido (str): Contenido completo del archivo.

    Returns:
        tuple[list[dict], dict]: (registros, estadísticas)
    """
    lineas = contenido.splitlines()

    # 1) Reconstruir registros completos: un registro nuevo empieza con un ID de
    #    tweet; las líneas de continuación (tweets/bios con saltos de línea
    #    internos) se anexan al registro actual.
    registros_raw = []
    buffer = []
    for linea in lineas:
        if _INICIO_TSV.match(linea):
            if buffer:
                registros_raw.append("\n".join(buffer))
            buffer = [linea]
        elif buffer:
            buffer.append(linea)
    if buffer:
        registros_raw.append("\n".join(buffer))

    # 2) Parsear cada registro. Algunos exports envuelven el registro completo en
    #    comillas externas con comillas internas duplicadas (""): se quita esa
    #    envoltura y se des-escapa antes de separar por el delimitador detectado
    #    (tab, coma o punto y coma según el carácter que sigue al ID).
    por_id     = {}
    desc_texto = 0

    for bruto in registros_raw:
        m = _DELIM_TRAS_ID.match(bruto)
        if not m:
            continue
        delim = m.group(1)

        registro = bruto
        if registro.startswith('"'):
            registro = registro[1:]
            if registro.endswith('"'):
                registro = registro[:-1]
            registro = registro.replace('""', '"')

        try:
            fila = next(csv.reader(io.StringIO(registro, newline=""), delimiter=delim))
        except (StopIteration, csv.Error):
            continue

        tweet_id = fila[0].strip().strip('"')
        if not _ID_TWEET.match(tweet_id) or tweet_id in por_id:
            continue

        texto = _limpiar_texto(fila[3]) if len(fila) > 3 else ""
        if len(texto) < LONGITUD_MINIMA:
            desc_texto += 1
            continue

        # Fecha: primer campo con formato de fecha tras el texto
        fecha = FECHA_DEMO
        for campo in fila[4:8]:
            mf = _FECHA_RE.search(campo or "")
            if mf:
                fecha = mf.group(1)
                break

        usuario = fila[2].strip() if len(fila) > 2 else ""
        por_id[tweet_id] = {
            "id": tweet_id, "texto": texto, "fecha": fecha, "usuario": usuario,
        }

    registros = list(por_id.values())

    estadisticas = {
        "total_leidas":      len(registros) + desc_texto,
        "total_validas":     len(registros),
        "total_descartadas": desc_texto,
        "detalle_descarte": {
            "texto_corto": desc_texto,
        },
        "formato": "A2 (export sin cabecera; tab, coma o punto y coma)",
    }
    return registros, estadisticas


# ── Pipeline principal ─────────────────────────────────────────────────────────

def procesar_archivo(ruta_entrada, ruta_salida):
    """
    Pipeline completo: detecta formato → extrae → escribe CSV de salida.

    Args:
        ruta_entrada (str): Ruta al archivo de entrada (.txt o .csv).
        ruta_salida (str):  Ruta del CSV de salida a generar.

    Returns:
        dict: Estadísticas del proceso.

    Raises:
        FileNotFoundError: Si el archivo de entrada no existe.
        ValueError: Si el CSV de Formato A no tiene las columnas esperadas.
    """
    registros, stats = _extraer_registros(ruta_entrada)
    _escribir_csv(registros, ruta_salida)
    stats["archivo_salida"] = ruta_salida
    return stats


def _extraer_registros(ruta_entrada):
    """
    Lee un archivo, detecta su formato y devuelve (registros, estadísticas).

    Args:
        ruta_entrada (str): Ruta al archivo de entrada.

    Returns:
        tuple[list[dict], dict]: comentarios extraídos y estadísticas.
    """
    contenido = _leer_archivo(ruta_entrada)

    if _es_formato_a(contenido):
        return _procesar_formato_a(contenido)
    elif _es_tsv_sin_cabecera(contenido):
        return _procesar_formato_tsv(contenido)
    else:
        return _procesar_formato_b(contenido)


def _escribir_csv(registros, ruta_salida):
    """Escribe los registros en el CSV de salida con las cuatro columnas."""
    with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["id", "texto", "fecha", "usuario"])
        escritor.writeheader()
        escritor.writerows(registros)



# ── Punto de entrada ──────────────────────────────────────────────────────────

def main():
    """Ejecuta el procesamiento y muestra el resultado en consola."""
    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else ARCHIVO_ENTRADA
    ruta_salida  = sys.argv[2] if len(sys.argv) > 2 else ARCHIVO_SALIDA

    print("=" * 60)
    print("  LIMPIAR.PY — Conversor a comentarios_x.csv")
    print("=" * 60)
    print(f"  Entrada : {ruta_entrada}")
    print(f"  Salida  : {ruta_salida}")

    try:
        stats = procesar_archivo(ruta_entrada, ruta_salida)

        print(f"\n  Formato detectado  : {stats['formato']}")
        print(f"  Registros leídos   : {stats['total_leidas']}")
        print(f"  Comentarios válidos: {stats['total_validas']}")
        print(f"  Descartados (total): {stats['total_descartadas']}")

        for motivo, n in stats.get("detalle_descarte", {}).items():
            if n > 0:
                print(f"    · {motivo}: {n}")

        print(f"\n  ✓ Listo. {stats['total_validas']} comentarios en {ruta_salida}")
        print("\n  Ahora ejecute main.py y cargue el archivo con la opción [1].")

    except FileNotFoundError as exc:
        print(f"\n  ERROR: {exc}")
        print("  Verifique que el archivo existe en el directorio del proyecto.")
        sys.exit(1)
    except ValueError as exc:
        print(f"\n  ERROR de formato: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\n  ERROR inesperado: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
