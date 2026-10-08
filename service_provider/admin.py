from django.contrib import admin
from .models import ServiceProvider, ServiceRequest, Notification


admin.site.register(ServiceProvider)
admin.site.register(ServiceRequest)
admin.site.register(Notification)
from .models import Offer

admin.site.register(Offer)