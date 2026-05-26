"""
Calculadora de promedios de notas
- Pide al usuario cuantas notas quiere ingresar, sumarlas y al final 
mostrar el promedio.
"""
cantidad = 0
suma = 0
i = 1

while cantidad < 5:

    nota = float(input(f"Ingresa la nota {i}: "))

    if nota <= 20 and nota >=0:
        cantidad +=1
        suma += nota   # suma = suma + nota
        i+=1 # i = i +1   i++
    else:

        print("Ingresa una nota válida")

promedio = suma/cantidad

print(f"La suma de notas es {suma}\nEl promedio de notas es {promedio}")


cantidad_notas = int(input("¿Cuántas notas quieres ingresar?: "))

suma_notas = 0

# OTRA OPCION

for i in range(cantidad_notas):

    nota = int(input(f"Ingresa la nota {i + 1}: "))

    suma_notas += nota



if cantidad_notas > 0:

    promedio = suma_notas // cantidad_notas

    print(f"El promedio final de las {cantidad_notas} notas es: {promedio}")

else:

    print("No se ingresaron notas para calcular un promedio.")