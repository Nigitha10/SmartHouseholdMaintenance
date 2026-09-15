from django.db import models


class Appliance(models.Model):
    APPLIANCE_TYPES = [
        ("AC", "Air Conditioner"),
        ("FRIDGE", "Refrigerator"),
        ("WASHING", "Washing Machine"),
        ("TV", "Television"),
        ("PURIFIER", "Water Purifier"),
        ("OTHER", "Other"),
    ]

    appliance_type = models.CharField(max_length=20, choices=APPLIANCE_TYPES)
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    customer_care_number = models.CharField(max_length=20, blank=True)
    purchase_date = models.DateField()
    bill = models.FileField(upload_to="bills/", blank=True, null=True)
    service_interval_months = models.PositiveIntegerField(default=6)

    warranty_start_date = models.DateField(blank=True, null=True)
    warranty_expiry_date = models.DateField(blank=True, null=True)

    last_service_date = models.DateField(blank=True, null=True)
    next_service_date = models.DateField(blank=True, null=True)
    service_type = models.CharField(max_length=100, blank=True)
    service_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.brand} - {self.model_number}"