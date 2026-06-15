"""
clasificador.py
---------------
Módulo de clasificación de sentimiento para el sistema de detección de crisis.
Implementa POO con herencia, polimorfismo y encapsulación, diccionario
léxico en español y uso de map/filter sobre lotes de comentarios.
"""


class AnalizadorBase:
    """
    Clase base (superclase) de los analizadores de texto del sistema.

    Define el comportamiento común que comparten todos los analizadores.
    El método clasificar() es genérico: cada subclase lo sobreescribe
    con su propia lógica (polimorfismo).

    Attributes:
        nombre (str): Nombre descriptivo del analizador.
    """

    def __init__(self, nombre):
        """
        Inicializa el analizador base.

        Args:
            nombre (str): Nombre descriptivo del analizador.
        """
        self.nombre = nombre

    def describir(self):
        """Retorna una descripción del analizador."""
        return f"Analizador: {self.nombre}"

    def clasificar(self, texto_limpio):
        """
        Clasifica un texto. Versión genérica de la superclase:
        todo texto se considera neutro. Las subclases sobreescriben
        este método con su propia lógica (polimorfismo).

        Args:
            texto_limpio (str): Texto normalizado a clasificar.

        Returns:
            dict: Con claves 'categoria', 'puntuacion', 'puntuacion_raw'
                  y 'palabras_clave'.
        """
        return {
            "categoria":      "neutro",
            "puntuacion":     0.0,
            "puntuacion_raw": 0.0,
            "palabras_clave": [],
        }


class AnalizadorSentimiento(AnalizadorBase):
    """
    Analizador de sentimiento basado en diccionario léxico ponderado en español.

    Hereda de AnalizadorBase y sobreescribe el método clasificar()
    con la lógica de léxico ponderado (polimorfismo).

    Clasifica texto en cinco categorías: muy positivo, positivo, neutro,
    negativo y muy negativo.  Utiliza encapsulación para proteger el léxico
    y los umbrales de clasificación.

    Attributes (privados):
        __lexicon (dict):            Palabras con peso de sentimiento.
        __negadores (set):           Palabras que invierten el peso del término siguiente.
        __umbral_muy_positivo (float): Puntuación mínima para "muy positivo".
        __umbral_muy_negativo (float): Puntuación máxima para "muy negativo".
    """

    # Etiquetas públicas de categoría
    MUY_POSITIVO = "muy positivo"
    POSITIVO     = "positivo"
    NEUTRO       = "neutro"
    NEGATIVO     = "negativo"
    MUY_NEGATIVO = "muy negativo"

    _CATEGORIAS_ORDEN = [MUY_POSITIVO, POSITIVO, NEUTRO, NEGATIVO, MUY_NEGATIVO]

    # ------------------------------------------------------------------ init

    def __init__(self, umbral_muy_positivo=2.0, umbral_muy_negativo=-2.0):
        """
        Inicializa el analizador con léxico y umbrales configurables.

        Args:
            umbral_muy_positivo (float): Puntuación mínima para "muy positivo".
            umbral_muy_negativo (float): Puntuación máxima para "muy negativo".
        """
        super().__init__("Analizador de Sentimiento Léxico (español)")
        self.__umbral_muy_positivo = umbral_muy_positivo
        self.__umbral_muy_negativo = umbral_muy_negativo
        self.__negadores = {"no", "nunca", "jamás", "jamas", "ni", "tampoco", "sin"}
        self.__lexicon = self.__cargar_lexicon()

    # ------------------------------------------------------------------ léxico

    def __cargar_lexicon(self):
        """
        Construye el diccionario léxico en español con pesos de sentimiento.

        Escala de pesos:
            +3 / -3 → intensidad muy alta
            +2 / -2 → intensidad alta
            +1 / -1 → intensidad baja

        Returns:
            dict[str, float]: Mapa palabra → peso.
        """
        return {
            # ── MUY POSITIVOS (+3) ──────────────────────────────────────────
            "excelente": 3,      "magnifico": 3,       "extraordinario": 3,
            "increíble": 3,      "increible": 3,       "fantástico": 3,
            "fantastico": 3,     "maravilloso": 3,     "espectacular": 3,
            "fenomenal": 3,      "brillante": 3,       "perfecto": 3,
            "sobresaliente": 3,  "sublime": 3,         "óptimo": 3,
            "bendicion": 3,      "bendición": 3,       "gloria": 3,
            # ── POSITIVOS (+2) ──────────────────────────────────────────────
            "bueno": 2,          "bien": 2,            "genial": 2,
            "feliz": 2,          "contento": 2,        "alegre": 2,
            "satisfecho": 2,     "agradable": 2,       "positivo": 2,
            "favorable": 2,      "mejora": 2,          "beneficio": 2,
            "éxito": 2,          "exito": 2,           "logro": 2,
            "progreso": 2,       "avance": 2,          "solución": 2,
            "solucion": 2,       "recomiendo": 2,      "encantado": 2,
            "eficiente": 2,      "eficaz": 2,          "útil": 2,
            "util": 2,           "rapido": 2,          "rápido": 2,
            "madurez": 2,        "potencial": 2,       "reconocimiento": 2,
            # ── LEVEMENTE POSITIVOS (+1) ────────────────────────────────────
            "ok": 1,             "aceptable": 1,       "correcto": 1,
            "adecuado": 1,       "suficiente": 1,      "tranquilo": 1,
            "estable": 1,        "seguro": 1,          "normal": 1,
            "regular": 1,        "apropiado": 1,       "razonable": 1,
            "suerte": 1,         "discrepo": 1,
            # ── MUY NEGATIVOS (-3) ──────────────────────────────────────────
            "terrible": -3,      "horrible": -3,       "desastre": -3,
            "catastrófico": -3,  "catastrofico": -3,   "crisis": -3,
            "colapso": -3,       "fraude": -3,         "corrupción": -3,
            "corrupcion": -3,    "escándalo": -3,      "escandalo": -3,
            "caos": -3,          "tragedia": -3,       "pánico": -3,
            "panico": -3,        "devastador": -3,     "nefasto": -3,
            "catástrofe": -3,    "catastrofe": -3,     "pésimo": -3,
            "pesimo": -3,        "corrupto": -3,       "delito": -3,
            "pajero": -3,        "pajerin": -3,        "pajeri": -3,
            "pajeraso": -3,      "violador": -3,       "mierda": -3,
            "ctm": -3,           "ctmare": -3,         "hdp": -3,
            "conchadetumadre": -3, "reconchentumadre": -3, "reconchetumare": -3,
            "imbecil": -3,       "imbesil": -3,        "cojudo": -3,
            "cojudaso": -3,      "idiota": -3,         "estupido": -3,
            "delincuente": -3,   "criminal": -3,       "mafioso": -3,
            "terrorista": -3,    "asesino": -3,        "ladrón": -3,
            "ladron": -3,        "coimero": -3,        "corrupto": -3,
            "adefecio": -3,      "atorrante": -3,      "sicopata": -3,
            "gentuza": -3,       "miserable": -3,      "basura": -3,
            "impresentable": -3, "inservible": -3,     "fracasado": -3,
            "prostitucion": -3,  "puteria": -3,        "rufla": -3,
            "ruflas": -3,        "puta": -3,           "prostituta": -3,
            "violacion": -3,     "violación": -3,      "ultraje": -3,
            "rctm": -3,          "cuchmakta": -3,      "hocico": -3,
            "reconcha": -3,      "hijo": -1,
            # ── NEGATIVOS (-2) ──────────────────────────────────────────────
            "malo": -2,          "mal": -2,            "fallo": -2,
            "error": -2,         "problema": -2,       "falla": -2,
            "denuncia": -2,      "queja": -2,          "rechazo": -2,
            "protesta": -2,      "crítica": -2,        "critica": -2,
            "incidente": -2,     "accidente": -2,      "daño": -2,
            "dano": -2,          "pérdida": -2,        "perdida": -2,
            "peligro": -2,       "amenaza": -2,        "riesgo": -2,
            "violencia": -2,     "conflicto": -2,      "tensión": -2,
            "tension": -2,       "indignado": -2,      "indignante": -2,
            "inaceptable": -2,   "negligencia": -2,    "irresponsable": -2,
            "robo": -2,          "mentira": -2,        "engaño": -2,
            "engano": -2,        "calla": -2,          "callate": -2,
            "fuera": -2,         "vergüenza": -2,      "verguenza": -2,
            "preso": -2,         "cárcel": -2,         "carcel": -2,
            "inepto": -2,        "inútil": -2,         "inutil": -2,
            "hipócrita": -2,     "hipocrita": -2,      "fariseo": -2,
            "impotente": -2,     "enfermo": -2,        "ridículo": -2,
            "ridiculo": -2,      "sinvergüenza": -2,   "sinverguenza": -2,
            "esperpento": -2,    "pelele": -2,         "burro": -2,
            "salvaje": -2,       "barbaridad": -2,     "deshonra": -2,
            "humillación": -2,   "humillacion": -2,    "defraude": -2,
            "clandestino": -2,   "vendepatria": -2,    "traicion": -2,
            "traición": -2,      "saquear": -2,        "depredar": -2,
            "impune": -2,        "blindar": -2,        "mamadera": -2,
            "repartija": -2,     "cochinada": -2,      "pendejo": -2,
            "webon": -2,         "gusano": -2,         "rastrero": -2,
            "accesitario": -2,   "figureti": -2,       "chanchito": -2,
            "fregaste": -2,
            # ── LEVEMENTE NEGATIVOS (-1) ────────────────────────────────────
            "preocupante": -1,   "difícil": -1,        "dificil": -1,
            "complicado": -1,    "lento": -1,          "tardanza": -1,
            "retraso": -1,       "molestia": -1,       "incomodo": -1,
            "confusión": -1,     "confusion": -1,      "duda": -1,
            "incertidumbre": -1, "irregular": -1,      "deficiente": -1,
            "descuido": -1,      "omisión": -1,        "omision": -1,
            "decepcion": -1,     "decepción": -1,      "lamentable": -1,
            "pena": -1,          "lastima": -1,        "lástima": -1,
            "abuso": -1,         "aprovecha": -1,      "improviso": -1,
            "improvisado": -1,   "incompetente": -1,
            # ── INTENSIFICADORES ────────────────────────────────────────────
            "muy": 0.5,          "bastante": 0.5,      "extremadamente": 1.0,
            "totalmente": 0.5,   "completamente": 0.5, "absolutamente": 1.0,
            "demasiado": 0.5,    "increíblemente": 1.0, "increiblemente": 1.0,
            "siempre": 0.3,

 }

    # ------------------------------------------------------------------ accesores

    def obtener_lexicon(self):
        """Retorna una copia de solo lectura del léxico (encapsulación)."""
        return dict(self.__lexicon)

    def obtener_umbrales(self):
        """Retorna los umbrales actuales de clasificación."""
        return {
            "muy_positivo": self.__umbral_muy_positivo,
            "muy_negativo": self.__umbral_muy_negativo,
        }

    # ------------------------------------------------------------------ cálculo

    def __calcular_puntuacion(self, palabras):
        """
        Recorre la lista de palabras y acumula el peso de sentimiento.

        Maneja negadores: si una palabra negadora precede a una palabra del
        léxico, invierte el signo del peso de esa palabra.

        Args:
            palabras (list[str]): Tokens del texto limpio.

        Returns:
            float: Puntuación bruta acumulada.
        """
        puntuacion = 0.0
        i = 0
        while i < len(palabras):
            palabra = palabras[i]

            if palabra in self.__negadores and i + 1 < len(palabras):
                siguiente = palabras[i + 1]
                peso = self.__lexicon.get(siguiente, 0)
                puntuacion -= peso   # inversión semántica
                i += 2
            else:
                puntuacion += self.__lexicon.get(palabra, 0)
                i += 1

        return puntuacion

    def __determinar_categoria(self, puntuacion_norm):
        """
        Traduce la puntuación normalizada a una etiqueta de categoría.

        Args:
            puntuacion_norm (float): Puntuación en escala normalizada.

        Returns:
            str: Una de las cinco etiquetas de categoría.
        """
        if puntuacion_norm >= self.__umbral_muy_positivo:
            return self.MUY_POSITIVO
        elif puntuacion_norm > 0:
            return self.POSITIVO
        elif puntuacion_norm == 0:
            return self.NEUTRO
        elif puntuacion_norm >= self.__umbral_muy_negativo:
            return self.NEGATIVO
        else:
            return self.MUY_NEGATIVO

    # ------------------------------------------------------------------ API pública

    def clasificar(self, texto_limpio):
        """
        Clasifica el sentimiento de un texto ya normalizado.

        Sobreescribe el método genérico de AnalizadorBase con la
        lógica de léxico ponderado (polimorfismo).

        La puntuación normalizada se calcula como:
            (puntuacion_bruta / max(n_palabras, 1)) * 10

        Args:
            texto_limpio (str): Texto en minúsculas sin caracteres especiales.

        Returns:
            dict: Con claves 'categoria', 'puntuacion', 'puntuacion_raw'
                  y 'palabras_clave'.
        """
        palabras = texto_limpio.split() if texto_limpio else []

        # Palabras del léxico con peso negativo presentes en el texto
        palabras_clave = list(filter(
            lambda p: p in self.__lexicon and self.__lexicon[p] < 0,
            palabras
        ))

        puntuacion_raw = self.__calcular_puntuacion(palabras)

        n = max(len(palabras), 1)
        puntuacion_norm = round((puntuacion_raw / n) * 10, 4)

        categoria = self.__determinar_categoria(puntuacion_norm)

        return {
            "categoria":      categoria,
            "puntuacion":     puntuacion_norm,
            "puntuacion_raw": round(puntuacion_raw, 4),
            "palabras_clave": palabras_clave,
        }

    def analizar_lote(self, datos):
        """
        Analiza una lista de comentarios usando map().

        Cada elemento de la lista debe contener la clave 'texto_limpio'.
        Se añaden las claves 'categoria', 'puntuacion', 'puntuacion_raw'
        y 'palabras_clave' al diccionario original.

        Args:
            datos (list[dict]): Comentarios procesados por ingesta.

        Returns:
            list[dict]: Comentarios con resultado de análisis incorporado.
        """
        def _analizar(item):
            resultado = self.clasificar(item.get("texto_limpio", ""))
            combinado = dict(item)        # copia del comentario original
            combinado.update(resultado)   # agrega categoria, puntuacion, etc.
            return combinado

        return list(map(_analizar, datos))

    def filtrar_negativos(self, datos_analizados, umbral=-1.0):
        """
        Filtra comentarios negativos usando filter().

        Args:
            datos_analizados (list[dict]): Resultados de analizar_lote().
            umbral (float): Puntuación por debajo de la cual se incluye.

        Returns:
            list[dict]: Solo los comentarios con puntuación < umbral.
        """
        return list(filter(
            lambda item: item.get("puntuacion", 0) < umbral,
            datos_analizados
        ))

    def obtener_estadisticas(self, datos_analizados):
        """
        Calcula la distribución de categorías con conteo y porcentaje.

        Args:
            datos_analizados (list[dict]): Resultados de analizar_lote().

        Returns:
            dict: Mapa categoría → {'count': int, 'porcentaje': float}.
        """
        categorias = list(map(lambda x: x["categoria"], datos_analizados))

        # Conteo manual con diccionario (sin librerías adicionales)
        conteo = {}
        for cat in categorias:
            conteo[cat] = conteo.get(cat, 0) + 1

        total = len(datos_analizados)

        return {
            cat: {
                "count":      conteo.get(cat, 0),
                "porcentaje": round((conteo.get(cat, 0) / total * 100)
                                    if total > 0 else 0, 2),
            }
            for cat in self._CATEGORIAS_ORDEN
        }
