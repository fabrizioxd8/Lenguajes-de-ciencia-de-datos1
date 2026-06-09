from entity import Estudiante

# INGRESO
nom = input("Ingrese su nombre")
t1 = float(input("Ingrese la primera nota: "))
t2 = float(input("Ingrese la segunda nota: "))
ef = float(input("Ingrese el examen final: "))

# PROCESO
objEstudiante = Estudiante(nom,t1,t2,ef)


#SALIDA
objEstudiante.mostrar_reporte()

