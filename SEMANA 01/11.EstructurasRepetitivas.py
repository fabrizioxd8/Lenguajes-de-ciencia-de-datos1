"""
while: Se repite miesntras una condicion sea verdadera
for: 
"""
#Ejericio 01: Imprimir los número pares del 1 al 10
"""
i = 0
while (i <= 10):
    print(f"{i}")
    i = i + 2 #Contador 

#Ejericio 02: Imprimir los primero 10 numeros
for i in range(1,11,2):
 print(i)

#Ejericio 03: Imprimir las letras de la palabra Python

for i in "Python":
 print(i)
"""
#Ejericio 04: Usa el unumerate para mostrar un alista de compras

compras = ["Leche","Pan","Queso","Arroz"]

for x,y in enumerate(compras):
    print(f"{x} - {y}")
