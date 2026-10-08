from django.urls import path
from . import views
from django.contrib.auth import authenticate, login, logout


urlpatterns = [

    path("", views.user_login, name="home"),

    path("register/", views.register, name="register"),

    path("login/", views.user_login, name="login"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.user_logout, name="logout"),
    path(
    "maintenance-cost/",
    views.maintenance_cost,
    name="maintenance_cost"
),
path(
    "offers/",
    views.user_offers,
    name="user_offers"
),

    # Admin Dashboard
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    # Admin Offers & Discounts
    path(
        "admin-offers/",
        views.admin_offers,
        name="admin_offers"
    ),
    path(
    "admin-notifications/",
    views.admin_notifications,
    name="admin_notifications"
),
path(
    "admin-reports/",
    views.admin_reports,
    name="admin_reports"
),
path(
    "admin-users/",
    views.admin_user_list,
    name="admin_user_list"
),

    # Admin Appliance Monitoring
    path(
        "admin-appliances/",
        views.admin_appliance_list,
        name="admin_appliance_list"
    ),

    # Warranty
    path(
        "warranty/",
        views.warranty,
        name="warranty"
    ),

    # Admin Service Requests
    path(
        "admin-service-requests/",
        views.admin_service_requests,
        name="admin_service_requests"
    ),

    # Admin Service Providers
    path(
        "admin-service-providers/",
        views.admin_service_provider_list,
        name="admin_service_provider_list"
    ),

]