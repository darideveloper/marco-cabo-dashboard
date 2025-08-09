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
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    email = models.EmailField(verbose_name="Correo")
    phone = models.CharField(max_length=15, verbose_name="Teléfono")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return f"{self.email}"

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
    vip_code = models.ForeignKey(
        VipCode, on_delete=models.CASCADE, verbose_name="Código VIP"
    )
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, verbose_name="Vehículo"
    )
    passengers = models.IntegerField(verbose_name="Pasajeros")
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, verbose_name="Tipo de Servicio"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    @property
    def total(self):
        return 0

    def __str__(self):
        return f"{self.client} - {self.vehicle.name} - {self.created_at}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


class Transfer(models.Model):
    TRANSFER_TYPE = (
        ("Departure", "Departure"),
        ("Arrival", "Arrival"),
    )
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    hour = models.TimeField(auto_now_add=False, verbose_name="Hora")
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Ubicación"
    )
    type = models.CharField(max_length=100, choices=TRANSFER_TYPE, default="Departure")
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
        return f"{self.date} - {self.location} - {self.type}"

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
    transfer_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, verbose_name="Tipo de Servicio"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    def __str__(self):
        return f"{self.location} - {self.price}"

    class Meta:
        verbose_name = "Precio"
        verbose_name_plural = "Precios"


class SaleDetail(Transfer):
    class Meta:
        proxy = True
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"

    @property
    def client_full_name(self):
        return f"{self.sale.client.name} {self.sale.client.last_name}"

    @property
    def vehicle_type(self):
        return self.sale.vehicle.type

    @property
    def passengers(self):
        return self.sale.passengers

    @property
    def has_vip_code(self):
        return self.sale.vip_code is not None

    def __str__(self):
        text = f"Servicio de {self.client_full_name} en "
        text += f"{self.location} a las {self.hour}"
        return text
