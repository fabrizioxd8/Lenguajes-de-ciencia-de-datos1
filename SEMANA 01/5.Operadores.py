"""
Aritmeticos: + - * /  **   %
Comparativos: = ==  !=  <  >  <=  >=  (Devuelven un true o false) 
Logicos: and (y)  or(o)   not(no)
"""
#Ejercicio 03:
usuario = False
contraseña = True
rol = True

ingresar = (usuario and contraseña)

print("Ingresar al sistema: " , ingresar)

#Ejercicio 02:
edad = 20
es_mayor = (edad >= 60)
print(f"¿Es mayor de edad? {es_mayor}")


#Ejercicio 01: Calcular el área de un círculo de radio 5
#INGRESO
radio = 5
pi = 3.1416

#PROCESO
area = pi * radio ** 2

#SALIDA
print(f"EL área del círculo es: {area}")