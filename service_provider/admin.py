from django.contrib import admin
from .models import (
    ServiceProvider,
    ServiceRequest,
    Notification,
    Offer
)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "service_name",
        "manager",
        "price",
        "discount",
        "is_available",
    )

    list_filter = (
        "is_available",
        "service_name",
    )

    search_fields = (
        "company_name",
        "owner_name",
        "service_name",
        "manager__username",
        "manager__email",
    )


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "service_provider",
        "appliance",
        "status",
        "request_date",
        "service_cost",
    )

    list_filter = (
        "status",
        "service_provider",
    )

    search_fields = (
        "user__username",
        "service_provider__company_name",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "message",
        "created_at",
        "is_read",
    )

    list_filter = (
        "is_read",
    )

    search_fields = (
        "user__username",
        "message",
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "service_provider",
        "discount_percentage",
        "valid_from",
        "valid_until",
        "is_active",
    )

    list_filter = (
        "is_active",
        "service_provider",
    )

    search_fields = (
        "title",
        "description",
        "service_provider__company_name",
    )
list_display = (
"title",
"service_provider",
"discount_percentage",
"valid_from",
"valid_until",
"is_active",
)


list_filter = (
    "is_active",
    "service_provider",
)

search_fields = (
    "title",
    "description",
    "service_provider__company_name",
)



