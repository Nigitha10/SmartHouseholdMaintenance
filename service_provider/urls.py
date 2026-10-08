from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.service_provider_list,
        name="service_provider_list"
    ),

    path(
        "request/<int:provider_id>/",
        views.request_service,
        name="request_service"
    ),

    path(
        "my-requests/",
        views.my_service_requests,
        name="my_service_requests"
    ),
    path(
    "dashboard/",
    views.service_provider_dashboard,
    name="service_provider_dashboard"
),
path(
    "update-request/<int:request_id>/",
    views.update_service_request,
    name="update_service_request"
),
path(
    "notifications/",
    views.notifications,
    name="notifications"
),
path(
    "admin-update-request/<int:request_id>/",
    views.admin_update_service_request,
    name="admin_update_service_request"
),
path(
    "history/",
    views.service_history,
    name="service_history"
),
]