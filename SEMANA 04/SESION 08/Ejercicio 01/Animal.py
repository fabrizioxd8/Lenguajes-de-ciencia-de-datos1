class Animal:
    
    def __init__(self,especie,edad):
        self.especie = especie
        self.edad = edad

    def onomotopeya(self):
        print("Animal ....")

    def caminar(self):
        pass

    def describir(self):
        print(f"Soy de la especie {self.especie} y tengo {self.edad} años")


