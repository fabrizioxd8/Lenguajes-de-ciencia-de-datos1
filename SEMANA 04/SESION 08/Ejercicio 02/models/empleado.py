class Empleado:
    def __init__(self,nombre,bono):
        self.nombre = nombre
        self.bono = bono

    def calcular_pago_final(self,sueldo_base):
        return sueldo_base + self.bono
    
    def mostrar_datos(self):
        return f"Empleado: {self.nombre}, Bono aplicado: {self.bono}"
