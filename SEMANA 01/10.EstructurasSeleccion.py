"""
Seleccion Simple (if)
Seleccion doble (if-else)
Selccion multiple (if-elif-else)
"""
#Ejercicio 03: Pregunta la edad y si tiene entrada. Si tiene más de 18
#               "Puede ingresar" caso contrario  

#INGRESO
edad = int(input("Ingrese su edad: "))
tiene_entrada = True
#PROCESO
if (edad >= 18 and tiene_entrada):
    mensaje = "Puede ingresar"
else:
    mensaje = "no puede ingresar"
#SALIDA
print(f"{mensaje}")


#Ejercicio 02: Crea un sistema de notas
#              si la nota es >90 es "A", >80 es "B"
#              caso contrario es "C"

nota = int(input("Introduce la nota: "))

if nota > 90:
    print ("Grado: A ")
elif nota >80:
    print ("grado B")
else:
    print("Grado C")

#Ejercicio  01: Pide un número al usuario uy dile si es positivo o negativo
num = int(input("Ingrese el número: "))

if num > 0:
    print("El número es positivo")
else:
    print("El número es negativo")

