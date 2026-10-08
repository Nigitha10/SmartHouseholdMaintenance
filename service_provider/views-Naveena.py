from django.shortcuts import render, redirect, get_object_or_404

from .models import ServiceProvider, ServiceRequest, Notification
from appliances.models import Appliance


# ---------------------------------------------------------
# SERVICE PROVIDER LIST
# ---------------------------------------------------------
def service_provider_list(request):

    if request.user.is_superuser:
        return redirect("admin_service_provider_list")

    providers = ServiceProvider.objects.all()

    return render(
        request,
        "service_provider/service_provider_list.html",
        {
            "providers": providers
        }
    )


# ---------------------------------------------------------
# REQUEST SERVICE
# ---------------------------------------------------------
def request_service(request, provider_id):

    provider = get_object_or_404(
        ServiceProvider,
        id=provider_id
    )

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


# ---------------------------------------------------------
# MY SERVICE REQUESTS
# ---------------------------------------------------------
def my_service_requests(request):

    requests = ServiceRequest.objects.filter(
        user=request.user
    ).order_by(
        "-request_date"
    )

    return render(
        request,
        "service_provider/my_service_requests.html",
        {
            "requests": requests
        }
    )


# ---------------------------------------------------------
# SERVICE PROVIDER DASHBOARD
# ---------------------------------------------------------

def service_provider_dashboard(request):

    providers = ServiceProvider.objects.all()

    selected_status = request.GET.get("status", "all")

    all_requests = ServiceRequest.objects.all().order_by(
        "-request_date"
    )

    if selected_status != "all":
        service_requests = all_requests.filter(
            status=selected_status
        )
    else:
        service_requests = all_requests

    # Calculate total cost for each request
    for item in service_requests:
        item.total_cost = (
            item.service_cost +
            item.repair_cost +
            item.spare_parts_cost +
            item.other_cost
        )

    pending_count = ServiceRequest.objects.filter(
        status="Pending"
    ).count()

    accepted_count = ServiceRequest.objects.filter(
        status="Accepted"
    ).count()

    in_progress_count = ServiceRequest.objects.filter(
        status="In Progress"
    ).count()

    completed_count = ServiceRequest.objects.filter(
        status="Completed"
    ).count()

    return render(
        request,
        "service_provider/dashboard.html",
        {
            "providers": providers,
            "service_requests": service_requests,
            "pending_count": pending_count,
            "accepted_count": accepted_count,
            "in_progress_count": in_progress_count,
            "completed_count": completed_count,
            "selected_status": selected_status,
        }
    )

# ---------------------------------------------------------
# UPDATE SERVICE REQUEST
# ---------------------------------------------------------
def update_service_request(request, request_id):

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id
    )

    if request.method == "POST":

        # -----------------------------
        # STATUS UPDATE
        # -----------------------------
        new_status = request.POST.get(
            "status"
        )

        if new_status in [
            "Accepted",
            "Rejected",
            "In Progress",
            "Completed"
        ]:
            service_request.status = new_status

        # -----------------------------
        # COST UPDATE
        # -----------------------------
        # Only update cost if the field
        # is actually present in POST.
        # This prevents old costs from
        # becoming 0 accidentally.
        # -----------------------------

        if "service_cost" in request.POST:
            service_request.service_cost = (
                request.POST.get("service_cost") or 0
            )

        if "repair_cost" in request.POST:
            service_request.repair_cost = (
                request.POST.get("repair_cost") or 0
            )

        if "spare_parts_cost" in request.POST:
            service_request.spare_parts_cost = (
                request.POST.get("spare_parts_cost") or 0
            )

        if "other_cost" in request.POST:
            service_request.other_cost = (
                request.POST.get("other_cost") or 0
            )

        service_request.save()

        # -----------------------------
        # ACCEPTED NOTIFICATION
        # -----------------------------
        if new_status == "Accepted":

            message = (
                f"Your "
                f"{service_request.service_provider.service_name} "
                f"service request has been accepted."
            )

            Notification.objects.create(
                user=service_request.user,
                message=message
            )

        # -----------------------------
        # REJECTED NOTIFICATION
        # -----------------------------
        elif new_status == "Rejected":

            message = (
                f"Your "
                f"{service_request.service_provider.service_name} "
                f"service request has been rejected."
            )

            Notification.objects.create(
                user=service_request.user,
                message=message
            )

        # -----------------------------
        # COMPLETED NOTIFICATION
        # -----------------------------
        elif new_status == "Completed":

            message = (
                f"Your "
                f"{service_request.service_provider.service_name} "
                f"service has been completed. "
                f"Maintenance cost has been updated."
            )

            Notification.objects.create(
                user=service_request.user,
                message=message
            )

    return redirect(
        "service_provider_dashboard"
    )


# ---------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------
def notifications(request):

    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "service_provider/notifications.html",
        {
            "notifications": user_notifications
        }
    )


# ---------------------------------------------------------
# SERVICE HISTORY
# ---------------------------------------------------------
def service_history(request):

    history = ServiceRequest.objects.filter(
        user=request.user,
        status="Completed"
    ).order_by(
        "-request_date"
    )

    return render(
        request,
        "service_provider/history.html",
        {
            "history": history
        }
    )


# ---------------------------------------------------------
# ADMIN UPDATE SERVICE REQUEST
# ---------------------------------------------------------
def admin_update_service_request(
    request,
    request_id
):

    if not request.user.is_superuser:
        return redirect(
            "dashboard"
        )

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        if new_status in [
            "Pending",
            "Accepted",
            "Rejected",
            "In Progress",
            "Completed"
        ]:

            service_request.status = new_status

            service_request.save()

    return redirect(
        "admin_service_requests"
    )