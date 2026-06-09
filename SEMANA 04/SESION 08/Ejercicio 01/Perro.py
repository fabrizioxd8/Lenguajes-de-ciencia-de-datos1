from Animal import Animal

class Perro(Animal):
    def __init__(self,especie,edad,dueño):
        super().__init__(especie,edad)
        self.dueño = dueño