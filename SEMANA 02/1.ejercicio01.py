"""
Pedir al usuario que ingrese una oración.
El programa de devolver:
    - La oración en mayusculas
    - Cuántas palabras tiene 
    - Cuál es el último caracter de la oración
"""
# INGRESO
oracion = input("Ingrese una oración: ")

# PROCESO

oracion_mayuscula = oracion.upper()
cantidad_palabras = len(oracion.split())
ultimo_caracter = oracion[-1] if len(oracion) > 0 else "Ninguno (oración vacía)"

# SALIDA

print("--- RESULTADOS ---")
print(f"La oración en mayúsculas: {oracion_mayuscula}")
print(f"Cantidad de palabras: {cantidad_palabras}")
print(f"Último carácter: '{ultimo_caracter}'")