from django.db import models


class ServiceProvider(models.Model):
    company_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    description = models.TextField(blank=True)

    # Service details
    service_name = models.CharField(
        max_length=150,
        default="General Service"
    )

    service_description = models.TextField(
        blank=True,
        default=""
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    is_available = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.company_name


class ServiceRequest(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE
    )

    service_provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE
    )
    appliance = models.ForeignKey(
    "appliances.Appliance",
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    request_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=30,
        choices=[
            ("Pending", "Pending"),
            ("Accepted", "Accepted"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
            ("Rejected", "Rejected"),
        ],
        default="Pending"
    )

    notes = models.TextField(
        blank=True
    )

    # Actual Maintenance Cost
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

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.service_provider.service_name}"
        )


class Notification(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return (
            self.user.username
            + " - "
            + self.message
        )
class Offer(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title