"""
convertir_kaggle.py
-------------------
Convierte el dataset 'NLP with Disaster Tweets' de Kaggle (train.csv)
al formato CSV que acepta el sistema: id, texto, fecha, usuario.

El dataset original trae las columnas: id, keyword, location, text, target.
Como no incluye fecha ni usuario, se asigna una fecha fija de demostración
y el usuario queda vacío.

Uso:
    python convertir_kaggle.py
"""

import csv
import os

# ── Configuración ───────────────────────────────────────────────────────────
ARCHIVO_ENTRADA = "train.csv"
ARCHIVO_SALIDA  = "kaggle_convertido.csv"
FECHA_DEMO      = "2015-08-06"   # El dataset no trae fechas; se usa una fija


def convertir(ruta_entrada, ruta_salida):
    """
    Lee el CSV de Kaggle y escribe un CSV con el formato del sistema.

    Args:
        ruta_entrada (str): Ruta al train.csv de Kaggle.
        ruta_salida (str):  Ruta del CSV convertido a generar.

    Returns:
        int: Número de filas convertidas.

    Raises:
        FileNotFoundError: Si el archivo de entrada no existe.
        ValueError: Si el CSV no tiene las columnas esperadas de Kaggle.
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_entrada}")

    convertidas = 0

    with open(ruta_entrada, "r", encoding="utf-8") as entrada:
        lector = csv.DictReader(entrada)

        # Validar que sea realmente el dataset de Kaggle
        columnas_esperadas = {"id", "text"}
        encabezados = set(lector.fieldnames or [])
        if not columnas_esperadas.issubset(encabezados):
            faltantes = columnas_esperadas - encabezados
            raise ValueError(
                f"El archivo no parece ser el train.csv de Kaggle. "
                f"Columnas faltantes: {faltantes}"
            )

        with open(ruta_salida, "w", encoding="utf-8", newline="") as salida:
            escritor = csv.DictWriter(
                salida, fieldnames=["id", "texto", "fecha", "usuario"]
            )
            escritor.writeheader()

            for fila in lector:
                registro = {
                    "id":      fila["id"].strip(),
                    "texto":   fila["text"].strip(),
                    "fecha":   FECHA_DEMO,
                    "usuario": "",   # el dataset no incluye autor
                }
                escritor.writerow(registro)
                convertidas += 1

    return convertidas


def main():
    """Ejecuta la conversión y muestra el resultado en consola."""
    print("=" * 60)
    print("  CONVERSOR: dataset Kaggle → formato del sistema")
    print("=" * 60)

    try:
        total = convertir(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)
        print(f"  Archivo de entrada : {ARCHIVO_ENTRADA}")
        print(f"  Archivo generado   : {ARCHIVO_SALIDA}")
        print(f"  Filas convertidas  : {total}")
        print("\n  Ahora ejecute main.py y cargue el archivo con la opción [1].")

    except FileNotFoundError as exc:
        print(f"  ERROR: {exc}")
        print("  Descargue train.csv desde kaggle.com/c/nlp-getting-started")
    except ValueError as exc:
        print(f"  ERROR: {exc}")


if __name__ == "__main__":
    main()
