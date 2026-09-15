
from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_appliance, name="add_appliance"),
    path("qr-codes/", views.qr_codes, name="qr_codes"),
    path("", views.appliance_list, name="appliance_list"),
    path("<int:pk>/", views.appliance_detail, name="appliance_detail"),
    path("<int:pk>/edit/", views.edit_appliance, name="edit_appliance"),
]