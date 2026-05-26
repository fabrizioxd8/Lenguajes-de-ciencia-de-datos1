"""
Crear un programa que guarde el nombre de un producto y su precio en un diccionario.
Calcular el precio final con un IGV del 18%
"""
# INGRESO
import random

nombre_producto = input("Ingrese el producto: ")
precio_producto = float(input("Ingrese el precio: ")) 
prefijo = nombre_producto[:3].upper()
numero_aleatorio = random.randint(100,999)
codigo = f"{prefijo}-{numero_aleatorio}"

producto = {
    "codigo":codigo,
    "nombre":nombre_producto,
    "precio":precio_producto
}

# PROCESO
IGV = 0.18
precio_final = producto["precio"] * (1 + IGV)

# SALIDA
print(f"Código: {producto["codigo"]}")
print(f"Producto: {producto["nombre"]}")
print(f"Precio final: {precio_final:.2f}")