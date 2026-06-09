from models.empleado import Empleado
#Clase hijo 01
class EmpleadoFijo(Empleado):
    def __init__(self,nombre,bono,sueldo_mensual):
        super().__init__(nombre,bono)
        self.sueldo_mensual = sueldo_mensual

    def calculo_total(self):
        return self.calcular_pago_final(self.sueldo_mensual)

#Clase hijo 02
class EmpleadoPorHora(Empleado):
     def __init__(self,nombre,bono,horas,tarifa):
        super().__init__(nombre,bono)
        self.horas = horas
        self.tarifa = tarifa

     def calculo_total(self):
        sueldo_por_horas =  self.horas * self.tarifa
        return self.calcular_pago_final(sueldo_por_horas)