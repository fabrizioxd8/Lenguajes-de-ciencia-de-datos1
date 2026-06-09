from models.tipo_empleado import EmpleadoFijo,EmpleadoPorHora

print("== SISTEMA DE PLANILLA ==")

# Datos compartidos
try:
    nombre = input("Ingrese el nombre: ") 
    bono = float(input("Ingrese el bono: "))

    print("Seleccione el tipo de empleado: ")
    print("1. Empleado Fijo")
    print("2. Empleado por horas")
    opcion = int(input("Ingrese la opción: "))

    if opcion == 1:
        sueldo = float(input("Ingrese sueldo mensual: "))

        objEmpleado = EmpleadoFijo(nombre,bono,sueldo)

    elif opcion == 2:
        horas = float(input("Ingrese las horas: "))
        tarifa = float(input("Ingrese la tarifa: "))

        objEmpleado = EmpleadoPorHora(nombre,bono,horas,tarifa)

    else:
        print("Opción inválida")

    print("== BOLETA ==")
    print(objEmpleado.mostrar_datos())
    print(f"Sueldo Total: {objEmpleado.calculo_total()}")

except ValueError:
    print("Error en el tipo de dato")
finally:
    print("Planilla registrada")