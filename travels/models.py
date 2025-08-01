from django.db import models


# Create your models here.
class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.last_name}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Code(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=10)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "VIP"
        verbose_name_plural = "VIPs"


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"


class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    passengers = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} {self.code} {self.vehicle} {self.passengers}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


class Transfer(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    hour = models.TimeField(auto_now_add=True)
    place = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} {self.hour} {self.place} {self.type} {self.sale}"

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"