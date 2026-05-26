#INGRESO
categoria = input("INGRESE LA CATEGORIA DEL ESTUDIANTE: (A/B/C/D)").upper()
promedio = float(input("INGRESE LE PROMEDIO PONDERADO"))

#PROCESO

match categoria:
    case "A":
        pension_base = 550
    case "B":
        pension_base = 500
    case "C":
        pension_base = 460
    case "D":
        pension_base = 400
    case _:
        print("Debe ser A,B,C o D")


if (0 <= promedio <= 13.999):
    porcentaje_descuento = 0.00   
elif (14.00 <= promedio <= 15.99):
    porcentaje_descuento = 0.10   
elif (16.00 <= promedio <= 17.99):
    porcentaje_descuento = 0.12   
elif (18.00 <= promedio <= 20.00):
    porcentaje_descuento = 0.15

monto_rebaja = pension_base * porcentaje_descuento
pension_nueva = pension_base - monto_rebaja

#SALIDA

print(f"Categoria: {categoria}")
print(f"Pension actual: S/. {pension_base:.2f}")