"""
Ejercicio 02: diseñar una funcion que reciba una nota y devuelva "APROBADO"
si es mayor o igual que 11
"""
def evaluar_nota(nota):
    if nota >= 11:
        return "APROBADO"
    else:
        return "DESAPROBADO"

"""
Ejercicio 01: crear una funcion que calceule el área de
un triángulo
"""
def area_triangulo(base, altura):
    area = (base * altura) / 2
    print(f"El área es: {area}")

area_triangulo(4,7)

##############################################################33

def saludar(ex,y):
    return f"Hola {ex}, {y}, bienvenido a clase"

print(saludar("Jean","Luis"))

