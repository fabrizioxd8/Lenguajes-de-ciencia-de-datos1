"""
main.py
-------
Punto de entrada del sistema modular de detección de crisis en redes sociales.
Presenta un menú interactivo de consola con manejo completo de excepciones.

Módulos utilizados:
    ingesta      → leer CSV, limpiar texto, detectar duplicados
    clasificador → AnalizadorSentimiento con léxico en español
    alertas      → GestorAlertas con umbral configurable
    persistencia → TXT, CSV, Pickle y SQLite (DML completo)
    reportes     → GeneradorReportes → reporte_crisis.txt
"""

import csv
import os
import sys
from datetime import datetime

from ingesta       import procesar_datos
from clasificador  import AnalizadorSentimiento
from alertas       import GestorAlertas
from persistencia  import GestorPersistencia
from reportes      import GeneradorReportes


# ── Configuración global ────────────────────────────────────────────────────
UMBRAL_ALERTA     = -2.0   # Puntuación que dispara alerta individual
PORCENTAJE_CRISIS = 30.0   # % de negativos que dispara alerta global
DIRECTORIO_SALIDA = "datos_salida"
DB_PATH           = "crisis.db"


# ── Utilidades de consola ───────────────────────────────────────────────────

def limpiar_pantalla():
    """Limpia la pantalla según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """Espera a que el usuario presione Enter."""
    input("\n  Presione Enter para continuar...")


def mostrar_banner():
    """Imprime el banner de bienvenida del sistema."""
    print("=" * 66)
    print("    SISTEMA DE DETECCIÓN DE CRISIS EN REDES SOCIALES")
    print("    Crisis Monitor v1.0 — Python 3.x — Solo stdlib")
    print("=" * 66)


def mostrar_menu(estado):
    """
    Muestra el menú principal con indicador del estado de sesión.

    Args:
        estado (dict): Estado compartido de la sesión activa.
    """
    limpiar_pantalla()
    mostrar_banner()

    n_datos   = len(estado.get("datos_analizados") or [])
    n_alertas = len(estado.get("alertas") or [])
    umbral    = estado.get("umbral", UMBRAL_ALERTA)

    if n_datos:
        print(f"  Sesión activa: {n_datos} comentarios | {n_alertas} alertas | umbral {umbral}")
    else:
        print(f"  Sin datos cargados | Umbral: {umbral}")

    print()
    print("  [1] Cargar y analizar archivo CSV")
    print("  [2] Ver estadísticas del análisis actual")
    print("  [3] Consultar base de datos")
    print("  [4] Gestionar alertas")
    print("  [5] Generar reporte de crisis (reporte_crisis.txt)")
    print("  [6] Exportar datos")
    print("  [7] Operaciones DML directas (demo)")
    print("  [8] Configurar umbral de alertas")
    print("  [9] Crear CSV de ejemplo")
    print("  [0] Salir")
    print("=" * 66)


# ── Opción 1: Cargar CSV ────────────────────────────────────────────────────

def opcion_cargar_csv(estado):
    """
    Lee un CSV, limpia, clasifica, detecta alertas y persiste en todos los formatos.

    Args:
        estado (dict): Estado compartido de la sesión.
    """
    print("\n── CARGAR Y ANALIZAR CSV ──────────────────────────────────")
    ruta = input("  Ruta del CSV (Enter = 'comentarios_x.csv'): ").strip()
    if not ruta:
        ruta = "comentarios_x.csv"

    try:
        # 1. Ingesta
        print(f"\n  Leyendo: {ruta}")
        datos, stats = procesar_datos(ruta)

        print(f"  Leídos          : {stats['total_original']}")
        print(f"  Únicos          : {stats['total_unicos']}")
        print(f"  Ruido descartado: {stats.get('total_ruido', 0)}")
        print(f"  Duplicados      : {stats['total_duplicados']}", end="")
        if stats["duplicados_ids"]:
            print(f"  (IDs: {', '.join(stats['duplicados_ids'])})")
        else:
            print()

        if not datos:
            print("  Sin datos válidos para analizar.")
            return

        # 2. Clasificación
        analizador     = AnalizadorSentimiento()
        datos_analizados = analizador.analizar_lote(datos)
        print(f"\n  Clasificados    : {len(datos_analizados)} comentarios")

        # 3. Alertas individuales
        gestor_alertas = GestorAlertas(
            umbral=estado.get("umbral", UMBRAL_ALERTA),
            porcentaje_crisis=PORCENTAJE_CRISIS,
        )
        alertas = gestor_alertas.procesar_lote(datos_analizados)

        # 4. Alerta de crisis global
        estadisticas = analizador.obtener_estadisticas(datos_analizados)
        alerta_global = gestor_alertas.verificar_crisis_global(
            estadisticas, len(datos_analizados)
        )
        if alerta_global:
            alertas.append(alerta_global)

        # 5. Actualizar estado de sesión
        estado["datos_analizados"] = datos_analizados
        estado["alertas"]          = alertas
        estado["estadisticas"]     = estadisticas

        print(f"  Alertas totales : {len(alertas)}")

        # 6. Persistencia automática en todos los formatos
        print("\n  Guardando en todos los formatos...")
        persistencia = GestorPersistencia(DIRECTORIO_SALIDA, DB_PATH)
        resultado    = persistencia.guardar_lote_completo(datos_analizados, alertas)

        print(f"    TXT      → {resultado['txt']}")
        print(f"    CSV neg  → {resultado['csv']}")
        print(f"    Pickle   → {resultado['pickle']}")
        print(f"    SQLite   → {resultado['sqlite_comentarios']} filas | "
              f"{resultado['sqlite_alertas']} alertas")

    except FileNotFoundError as exc:
        print(f"\n  ERROR: {exc}")
        print("  Use la opción [9] para generar un CSV de ejemplo.")
    except ValueError as exc:
        print(f"\n  ERROR de formato: {exc}")
    except RuntimeError as exc:
        print(f"\n  ERROR de persistencia: {exc}")
    except Exception as exc:
        print(f"\n  ERROR inesperado: {exc}")
    finally:
        pausar()


# ── Opción 2: Estadísticas ──────────────────────────────────────────────────

def opcion_estadisticas(estado):
    """Muestra el resumen estadístico en consola del análisis actual."""
    print("\n── ESTADÍSTICAS DEL ANÁLISIS ACTUAL ──────────────────────")

    datos   = estado.get("datos_analizados")
    alertas = estado.get("alertas", [])

    if not datos:
        print("  No hay datos cargados. Use la opción [1].")
        pausar()
        return

    try:
        generador = GeneradorReportes(DIRECTORIO_SALIDA)
        generador.generar_resumen_consola(datos, alertas)
    except Exception as exc:
        print(f"\n  ERROR: {exc}")
    finally:
        pausar()


# ── Opción 3: Consultar BD ──────────────────────────────────────────────────

def opcion_consultar_db(_estado):
    """Submenú de consultas SELECT a la base de datos SQLite."""
    while True:
        print("\n── CONSULTAR BASE DE DATOS ────────────────────────────────")
        print("  [1] Todos los comentarios (últimos 200)")
        print("  [2] Comentarios por categoría")
        print("  [3] Alertas activas")
        print("  [4] Todas las alertas")
        print("  [0] Volver")

        opcion = input("\n  Selección: ").strip()
        if opcion == "0":
            break

        try:
            persistencia = GestorPersistencia(DIRECTORIO_SALIDA, DB_PATH)
            CATS = ["muy positivo", "positivo", "neutro", "negativo", "muy negativo"]

            if opcion == "1":
                registros = persistencia.seleccionar_comentarios(limite=20)
                print(f"\n  {len(registros)} comentarios (máx. 20):\n")
                for r in registros:
                    print(f"  [{r['id_original']:<4}] {r['categoria'].upper():<15}  "
                          f"Punt:{r['puntuacion']:>6.2f}  "
                          f"{r['texto_original'][:45]}...")

            elif opcion == "2":
                for i, c in enumerate(CATS, 1):
                    print(f"  [{i}] {c}")
                idx = input("  Número de categoría: ").strip()
                if idx.isdigit() and 1 <= int(idx) <= len(CATS):
                    cat      = CATS[int(idx) - 1]
                    registros = persistencia.seleccionar_comentarios(categoria=cat)
                    print(f"\n  Categoría '{cat}': {len(registros)} registro(s)\n")
                    for r in registros[:15]:
                        print(f"  [{r['id_original']:<4}]  {r['texto_original'][:55]}...")
                else:
                    print("  Selección inválida.")

            elif opcion == "3":
                alertas = persistencia.seleccionar_alertas(solo_activas=True)
                print(f"\n  Alertas activas: {len(alertas)}\n")
                for a in alertas:
                    print(f"  ID:{a['id']:<4}  Com:{a['id_comentario']:<8}  "
                          f"Punt:{a['puntuacion']:>7.2f}  {a['fecha_alerta']}")

            elif opcion == "4":
                alertas = persistencia.seleccionar_alertas()
                print(f"\n  Total alertas: {len(alertas)}\n")
                for a in alertas[:20]:
                    estado_txt = "ACTIVA   " if a["activa"] else "RESUELTA "
                    print(f"  [{a['id']:>3}] {estado_txt}  Com:{a['id_comentario']:<8}  "
                          f"{a['fecha_alerta']}")

            else:
                print("  Opción no reconocida. Ingrese un número del 0 al 4.")

        except RuntimeError as exc:
            print(f"\n  ERROR BD: {exc}")
        except Exception as exc:
            print(f"\n  ERROR: {exc}")
        finally:
            pausar()


# ── Opción 4: Gestionar alertas ─────────────────────────────────────────────

def opcion_gestionar_alertas(estado):
    """Submenú de gestión de alertas (ver, resolver, limpiar)."""
    while True:
        print("\n── GESTIONAR ALERTAS ──────────────────────────────────────")
        print("  [1] Ver alertas de la sesión actual")
        print("  [2] Resolver alerta por ID (BD)")
        print("  [3] Limpiar alertas resueltas de la BD")
        print("  [0] Volver")

        opcion = input("\n  Selección: ").strip()
        if opcion == "0":
            break

        try:
            persistencia = GestorPersistencia(DIRECTORIO_SALIDA, DB_PATH)

            if opcion == "1":
                alertas = estado.get("alertas", [])
                if not alertas:
                    print("  No hay alertas en la sesión actual.")
                else:
                    print(f"\n  Alertas de sesión ({len(alertas)}):\n")
                    for i, a in enumerate(alertas, 1):
                        tipo = a.get("tipo", "").upper()
                        print(f"  [{i:02d}] {tipo:<15}  "
                              f"ID:{a.get('id_comentario','?'):<8}  "
                              f"Punt:{a.get('puntuacion',0):>6.2f}")

            elif opcion == "2":
                id_str = input("  ID de la alerta a resolver: ").strip()
                if id_str.isdigit():
                    n = persistencia.resolver_alerta(int(id_str))
                    print(f"  Filas actualizadas: {n}")
                else:
                    print("  ID inválido (debe ser entero).")

            elif opcion == "3":
                n = persistencia.limpiar_alertas_resueltas()
                print(f"  Alertas resueltas eliminadas: {n}")

            else:
                print("  Opción no reconocida. Ingrese un número del 0 al 3.")

        except RuntimeError as exc:
            print(f"\n  ERROR BD: {exc}")
        except Exception as exc:
            print(f"\n  ERROR: {exc}")
        finally:
            pausar()


# ── Opción 5: Generar reporte ───────────────────────────────────────────────

def opcion_generar_reporte(estado):
    """Genera el archivo reporte_crisis.txt y opcionalmente lo muestra."""
    print("\n── GENERAR REPORTE DE CRISIS ──────────────────────────────")

    datos   = estado.get("datos_analizados")
    alertas = estado.get("alertas", [])

    if not datos:
        print("  No hay datos cargados. Use la opción [1].")
        pausar()
        return

    try:
        generador = GeneradorReportes(DIRECTORIO_SALIDA)
        ruta      = generador.generar_reporte_crisis(datos, alertas)
        print(f"\n  Reporte generado: {ruta}")

        ver = input("  ¿Desea ver el reporte en consola? (s/n): ").strip().lower()
        if ver == "s":
            with open(ruta, "r", encoding="utf-8") as f:
                print("\n" + f.read())

    except Exception as exc:
        print(f"\n  ERROR al generar reporte: {exc}")
    finally:
        pausar()


# ── Opción 6: Exportar ──────────────────────────────────────────────────────

def opcion_exportar(estado):
    """Exporta datos en el formato elegido por el usuario."""
    print("\n── EXPORTAR DATOS ─────────────────────────────────────────")

    datos   = estado.get("datos_analizados")
    alertas = estado.get("alertas", [])

    if not datos:
        print("  No hay datos cargados. Use la opción [1].")
        pausar()
        return

    print("  [1] TXT completo")
    print("  [2] CSV negativos")
    print("  [3] Pickle (backup completo)")
    print("  [4] Todos los formatos")
    print("  [0] Volver")

    opcion = input("\n  Selección: ").strip()
    if opcion == "0":
        return

    try:
        persistencia = GestorPersistencia(DIRECTORIO_SALIDA, DB_PATH)
        sello = datetime.now().strftime("%Y%m%d_%H%M%S")

        if opcion == "1":
            ruta = persistencia.guardar_txt(datos, f"export_{sello}.txt")
            print(f"  Exportado: {ruta}")
        elif opcion == "2":
            ruta = persistencia.guardar_csv_filtrado(datos, nombre_archivo=f"negativos_{sello}.csv")
            print(f"  Exportado: {ruta}")
        elif opcion == "3":
            ruta = persistencia.guardar_pickle(
                {"datos": datos, "alertas": alertas},
                f"backup_{sello}.pkl"
            )
            print(f"  Exportado: {ruta}")
        elif opcion == "4":
            resultado = persistencia.guardar_lote_completo(datos, alertas)
            print(f"  TXT    → {resultado['txt']}")
            print(f"  CSV    → {resultado['csv']}")
            print(f"  Pickle → {resultado['pickle']}")
        else:
            print("  Opción inválida.")

    except RuntimeError as exc:
        print(f"\n  ERROR: {exc}")
    except Exception as exc:
        print(f"\n  ERROR inesperado: {exc}")
    finally:
        pausar()


# ── Opción 7: Demo DML ──────────────────────────────────────────────────────

def opcion_demo_dml(estado):
    """Demuestra operaciones DML directas sobre la base de datos."""
    print("\n── DEMO DML — OPERACIONES DIRECTAS ────────────────────────")

    datos = estado.get("datos_analizados")
    if not datos:
        print("  Cargue un CSV primero (opción 1).")
        pausar()
        return

    try:
        persistencia = GestorPersistencia(DIRECTORIO_SALIDA, DB_PATH)

        # INSERT individual
        primer = datos[0]
        nuevo_id = persistencia.insertar_comentario(primer)
        print(f"  INSERT individual → rowid {nuevo_id}")

        # SELECT con filtro
        comentarios = persistencia.seleccionar_comentarios(categoria="muy negativo", limite=3)
        print(f"  SELECT muy negativos → {len(comentarios)} fila(s)")

        # UPDATE
        n_upd = persistencia.actualizar_categoria(primer["id"], "neutro")
        print(f"  UPDATE categoría '{primer['id']}' → {n_upd} fila(s) afectada(s)")

        # Revertir UPDATE
        persistencia.actualizar_categoria(primer["id"], primer.get("categoria", "neutro"))

        # DELETE
        n_del = persistencia.eliminar_comentario(primer["id"])
        print(f"  DELETE id='{primer['id']}' → {n_del} fila(s) eliminada(s)")

        print("\n  Todas las operaciones DML ejecutadas correctamente.")

    except RuntimeError as exc:
        print(f"\n  ERROR BD: {exc}")
    except Exception as exc:
        print(f"\n  ERROR: {exc}")
    finally:
        pausar()


# ── Opción 8: Configurar umbral ─────────────────────────────────────────────

def opcion_configurar_umbral(estado):
    """Permite cambiar el umbral de alertas individuales."""
    print("\n── CONFIGURAR UMBRAL DE ALERTAS ───────────────────────────")
    actual = estado.get("umbral", UMBRAL_ALERTA)
    print(f"  Umbral actual   : {actual}")
    print("  Escala de uso   : -1.0 (sensible) → -4.0 (solo extremos)")

    try:
        entrada = input("  Nuevo umbral (Enter para mantener): ").strip()
        if not entrada:
            print("  Sin cambios.")
            return

        valor = float(entrada)

        if valor > 0:
            conf = input("  El umbral positivo no detectará negativos. ¿Confirmar? (s/n): ").strip()
            if conf.lower() != "s":
                print("  Cambio cancelado.")
                return

        estado["umbral"] = valor
        print(f"  Umbral actualizado a: {valor}")

    except ValueError:
        print("  Valor inválido. Introduzca un número decimal (ej: -2.5).")
    finally:
        pausar()


# ── Opción 9: Crear CSV ejemplo ─────────────────────────────────────────────

def opcion_crear_ejemplo(_estado):
    """Crea un archivo CSV de ejemplo con 16 filas (incluye 1 duplicado)."""
    ruta = "comentarios_x.csv"
    filas = [
        ["id", "texto", "fecha", "usuario"],
        ["1",  "Este servicio es absolutamente terrible, un completo desastre", "2024-01-15", "@maria_lopez"],
        ["2",  "Excelente atención al cliente, muy satisfecho con el servicio", "2024-01-15", "@jc_torres"],
        ["3",  "El producto llegó dañado, es un fraude total inaceptable",      "2024-01-16", "@ana_quispe"],
        ["4",  "Todo bien, servicio normal y correcto, sin problemas",           "2024-01-16", "@pedro_rmz"],
        ["5",  "Crisis grave en la empresa, muchos errores y negligencia",       "2024-01-17", "@maria_lopez"],
        ["6",  "Maravilloso, increíble experiencia, lo recomiendo totalmente",   "2024-01-17", "@jc_torres"],
        ["7",  "Muy mal servicio, denuncia formal por incidente grave",          "2024-01-18", "@ana_quispe"],
        ["8",  "Regular, nada especial pero tampoco hay problemas graves",       "2024-01-18", "@pedro_rmz"],
        ["9",  "Escándalo total, corrupción evidente en la gestión interna",     "2024-01-19", "@maria_lopez"],
        ["10", "Genial y fantástico, superó todas mis expectativas de éxito",    "2024-01-19", "@jc_torres"],
        ["11", "Pésimo, horrible experiencia, caos total, nunca regreso",        "2024-01-20", "@ana_quispe"],
        ["12", "Bastante bien, mejora notable respecto al mes anterior",         "2024-01-20", "@pedro_rmz"],
        ["13", "Conflicto y tensión constante, situación muy preocupante",       "2024-01-21", "@maria_lopez"],
        ["14", "Progreso evidente y avance significativo en la solución",        "2024-01-21", "@jc_torres"],
        ["15", "Caos total, no hay organización ni respuesta ante el problema",  "2024-01-22", "@ana_quispe"],
        ["16", "Este servicio es absolutamente terrible, un completo desastre",  "2024-01-22", "@pedro_rmz"],  # duplicado
    ]

    try:
        with open(ruta, "w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerows(filas)

        print(f"\n  CSV de ejemplo creado: {ruta}")
        print(f"  Filas de datos: {len(filas) - 1} (incluye 1 duplicado)")

    except OSError as exc:
        print(f"\n  ERROR al crear CSV: {exc}")
    finally:
        pausar()


# ── Función principal ───────────────────────────────────────────────────────

def main():
    """
    Punto de entrada del sistema.

    Inicializa la base de datos, presenta el menú interactivo y
    despacha las opciones seleccionadas.  El bucle principal está
    protegido con try/except/finally para garantizar un cierre limpio.
    """
    estado = {
        "datos_analizados": None,
        "alertas":          [],
        "estadisticas":     {},
        "umbral":           UMBRAL_ALERTA,
    }

    # Mapa opción → función manejadora
    manejadores = {
        "1": opcion_cargar_csv,
        "2": opcion_estadisticas,
        "3": opcion_consultar_db,
        "4": opcion_gestionar_alertas,
        "5": opcion_generar_reporte,
        "6": opcion_exportar,
        "7": opcion_demo_dml,
        "8": opcion_configurar_umbral,
        "9": opcion_crear_ejemplo,
    }

    # Inicialización del sistema
    try:
        print("\n  Inicializando sistema...")
        GestorPersistencia(DIRECTORIO_SALIDA, DB_PATH)
        print(f"  BD lista     : {DB_PATH}")
        print(f"  Salida en    : {DIRECTORIO_SALIDA}/")
        print(f"  Umbral alerta: {UMBRAL_ALERTA}")
        pausar()
    except RuntimeError as exc:
        print(f"  Advertencia al inicializar BD: {exc}")
        pausar()
    except Exception as exc:
        print(f"  Error crítico al iniciar: {exc}")
        sys.exit(1)

    # Bucle principal del menú
    while True:
        try:
            mostrar_menu(estado)
            seleccion = input("\n  Seleccione opción [0-9]: ").strip()

            if seleccion == "0":
                limpiar_pantalla()
                print("\n  Cerrando sistema. ¡Hasta luego!\n")
                break

            if seleccion in manejadores:
                manejadores[seleccion](estado)
            else:
                print("\n  Opción no reconocida. Ingrese un número del 0 al 9.")
                pausar()

        except KeyboardInterrupt:
            print("\n\n  Interrupción por teclado (Ctrl+C).")
            try:
                confirmar = input("  ¿Desea salir del sistema? (s/n): ").strip().lower()
                if confirmar == "s":
                    print("  Cerrando sistema.")
                    break
            except (KeyboardInterrupt, EOFError):
                print("\n  Saliendo forzosamente.")
                break

        except EOFError:
            print("\n  Entrada cerrada. Terminando.")
            break

        except Exception as exc:
            print(f"\n  ERROR CRITICO NO ESPERADO: {exc}")
            print("  El sistema continuará en la próxima iteración.")
            pausar()

        finally:
            # El bloque finally se ejecuta en cada iteración del bucle.
            # Se usa para tareas de limpieza opcionales por ciclo (actualmente vacío).
            pass


# ── Arranque ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
