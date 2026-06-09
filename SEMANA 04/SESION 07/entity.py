class Estudiante: 
    #Constructor inicia los atributos
    def __init__(self,nombre,t1,t2,ef):
        self.nombre = nombre
        self.t1 = t1
        self.t2 = t2
        self.ef = ef
 
    # Metodos para procesar el promedio
    def obtener_promedio(self):
        return (self.t1 + self.t2 + self.ef)/3
    
    def mostrar_reporte(self):
        print(f"El promedio de {self.nombre} es: {self.obtener_promedio():.2f}")

class Perro:
    def __init__(self,nombre,raza):
        #Atributis de instancia
        self.nombre = nombre
        self.raza = raza

objPerro01 = Perro("Laica","Bulldog")
objPerro02 = Perro("Boby","Pekines")

print(objPerro01.nombre)
print(objPerro01.raza)
#print(objPerro01)
#print(objPerro02)