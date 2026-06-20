"""
alertas.py
----------
Módulo de alertas para el sistema de detección de crisis en redes sociales.
Lanza una alerta cuando la puntuación de un comentario supera un umbral
negativo configurable, o cuando el porcentaje global de negativos supera
un umbral de crisis.
"""

from datetime import datetime


class GestorAlertas:
    """
    Gestor de alertas basado en umbrales configurables.

    Genera alertas individuales por comentario y alertas globales cuando
    el porcentaje de comentarios negativos supera un umbral de crisis.

    Attributes (privados):
        __umbral (float):             Puntuación por debajo de la cual se alerta.
        __porcentaje_crisis (float):  % de negativos para alerta de crisis global.
        __alertas (list):             Historial de alertas de la sesión.
    """

    TIPO_INDIVIDUAL = "individual"
    TIPO_GLOBAL     = "crisis_global"

    def __init__(self, umbral=-2.0, porcentaje_crisis=30.0):
        """
        Inicializa el gestor con umbrales configurables.

        Args:
            umbral (float):            Puntuación normalizada que dispara alerta.
                                       Debe ser un valor negativo (ej: -2.0).
            porcentaje_crisis (float): Porcentaje mínimo de negativos para
                                       disparar la alerta global (0-100).
        """
        self.__umbral = umbral
        self.__porcentaje_crisis = porcentaje_crisis
        self.__alertas = []

    # ------------------------------------------------------------------ accesores

    def obtener_umbral(self):
        """Retorna el umbral individual configurado."""
        return self.__umbral

    def configurar_umbral(self, nuevo_umbral):
        """
        Actualiza el umbral de alertas individuales.

        Args:
            nuevo_umbral (float): Nuevo valor de umbral (negativo recomendado).
        """
        self.__umbral = nuevo_umbral

    def obtener_alertas(self):
        """Retorna una copia de la lista de alertas generadas en la sesión."""
        return list(self.__alertas)

    def total_alertas(self):
        """Retorna el número de alertas generadas en la sesión."""
        return len(self.__alertas)

    # ------------------------------------------------------------------ generación

    def __construir_alerta(self, id_comentario, texto, puntuacion, tipo, usuario=""):
        """
        Construye el diccionario de una alerta.

        Args:
            id_comentario (str): Identificador del comentario origen.
            texto (str):         Texto resumido de la alerta.
            puntuacion (float):  Puntuación o índice que disparó la alerta.
            tipo (str):          TIPO_INDIVIDUAL o TIPO_GLOBAL.
            usuario (str):       Autor del comentario (vacío si no se conoce).

        Returns:
            dict: Alerta lista para persistir.
        """
        return {
            "id_comentario": id_comentario,
            "texto":         texto,
            "usuario":       usuario,
            "puntuacion":    puntuacion,
            "umbral":        self.__umbral,
            "fecha_alerta":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo":          tipo,
            "activa":        True,
        }

    def verificar_comentario(self, comentario):
        """
        Verifica si un comentario supera el umbral negativo y genera alerta.

        Args:
            comentario (dict): Comentario analizado con clave 'puntuacion'.

        Returns:
            dict | None: Alerta generada, o None si no se superó el umbral.
        """
        puntuacion = comentario.get("puntuacion", 0)

        if puntuacion < self.__umbral:
            alerta = self.__construir_alerta(
                id_comentario=comentario.get("id", "N/A"),
                texto=comentario.get("texto", ""),
                puntuacion=puntuacion,
                tipo=self.TIPO_INDIVIDUAL,
                usuario=comentario.get("usuario", ""),
            )
            self.__alertas.append(alerta)
            return alerta

        return None

    def verificar_crisis_global(self, estadisticas, total_comentarios):
        """
        Verifica si el porcentaje global de negativos supera el umbral de crisis.

        Args:
            estadisticas (dict):      Distribución de categorías (de AnalizadorSentimiento).
            total_comentarios (int):  Número total de comentarios analizados.

        Returns:
            dict | None: Alerta de crisis global, o None si no aplica.
        """
        if total_comentarios == 0:
            return None

        n_negativos    = estadisticas.get("negativo",     {}).get("count", 0)
        n_muy_negativos = estadisticas.get("muy negativo", {}).get("count", 0)
        total_neg = n_negativos + n_muy_negativos

        porcentaje = (total_neg / total_comentarios) * 100

        if porcentaje >= self.__porcentaje_crisis:
            mensaje = (
                f"Crisis detectada: {porcentaje:.1f}% de comentarios negativos "
                f"({total_neg}/{total_comentarios})"
            )
            alerta = self.__construir_alerta(
                id_comentario="GLOBAL",
                texto=mensaje,
                puntuacion=porcentaje,
                tipo=self.TIPO_GLOBAL,
            )
            self.__alertas.append(alerta)
            return alerta

        return None

    # ------------------------------------------------------------------ proceso masivo

    def procesar_lote(self, datos_analizados):
        """
        Evalúa cada comentario del lote y genera alertas individuales.

        Muestra en consola cada alerta detectada con formato destacado.

        Args:
            datos_analizados (list[dict]): Resultados de AnalizadorSentimiento.

        Returns:
            list[dict]: Alertas individuales generadas en este lote.
        """
        nuevas = []

        for comentario in datos_analizados:
            alerta = self.verificar_comentario(comentario)
            if alerta:
                nuevas.append(alerta)
                self.__mostrar_alerta_consola(alerta)

        return nuevas

    # ------------------------------------------------------------------ salida

    def __mostrar_alerta_consola(self, alerta):
        """
        Imprime una alerta con formato visual destacado en consola.

        Args:
            alerta (dict): Alerta a mostrar.
        """
        sep = "!" * 62
        tipo = alerta["tipo"].upper().replace("_", " ")
        texto_corto = alerta["texto"][:70] + ("..." if len(alerta["texto"]) > 70 else "")

        print(f"\n{sep}")
        print(f"  *** ALERTA {tipo} ***")
        print(f"{sep}")
        print(f"  ID comentario : {alerta['id_comentario']}")
        if alerta.get("usuario"):
            print(f"  Usuario       : {alerta['usuario']}")
        print(f"  Puntuacion    : {alerta['puntuacion']:.4f}  (umbral: {alerta['umbral']})")
        print(f"  Mensaje       : {texto_corto}")
        print(f"  Fecha         : {alerta['fecha_alerta']}")
        print(f"{sep}\n")
