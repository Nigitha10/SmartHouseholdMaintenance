from django.db import models
from django.contrib.auth.models import User


class Appliance(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appliances",
        null=True,
        blank=True
    )

    APPLIANCE_TYPES = [
        ("AC", "Air Conditioner"),
        ("FRIDGE", "Refrigerator"),
        ("WASHING", "Washing Machine"),
        ("TV", "Television"),
        ("PURIFIER", "Water Purifier"),
        ("OTHER", "Other"),
    ]

    appliance_type = models.CharField(
        max_length=20,
        choices=APPLIANCE_TYPES
    )

    brand = models.CharField(max_length=100)

    model_number = models.CharField(max_length=100)

    customer_care_number = models.CharField(
        max_length=20,
        blank=True
    )

    purchase_date = models.DateField()

    bill = models.FileField(
        upload_to="bills/",
        blank=True,
        null=True
    )

    service_interval_months = models.PositiveIntegerField(
        default=6
    )

    warranty_start_date = models.DateField(
        blank=True,
        null=True
    )

    warranty_expiry_date = models.DateField(
        blank=True,
        null=True
    )

    last_service_date = models.DateField(
        blank=True,
        null=True
    )

    next_service_date = models.DateField(
        blank=True,
        null=True
    )

    service_type = models.CharField(
        max_length=100,
        blank=True
    )

    service_notes = models.TextField(
        blank=True
    )
    maintenance_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)
    service_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)

    repair_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)

    spare_parts_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)

    other_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)
    health_score = models.PositiveIntegerField(
    default=100
)
    
    qr_code = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.brand} - {self.model_number}"