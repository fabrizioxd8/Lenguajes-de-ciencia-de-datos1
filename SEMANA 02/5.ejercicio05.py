"""
SISTEMA DE LOGIN
Base de datos (diccionario dentro de una lista)
Con tres intentos se bloquea
"""
# Base de datos
bd_usuarios = [
    {"usuario":"admin","password":"1234"},
    {"usuario":"jean","password":"jean123"},
    {"usuario":"angy","password":"angy123"}
]

acceso = False
intentos = 3
print("======== LOGIN =========")

while (intentos > 0):
    user  = input("Ingrese el usuario: ")
    password = input("Ingrese su contraseña: ")

    for cuenta in bd_usuarios:
        if (cuenta["usuario"] == user and cuenta["password"]== password):
            acceso = True
            break

    if acceso:
        print(f"Bienvenido al sistema {user}")
        break
    else:
        intentos = intentos - 1 # intentos -=1
        print(f"No tiene acceso")

if (intentos == 0):
    print("Se han agotado los intentos")