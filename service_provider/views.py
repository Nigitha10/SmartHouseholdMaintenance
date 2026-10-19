
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import ServiceProvider, ServiceRequest, Notification, Offer
from appliances.models import Appliance
from users.models import UserProfile
from email_utils import send_twilio_email


logger = logging.getLogger(__name__)


# --------------------------------------------------
# FIND SERVICE PROVIDERS
# --------------------------------------------------
@login_required
def service_provider_list(request):
    if request.user.is_superuser:
        return redirect("admin_service_provider_list")

    providers = ServiceProvider.objects.all()

    return render(
        request,
        "service_provider/service_provider_list.html",
        {"providers": providers}
    )


# --------------------------------------------------
# REQUEST A SERVICE - PENDING EMAIL
# --------------------------------------------------
@login_required
def request_service(request, provider_id):
    provider = get_object_or_404(
        ServiceProvider,
        id=provider_id
    )

    appliances = Appliance.objects.filter(
        owner=request.user
    )

    if request.method == "POST":
        notes = request.POST.get("notes", "")
        appliance_id = request.POST.get("appliance_id")

        appliance = get_object_or_404(
            Appliance,
            id=appliance_id,
            owner=request.user
        )

        service_request = ServiceRequest.objects.create(
            user=request.user,
            service_provider=provider,
            appliance=appliance,
            notes=notes
        )

        # Email when the request is created with Pending status
        if request.user.email:
            try:
                send_twilio_email(
                    request.user.email,
                    "Service Request Received - Smart Household Maintenance",
                    f"""
                    <h2>Service Request Received</h2>
                    <p>Hello {request.user.username},</p>
                    <p>Your service request has been submitted successfully.</p>
                    <p><b>Request ID:</b> {service_request.id}</p>
                    <p><b>Service Provider:</b> {provider.service_name}</p>
                    <p><b>Appliance:</b> {appliance}</p>
                    <p><b>Status:</b> {service_request.status}</p>
                    <p>The service provider will review your request.</p>
                    <p>Thank you for using Smart Household Maintenance.</p>
                    """
                )
            except Exception:
                logger.exception("Pending service request email failed.")

        return redirect("service_provider_list")

    return render(
        request,
        "service_provider/request_service.html",
        {
            "provider": provider,
            "appliances": appliances
        }
    )


# --------------------------------------------------
# USER'S SERVICE REQUESTS
# --------------------------------------------------
@login_required
def my_service_requests(request):
    service_requests = ServiceRequest.objects.filter(
        user=request.user
    ).order_by("-request_date")

    return render(
        request,
        "service_provider/my_service_requests.html",
        {"requests": service_requests}
    )


# --------------------------------------------------
# GET MANAGER'S COMPANY
# --------------------------------------------------
def get_managed_provider(user):
    return ServiceProvider.objects.filter(
        manager=user
    ).first()


# --------------------------------------------------
# SERVICE MANAGER DASHBOARD
# --------------------------------------------------
@login_required
def service_provider_dashboard(request):
    provider = get_managed_provider(request.user)

    if provider is None:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("dashboard")

    providers = ServiceProvider.objects.filter(id=provider.id)

    all_requests = ServiceRequest.objects.filter(
        service_provider=provider
    ).order_by("-request_date")

    selected_status = request.GET.get("status", "all")

    valid_statuses = [
        "Pending",
        "Accepted",
        "In Progress",
        "Completed",
        "Rejected"
    ]

    if selected_status in valid_statuses:
        service_requests = all_requests.filter(
            status=selected_status
        )
    else:
        selected_status = "all"
        service_requests = all_requests

    return render(
        request,
        "service_provider/dashboard.html",
        {
            "providers": providers,
            "service_requests": service_requests,
            "total_requests": all_requests.count(),
            "pending_count": all_requests.filter(status="Pending").count(),
            "accepted_count": all_requests.filter(status="Accepted").count(),
            "in_progress_count": all_requests.filter(status="In Progress").count(),
            "completed_count": all_requests.filter(status="Completed").count(),
            "selected_status": selected_status,
        }
    )


# --------------------------------------------------
# UPDATE SERVICE REQUEST - STATUS EMAILS
# --------------------------------------------------
@login_required
def update_service_request(request, request_id):
    provider = get_managed_provider(request.user)

    if provider is None:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("dashboard")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        service_provider=provider
    )

    if request.method == "POST":
        old_status = service_request.status
        new_status = request.POST.get("status")

        valid_statuses = [
            "Accepted",
            "Rejected",
            "In Progress",
            "Completed"
        ]

        if new_status in valid_statuses:
            service_request.status = new_status

        service_request.service_cost = (
            request.POST.get("service_cost") or 0
        )
        service_request.repair_cost = (
            request.POST.get("repair_cost") or 0
        )
        service_request.spare_parts_cost = (
            request.POST.get("spare_parts_cost") or 0
        )
        service_request.other_cost = (
            request.POST.get("other_cost") or 0
        )

        service_request.save()

        # Send an email only when the status actually changes.
        if (
            new_status in valid_statuses
            and new_status != old_status
            and service_request.user.email
        ):
            status_messages = {
                "Accepted": (
                    "Your service request has been accepted."
                ),
                "Rejected": (
                    "Your service request has been rejected. "
                    "Please contact the service provider if you need help."
                ),
                "In Progress": (
                    "Work on your service request is now in progress."
                ),
                "Completed": (
                    "Your service request has been completed."
                ),
            }

            subject = (
                f"Service Request {new_status} - "
                "Smart Household Maintenance"
            )

            html_content = f"""
            <h2>Service Request Update</h2>
            <p>Hello {service_request.user.username},</p>
            <p>{status_messages[new_status]}</p>
            <p><b>Request ID:</b> {service_request.id}</p>
            <p><b>Service Provider:</b> {provider.service_name}</p>
            <p><b>Appliance:</b> {service_request.appliance}</p>
            <p><b>Current Status:</b> {new_status}</p>
            <p>Thank you for using Smart Household Maintenance.</p>
            """

            try:
                send_twilio_email(
                    service_request.user.email,
                    subject,
                    html_content
                )
            except Exception:
                logger.exception(
                    "Service status email failed for request %s.",
                    service_request.id
                )

        # In-app notifications when status changes.
        if new_status in valid_statuses and new_status != old_status:
            notification_messages = {
                "Accepted": (
                    f"Your {provider.service_name} service request "
                    "has been accepted."
                ),
                "Rejected": (
                    f"Your {provider.service_name} service request "
                    "has been rejected."
                ),
                "In Progress": (
                    f"Your {provider.service_name} service request "
                    "is now in progress."
                ),
                "Completed": (
                    f"Your {provider.service_name} service has been "
                    "completed. Maintenance cost has been updated."
                ),
            }

            Notification.objects.create(
                user=service_request.user,
                message=notification_messages[new_status]
            )

    return redirect("service_provider_dashboard")


# --------------------------------------------------
# NOTIFICATIONS
# --------------------------------------------------
@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    user_notifications.update(is_read=True)

    return render(
        request,
        "service_provider/notifications.html",
        {"notifications": user_notifications}
    )


# --------------------------------------------------
# ADMIN UPDATE SERVICE REQUEST
# --------------------------------------------------
@login_required
def admin_update_service_request(request, request_id):
    if not request.user.is_superuser:
        return redirect("dashboard")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id
    )

    if request.method == "POST":
        new_status = request.POST.get("status")

        valid_statuses = [
            "Pending",
            "Accepted",
            "Rejected",
            "In Progress",
            "Completed"
        ]

        if (
            new_status in valid_statuses
            and new_status != service_request.status
        ):
            old_status = service_request.status
            service_request.status = new_status
            service_request.save()

            if service_request.user.email:
                status_messages = {
                    "Pending": "Your service request is pending review.",
                    "Accepted": "Your service request has been accepted.",
                    "Rejected": "Your service request has been rejected.",
                    "In Progress": "Your service is now in progress.",
                    "Completed": "Your service has been completed.",
                }

                try:
                    send_twilio_email(
                        service_request.user.email,
                        f"Service Request {new_status} - Smart Household Maintenance",
                        f"""
                        <h2>Service Request Update</h2>
                        <p>Hello {service_request.user.username},</p>
                        <p>{status_messages[new_status]}</p>
                        <p><b>Request ID:</b> {service_request.id}</p>
                        <p><b>Status:</b> {new_status}</p>
                        <p>Thank you for using Smart Household Maintenance.</p>
                        """
                    )
                except Exception:
                    logger.exception(
                        "Admin status email failed for request %s.",
                        service_request.id
                    )

    return redirect("admin_service_requests")


# --------------------------------------------------
# COMPLETED SERVICE HISTORY
# --------------------------------------------------
@login_required
def service_history(request):
    provider = get_managed_provider(request.user)

    if provider is None:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("dashboard")

    history = ServiceRequest.objects.filter(
        service_provider=provider,
        status="Completed"
    ).select_related(
        "user",
        "service_provider",
        "appliance"
    ).order_by("-request_date")

    return render(
        request,
        "service_provider/history.html",
        {"history": history}
    )


# --------------------------------------------------
# COMPANY DETAILS FROM OFFERS PAGE
# --------------------------------------------------
@login_required
def company_detail(request, provider_id):
    provider = get_object_or_404(
        ServiceProvider,
        id=provider_id,
        is_available=True
    )

    offers = Offer.objects.filter(
        service_provider=provider,
        is_active=True
    ).order_by("-id")

    return render(
        request,
        "service_provider/company_detail.html",
        {
            "provider": provider,
            "offers": offers
        }
    )
