"""
reportes.py
-----------
Módulo de generación de reportes para el sistema de detección de crisis.
Produce el archivo reporte_crisis.txt con distribución de categorías,
top 5 palabras negativas y resumen de alertas.
"""

import os
from datetime import datetime


class GeneradorReportes:
    """
    Generador de reportes estadísticos del análisis de sentimiento.

    Attributes (privados):
        __directorio (str): Directorio de salida para los reportes.
    """

    _CATEGORIAS_ORDEN = [
        "muy positivo", "positivo", "neutro", "negativo", "muy negativo"
    ]

    _SIMBOLOS = {
        "muy positivo": "++",
        "positivo":     "+ ",
        "neutro":       "~ ",
        "negativo":     "- ",
        "muy negativo": "--",
    }

    def __init__(self, directorio_salida="datos_salida"):
        """
        Inicializa el generador creando el directorio si es necesario.

        Args:
            directorio_salida (str): Carpeta donde se guardan los reportes.
        """
        self.__directorio = directorio_salida
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)

    # ------------------------------------------------------------------ cálculos internos

    def __calcular_distribucion(self, datos_analizados):
        """
        Calcula conteo y porcentaje por categoría.

        Args:
            datos_analizados (list[dict]): Resultados de AnalizadorSentimiento.

        Returns:
            tuple[dict, int]: (distribución, total_comentarios)
        """
        total = len(datos_analizados)
        categorias = list(map(lambda x: x.get("categoria", "neutro"), datos_analizados))

        # Conteo manual con diccionario (sin librerías adicionales)
        conteo = {}
        for cat in categorias:
            conteo[cat] = conteo.get(cat, 0) + 1

        distribucion = {
            cat: {
                "count":      conteo.get(cat, 0),
                "porcentaje": round((conteo.get(cat, 0) / total * 100)
                                    if total > 0 else 0.0, 2),
            }
            for cat in self._CATEGORIAS_ORDEN
        }
        return distribucion, total

    def __top_palabras_negativas(self, datos_analizados, top_n=5):
        """
        Extrae las top N palabras más frecuentes en comentarios negativos.

        Filtra con filter() solo los comentarios negativos/muy negativos,
        cuenta sus palabras_clave con un diccionario y las ordena
        con sorted() y una función lambda.

        Args:
            datos_analizados (list[dict]): Comentarios con 'palabras_clave'.
            top_n (int):                   Número de palabras a retornar.

        Returns:
            list[tuple[str, int]]: Lista de (palabra, frecuencia) descendente.
        """
        negativos = list(filter(
            lambda x: x.get("categoria") in ("negativo", "muy negativo"),
            datos_analizados
        ))

        todas_palabras = []
        for item in negativos:
            todas_palabras.extend(item.get("palabras_clave", []))

        if not todas_palabras:
            return []

        # Conteo manual con diccionario
        frecuencias = {}
        for palabra in todas_palabras:
            frecuencias[palabra] = frecuencias.get(palabra, 0) + 1

        # Ordenar de mayor a menor frecuencia con sorted() + lambda
        ordenadas = sorted(frecuencias.items(),
                           key=lambda par: par[1], reverse=True)

        return ordenadas[:top_n]

    def __nivel_crisis(self, indice_porcentaje):
        """
        Clasifica el nivel de crisis a partir del porcentaje de negativos.

        Args:
            indice_porcentaje (float): % de comentarios negativos (0-100).

        Returns:
            str: Etiqueta de nivel: CRITICO, ALTO, MODERADO, NORMAL.
        """
        if indice_porcentaje >= 60:
            return "CRITICO"
        elif indice_porcentaje >= 30:
            return "ALTO"
        elif indice_porcentaje >= 10:
            return "MODERADO"   
        return "NORMAL"

    def __barra_ascii(self, porcentaje, ancho=25):
        """Genera una barra ASCII proporcional al porcentaje dado."""
        llenos = int(porcentaje / 100 * ancho)
        return "#" * llenos + "-" * (ancho - llenos)

    # ------------------------------------------------------------------ reporte principal

    def generar_reporte_crisis(self, datos_analizados, alertas,
                                nombre_archivo="reporte_crisis.txt"):
        """
        Genera el reporte completo de crisis en archivo de texto.

        Secciones del reporte:
            1. Encabezado con métricas globales.
            2. Distribución de categorías con barra ASCII.
            3. Top 5 palabras negativas más frecuentes.
            4. Resumen de alertas generadas.
            5. Top 5 comentarios con menor puntuación.

        Args:
            datos_analizados (list[dict]): Comentarios analizados.
            alertas (list[dict]):          Alertas generadas por GestorAlertas.
            nombre_archivo (str):          Nombre del archivo de salida.

        Returns:
            str: Ruta absoluta del reporte generado.
        """
        ruta = os.path.join(self.__directorio, nombre_archivo)

        distribucion, total = self.__calcular_distribucion(datos_analizados)
        top_palabras        = self.__top_palabras_negativas(datos_analizados)

        n_neg = (distribucion.get("negativo",     {}).get("count", 0)
                 + distribucion.get("muy negativo", {}).get("count", 0))
        indice_crisis = (n_neg / total * 100) if total > 0 else 0.0
        nivel         = self.__nivel_crisis(indice_crisis)

        with open(ruta, "w", encoding="utf-8") as f:

            # ── Encabezado ──────────────────────────────────────────────────
            f.write("=" * 72 + "\n")
            f.write("      REPORTE DE DETECCIÓN DE CRISIS EN REDES SOCIALES\n")
            f.write("=" * 72 + "\n")
            f.write(f"  Generado el   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Comentarios   : {total}\n")
            f.write(f"  Alertas gen.  : {len(alertas)}\n")
            f.write(f"  Indice crisis : {indice_crisis:.1f}%  ({n_neg} negativos / {total} total)\n")
            f.write(f"  Nivel crisis  : {nivel}\n")
            f.write("=" * 72 + "\n\n")

            # ── Distribución de categorías ───────────────────────────────────
            f.write("1. DISTRIBUCION DE CATEGORIAS\n")
            f.write("-" * 48 + "\n")

            for cat in self._CATEGORIAS_ORDEN:
                datos_cat = distribucion[cat]
                simbolo   = self._SIMBOLOS.get(cat, "  ")
                barra     = self.__barra_ascii(datos_cat["porcentaje"])
                f.write(
                    f"  [{simbolo}] {cat:<15}  "
                    f"{datos_cat['count']:>4} coment.  "
                    f"({datos_cat['porcentaje']:>5.1f}%)  "
                    f"|{barra}|\n"
                )

            f.write("\n")

            # ── Top 5 palabras negativas ─────────────────────────────────────
            f.write("2. TOP 5 PALABRAS NEGATIVAS MAS FRECUENTES\n")
            f.write("-" * 48 + "\n")

            if top_palabras:
                for rank, (palabra, frecuencia) in enumerate(top_palabras, start=1):
                    barra = "#" * frecuencia if frecuencia <= 30 else "#" * 30 + "+"
                    f.write(f"  {rank}. {palabra:<22}  {frecuencia:>3}x  {barra}\n")
            else:
                f.write("  No se encontraron palabras negativas en los comentarios.\n")

            f.write("\n")

            # ── Resumen de alertas ───────────────────────────────────────────
            f.write("3. RESUMEN DE ALERTAS GENERADAS\n")
            f.write("-" * 48 + "\n")

            if alertas:
                for idx, alerta in enumerate(alertas[:10], start=1):
                    tipo = alerta.get("tipo", "").upper()
                    f.write(
                        f"  [{idx:02d}] {tipo:<15}  "
                        f"ID:{alerta.get('id_comentario','N/A'):<8}  "
                        f"Punt:{alerta.get('puntuacion', 0):>7.2f}  "
                        f"{alerta.get('fecha_alerta','')}\n"
                    )
                if len(alertas) > 10:
                    f.write(f"       ... y {len(alertas) - 10} alertas adicionales.\n")
            else:
                f.write("  No se generaron alertas en este análisis.\n")

            f.write("\n")

            # ── Top 5 comentarios más negativos ─────────────────────────────
            f.write("4. TOP 5 COMENTARIOS MAS NEGATIVOS\n")
            f.write("-" * 48 + "\n")

            peor_cinco = sorted(
                datos_analizados,
                key=lambda x: x.get("puntuacion", 0)
            )[:5]

            for idx, com in enumerate(peor_cinco, start=1):
                texto   = com.get("texto", "")
                recorte = (texto[:65] + "...") if len(texto) > 65 else texto
                usuario = com.get("usuario", "") or "N/A"
                f.write(f"  [{idx}] ID:{com.get('id','N/A'):<8}  "
                        f"Usuario:{usuario:<15}  "
                        f"Punt:{com.get('puntuacion', 0):>7.4f}\n")
                f.write(f"       Texto: {recorte}\n")

            f.write("\n")

            # ── Top 5 usuarios con más comentarios negativos ────────────────
            f.write("5. USUARIOS CON MAS COMENTARIOS NEGATIVOS\n")
            f.write("-" * 48 + "\n")

            # Solo comentarios negativos que tengan usuario conocido
            negativos = list(filter(
                lambda x: x.get("categoria") in ("negativo", "muy negativo")
                          and x.get("usuario"),
                datos_analizados
            ))

            # Conteo manual con diccionario
            por_usuario = {}
            for com in negativos:
                usuario = com["usuario"]
                por_usuario[usuario] = por_usuario.get(usuario, 0) + 1

            if por_usuario:
                # Ordenar de mayor a menor con sorted() + lambda
                ranking = sorted(por_usuario.items(),
                                 key=lambda par: par[1], reverse=True)[:5]
                for rank, (usuario, cantidad) in enumerate(ranking, start=1):
                    f.write(f"  {rank}. {usuario:<25} {cantidad:>3} comentario(s) negativo(s)\n")
            else:
                f.write("  (sin informacion de usuarios)\n")

            f.write("\n" + "=" * 72 + "\n")
            f.write("  FIN DEL REPORTE\n")
            f.write("=" * 72 + "\n")

        return ruta

    # ------------------------------------------------------------------ resumen consola

    def generar_resumen_consola(self, datos_analizados, alertas):
        """
        Imprime un resumen estadístico breve directamente en consola.

        Args:
            datos_analizados (list[dict]): Comentarios analizados.
            alertas (list[dict]):          Alertas generadas.
        """
        distribucion, total = self.__calcular_distribucion(datos_analizados)
        top_palabras        = self.__top_palabras_negativas(datos_analizados)

        n_neg     = (distribucion.get("negativo",     {}).get("count", 0)
                     + distribucion.get("muy negativo", {}).get("count", 0))
        idx_crisis = (n_neg / total * 100) if total > 0 else 0.0
        nivel      = self.__nivel_crisis(idx_crisis)

        print("\n" + "=" * 60)
        print("  RESUMEN DEL ANÁLISIS")
        print("=" * 60)
        print(f"  Total procesados  : {total}")
        print(f"  Alertas generadas : {len(alertas)}")
        print(f"  Índice de crisis  : {idx_crisis:.1f}%  [{nivel}]")
        print()
        print("  DISTRIBUCIÓN DE CATEGORÍAS:")
        for cat in self._CATEGORIAS_ORDEN:
            d   = distribucion[cat]
            sim = self._SIMBOLOS.get(cat, "  ")
            print(f"    [{sim}] {cat:<15}  {d['count']:>4}  ({d['porcentaje']:>5.1f}%)")
        print()
        print("  TOP 5 PALABRAS NEGATIVAS:")
        if top_palabras:
            for palabra, freq in top_palabras:
                print(f"    - {palabra:<20}  ({freq}x)")
        else:
            print("    (ninguna encontrada)")
        print("=" * 60)
