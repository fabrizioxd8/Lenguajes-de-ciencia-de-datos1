"""
Ejercicio 04: Simule la lectura del sistema escolar donde, ocurra o no un error, siempre
se debe mostrar el mensaje "Fin de la operación"
"""
try:
    dni = int(input("Ingrese el DNI: "))
    print(f"Buscando los datos del {dni} ...")
except ValueError:
    print("Error de formato")
finally:
    print("PROCESO FINALIZADO")

"""
Ejercicio 03: Al intentar acceder a la posición de un estudiante en uan lista
por su numero de orden, Controlar el error si el número supera el tamaño de la lista
"""
estudiantes = ["Ana","Pedro","Luis"]

try:
    indice = int(input("Ingrese el número de indice 0/1/2: "))
    print(f"El alumno seleccionado es: {estudiantes[indice]}")
except IndexError:
    print("Error: Ese número no existe")
"""
Ejercicio 02: La división entre cero
"""
try:

    numerador = 10
    denominador = int(input("Ingrese un número a dividir: "))

    divi = numerador / denominador

    print(divi)
except ZeroDivisionError:
    print("Error: no debe ser cero")
except ValueError:
    print("Error: Debe ingresar un número válido")
"""
Ejercicio 01: Pedir al usuario e impedir que el programa falle si ingresa 
una letra en lugar de un número entero
"""
try:
    nota = int(input("Ingrese la nota del examen: "))
    print(f"La nota fue registrada con éxito: {nota}")
except ValueError:
    print("Error: Debe ingresar un número válido")