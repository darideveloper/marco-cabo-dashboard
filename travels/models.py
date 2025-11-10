import uuid

from django.db import models


class Zone(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"

    @property
    def locations(self):
        locations_match = Location.objects.filter(zone=self)
        return locations_match


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="Zona")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        unique_together = ("name", "zone")


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(
        max_length=100,
        verbose_name="Apellido",
        null=True,
        blank=True,
    )
    email = models.EmailField(verbose_name="Correo")
    phone = models.CharField(
        max_length=15,
        verbose_name="Teléfono",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return f"{self.email} - {self.phone}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class VipCode(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=10, unique=True, verbose_name="Código")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "VIP"
        verbose_name_plural = "VIPs"


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"


class ServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tipo de Servicio"
        verbose_name_plural = "Tipos de Servicios"


class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Cliente")
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, verbose_name="Vehículo"
    )
    passengers = models.IntegerField(
        verbose_name="Pasajeros",
        null=True,
        blank=True,
    )
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, verbose_name="Tipo de Servicio"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Ubicación"
    )
    details = models.TextField(
        verbose_name="Detalles adicionales", null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )
    stripe_code = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name="Código de Venta",
        unique=True,
    )
    total = models.FloatField(verbose_name="Total")
    paid = models.BooleanField(default=False, verbose_name="Pagado")

    def __str__(self):
        return f"{self.client} - {self.vehicle.name} - {self.created_at}"

    def get_summary(self):
        summary = f"Marco Cabo {self.vehicle.name}"
        summary += f" - {self.client.email}"
        summary += f" - {self.location.zone.name}"
        summary += f" - {self.location.name}"
        summary += f" - {self.service_type.name}"
        summary += f" - {self.total} USD"

        return summary

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


class Transfer(models.Model):
    # Options
    TRANSFER_TYPE_OPTIONS = (
        ("departure", "Regreso"),
        ("arrival", "Llegada"),
    )

    # Fields
    id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name="Fecha")
    hour = models.TimeField(verbose_name="Hora")
    type = models.CharField(
        max_length=100,
        choices=TRANSFER_TYPE_OPTIONS,
        default="Departure",
        verbose_name="Tipo",
    )
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name="Venta")
    airline = models.CharField(max_length=100, verbose_name="Aerolínea")
    flight_number = models.CharField(max_length=100, verbose_name="Número de Vuelo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return f"{self.date} - {self.sale.location.name} - {self.type}"

    class Meta:
        verbose_name = "Transportación"
        verbose_name_plural = "Transportaciones"


class Pricing(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Ubicación"
    )
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, verbose_name="Vehículo"
    )
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, verbose_name="Tipo de Servicio"
    )
    price = models.FloatField(verbose_name="Precio")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return f"{self.location.name} - {self.price}"

    class Meta:
        verbose_name = "Precio"
        verbose_name_plural = "Precios"