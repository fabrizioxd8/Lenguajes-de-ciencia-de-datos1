"""
Ejercicio 04: Si un promedio sale con decimales altos, la institucion
requiere redondear hacia usando math
"""
import math

nota1 = float(input("Ingrese la nota 1: "))
nota2 = float(input("Ingrese la nota 2: "))
nota3 = float(input("Ingrese la nota 3: "))

promedio = (nota1 + nota2 + nota3) / 3
promedio_redondeado = math.ceil(promedio)

print("Promedio:", promedio)
print("Promedio redondeado:", promedio_redondeado)

"""
Ejercicio 03:para crear correos instituciones se necesita pasar el nombre de 
un estudiante a minuscula y quitar los espacios extras de las esquinas
"""
entrada = "       ESTUDIANTE JUAN peRez     "

usuario_limpio = entrada.strip().lower();

print(usuario_limpio)

"""
Ejercicio 02:Sacar la raiz cuadrada de un numero
"""
import math
import random
#variable = math.sqrt(25)
#variable = random.randint(1,10)
variable = random.choice(["cara","sello"])
print(variable)
"""
Ejercicio 01: Pedir al estudiante su nombre completo y mostrar
cuantos caracteres tiene (incluido los espacios)
"""
nombre = input("Ingrese su nombre completo: ")
cantidad = len(nombre)

print(f"Tu nombre es: {cantidad}")