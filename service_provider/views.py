from django.shortcuts import render, redirect, get_object_or_404

from .models import ServiceProvider, ServiceRequest, Notification
from appliances.models import Appliance


def service_provider_list(request):
    if request.user.is_superuser:
        return redirect("admin_service_provider_list")

    providers = ServiceProvider.objects.all()

    return render(
        request,
        "service_provider/service_provider_list.html",
        {"providers": providers}
    )

def request_service(request, provider_id):
    provider = get_object_or_404(
        ServiceProvider,
        id=provider_id
    )

    # Get user's appliances
    appliances = Appliance.objects.filter(
        owner=request.user
    )

    if request.method == "POST":

        notes = request.POST.get(
            "notes",
            ""
        )

        appliance_id = request.POST.get(
            "appliance_id"
        )

        appliance = get_object_or_404(
            Appliance,
            id=appliance_id,
            owner=request.user
        )

        ServiceRequest.objects.create(
            user=request.user,
            service_provider=provider,
            appliance=appliance,
            notes=notes
        )

        return redirect(
            "service_provider_list"
        )

    return render(
        request,
        "service_provider/request_service.html",
        {
            "provider": provider,
            "appliances": appliances
        }
    )


def my_service_requests(request):
    requests = ServiceRequest.objects.filter(
        user=request.user
    ).order_by("-request_date")

    return render(
        request,
        "service_provider/my_service_requests.html",
        {"requests": requests}
    )

def service_provider_dashboard(request):

    providers = ServiceProvider.objects.all()

    # All service requests
    all_requests = ServiceRequest.objects.all().order_by(
        "-request_date"
    )

    # Status filter
    selected_status = request.GET.get("status", "all")

    if selected_status in [
        "Pending",
        "Accepted",
        "In Progress",
        "Completed"
    ]:
        service_requests = all_requests.filter(
            status=selected_status
        )
    else:
        service_requests = all_requests

    # Status-wise counts
    total_requests = all_requests.count()

    pending_count = all_requests.filter(
        status="Pending"
    ).count()

    accepted_count = all_requests.filter(
        status="Accepted"
    ).count()

    in_progress_count = all_requests.filter(
        status="In Progress"
    ).count()

    completed_count = all_requests.filter(
        status="Completed"
    ).count()

    return render(
        request,
        "service_provider/dashboard.html",
        {
            "providers": providers,
            "service_requests": service_requests,

            "total_requests": total_requests,
            "pending_count": pending_count,
            "accepted_count": accepted_count,
            "in_progress_count": in_progress_count,
            "completed_count": completed_count,

            "selected_status": selected_status,
        }
    )

def update_service_request(request, request_id):

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id
    )

    if request.method == "POST":

        new_status = request.POST.get("status")

        # Update service status
        if new_status in [
            "Accepted",
            "Rejected",
            "In Progress",
            "Completed"
        ]:

            service_request.status = new_status

        # Update actual maintenance costs
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

        # Notification
        if new_status == "Accepted":

            message = (
                f"Your "
                f"{service_request.service_provider.service_name} "
                "service request has been accepted."
            )

            Notification.objects.create(
                user=service_request.user,
                message=message
            )

        elif new_status == "Rejected":

            message = (
                f"Your "
                f"{service_request.service_provider.service_name} "
                "service request has been rejected."
            )

            Notification.objects.create(
                user=service_request.user,
                message=message
            )

        elif new_status == "Completed":

            message = (
                f"Your "
                f"{service_request.service_provider.service_name} "
                "service has been completed. "
                "Maintenance cost has been updated."
            )

            Notification.objects.create(
                user=service_request.user,
                message=message
            )

    return redirect(
        "service_provider_dashboard"
    )

def notifications(request):

    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    user_notifications.update(is_read=True)

    return render(
        request,
        "service_provider/notifications.html",
        {
            "notifications": user_notifications
        }
    )
def admin_update_service_request(request, request_id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id
    )

    if request.method == "POST":

        new_status = request.POST.get("status")

        if new_status in [
            "Pending",
            "Accepted",
            "Rejected",
            "In Progress",
            "Completed"
        ]:
            service_request.status = new_status
            service_request.save()

    return redirect("admin_service_requests")
def service_history(request):

    service_requests = ServiceRequest.objects.filter(
        service_provider__isnull=False,
        status="Completed"
    ).select_related(
        "user",
        "service_provider",
        "appliance"
    ).order_by("-request_date")

    return render(
        request,
        "service_provider/history.html",
        {
            "service_requests": service_requests
        }
    )