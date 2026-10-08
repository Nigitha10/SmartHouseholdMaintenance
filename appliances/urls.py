from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_appliance, name="add_appliance"),
    path("service/", views.service, name="service"),
    path("history/", views.history, name="history"),
    path("maintenance-cost/", views.maintenance_cost, name="maintenance_cost"),
    path("health-score/", views.health_score, name="health_score"),
    path("ai-assistant/", views.ai_assistant, name="ai_assistant"),
    path("reminders/", views.reminders, name="reminders"),
    path("qr-codes/", views.qr_codes, name="qr_codes"),
    path("", views.appliance_list, name="appliance_list"),
    path("<int:pk>/", views.appliance_detail, name="appliance_detail"),
    path("<int:pk>/edit/", views.edit_appliance, name="edit_appliance"),
]