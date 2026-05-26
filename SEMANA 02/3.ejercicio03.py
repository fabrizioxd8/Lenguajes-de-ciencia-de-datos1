"""
Crea un una lista llamada invitados. 
Pida al usuario un nombre para decirle si esta en lista o no?
"""
# INGRESO
invitados = ["Raul", "Ana", "Carlos", "Lucia", "Pedro"]
nombre = input("Ingrese un nombre: ")

# PROCESO
if nombre in invitados:
    mensaje = "Está en la lista de invitados"
else:
    mensaje = "No está en la lista de invitados"

# SALIDA
print(mensaje)