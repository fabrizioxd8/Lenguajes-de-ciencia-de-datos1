#INGRESO
Descuento = 0.11
precio_producto = 31 # Precio del producto
cantidad_unidades = int(input("cuantas unidades desea comprar? "))

#PROCESO
importe_compra = precio_producto * cantidad_unidades
importe_descuento = importe_compra * Descuento
importe_pagar = importe_compra - importe_descuento
caramelos = 2 * cantidad_unidades 

#SALIDA
print(f"""cantidades adquiridas son: {cantidad_unidades}
        El importe de descuento: {importe_descuento}
        El importe de compra: {importe_compra}
        El importe a pagar: {importe_pagar}
        Caramelos de regalo: {caramelos}""")