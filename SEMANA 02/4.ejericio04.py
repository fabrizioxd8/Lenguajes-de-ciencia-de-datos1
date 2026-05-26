"""
Conversor de unidades
(metros --> pies)
(metros --> pulgadas)
Pedir al usuario una cantidad en metros
"""
# INGRESO
CONVERSION = (3.28084,39.3701)
metros = float(input("Ingrese una cantidad en metros: "))

# PROCESO
pies = metros * CONVERSION[0]
pulgadas = metros * CONVERSION[1]

# SALIDA
print(f"{metros} metros son {pies:.2f} pies")
print(f"{metros} metros son {pulgadas:.2f} pulgadas")