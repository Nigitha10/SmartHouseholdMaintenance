
from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from appliances.models import Appliance
from service_provider.models import (
    ServiceRequest,
    Notification,
    ServiceProvider,
    Offer
)


# =========================
# USER REGISTRATION
# =========================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Registration successful!"
        )

        return redirect("login")

    return render(
        request,
        "users/register.html"
    )


# =========================
# USER LOGIN
# =========================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")

            return redirect("dashboard")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

            return redirect("login")

    return render(
        request,
        "users/login.html"
    )


# =========================
# USER LOGOUT
# =========================

def user_logout(request):

    logout(request)

    return redirect("login")


# =========================
# USER DASHBOARD
# =========================

@login_required(login_url="/users/login/")
def dashboard(request):

    appliances = Appliance.objects.filter(
        owner=request.user
    )

    appliance_count = appliances.count()

    service_requests = ServiceRequest.objects.filter(
        user=request.user
    ).select_related(
        "service_provider",
        "appliance"
    ).order_by(
        "-request_date"
    )[:5]

    service_request_count = ServiceRequest.objects.filter(
        user=request.user
    ).count()

    notification_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    recent_notifications = Notification.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "dashboard.html",
        {
            "appliance_count": appliance_count,
            "service_request_count": service_request_count,
            "notification_count": notification_count,
            "recent_requests": service_requests,
            "recent_notifications": recent_notifications,
        }
    )
# =========================
# ADMIN DASHBOARD
# =========================

@login_required(login_url="/users/login/")
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    total_users = User.objects.filter(
        is_superuser=False
    ).count()

    total_appliances = Appliance.objects.count()

    total_requests = ServiceRequest.objects.count()

    total_providers = ServiceProvider.objects.count()

    service_requests = ServiceRequest.objects.select_related(
        "user",
        "service_provider",
        "appliance"
    ).order_by("-request_date")[:10]

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": total_users,
            "total_appliances": total_appliances,
            "total_requests": total_requests,
            "total_providers": total_providers,
            "service_requests": service_requests,
        }
    )


# =========================
# WARRANTY
# =========================

@login_required(login_url="/users/login/")
def warranty(request):

    appliances = Appliance.objects.filter(
        owner=request.user
    )

    today = date.today()

    for appliance in appliances:

        if appliance.warranty_expiry_date:

            days_left = (
                appliance.warranty_expiry_date - today
            ).days

            if days_left < 0:

                appliance.warranty_status = "Expired"

            elif days_left <= 30:

                appliance.warranty_status = "Expiring Soon"

            else:

                appliance.warranty_status = "Active"

        else:

            appliance.warranty_status = "Not Available"

    return render(
        request,
        "warranty.html",
        {
            "appliances": appliances,
            "today": today
        }
    )


# =========================
# ADMIN APPLIANCE LIST
# =========================

@login_required(login_url="/users/login/")
def admin_appliance_list(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    appliances = Appliance.objects.select_related(
        "owner"
    ).all().order_by("-id")

    return render(
        request,
        "admin_appliance_list.html",
        {
            "appliances": appliances
        }
    )


# =========================
# ADMIN SERVICE REQUESTS
# =========================

@login_required(login_url="/users/login/")
def admin_service_requests(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    service_requests = ServiceRequest.objects.select_related(
        "user",
        "service_provider",
        "appliance"
    ).order_by("-request_date")

    return render(
        request,
        "admin_service_requests.html",
        {
            "service_requests": service_requests
        }
    )


# =========================
# ADMIN SERVICE PROVIDERS
# =========================

@login_required(login_url="/users/login/")
def admin_service_provider_list(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    providers = ServiceProvider.objects.all().order_by("-id")

    return render(
        request,
        "admin_service_providers.html",
        {
            "providers": providers
        }
    )


# =========================
# ADMIN OFFERS
# =========================

@login_required(login_url="/users/login/")
def admin_offers(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    offers = Offer.objects.all().order_by("-id")

    return render(
        request,
        "admin_offers.html",
        {
            "offers": offers
        }
    )


# =========================
# ADMIN NOTIFICATIONS
# =========================

@login_required(login_url="/users/login/")
def admin_notifications(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    notifications = Notification.objects.select_related(
        "user"
    ).order_by("-created_at")

    total_notifications = notifications.count()

    unread_notifications = notifications.filter(
        is_read=False
    ).count()

    read_notifications = notifications.filter(
        is_read=True
    ).count()

    return render(
        request,
        "admin_notifications.html",
        {
            "notifications": notifications,
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "read_notifications": read_notifications,
        }
    )


# =========================
# ADMIN REPORTS
# =========================

@login_required(login_url="/users/login/")
def admin_reports(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    total_users = User.objects.filter(
        is_superuser=False
    ).count()

    total_appliances = Appliance.objects.count()

    total_requests = ServiceRequest.objects.count()

    total_providers = ServiceProvider.objects.count()

    completed_requests = ServiceRequest.objects.filter(
        status="Completed"
    ).count()

    pending_requests = ServiceRequest.objects.filter(
        status="Pending"
    ).count()

    accepted_requests = ServiceRequest.objects.filter(
        status="Accepted"
    ).count()

    in_progress_requests = ServiceRequest.objects.filter(
        status="In Progress"
    ).count()

    rejected_requests = ServiceRequest.objects.filter(
        status="Rejected"
    ).count()

    total_service_cost = sum(
        request.service_cost or 0
        for request in ServiceRequest.objects.all()
    )

    return render(
        request,
        "admin_reports.html",
        {
            "total_users": total_users,
            "total_appliances": total_appliances,
            "total_requests": total_requests,
            "total_providers": total_providers,
            "completed_requests": completed_requests,
            "pending_requests": pending_requests,
            "accepted_requests": accepted_requests,
            "in_progress_requests": in_progress_requests,
            "rejected_requests": rejected_requests,
            "total_service_cost": total_service_cost,
        }
    )


# =========================
# ADMIN USER LIST
# =========================

@login_required(login_url="/users/login/")
def admin_user_list(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    users = User.objects.filter(
        is_superuser=False
    ).order_by("-date_joined")

    return render(
        request,
        "admin_user_list.html",
        {
            "users": users,
        }
    )


# =========================
# MAINTENANCE COST
# =========================

@login_required(login_url="/users/login/")
def maintenance_cost(request):

    requests = ServiceRequest.objects.filter(
        user=request.user
    ).order_by("-request_date")

    total_cost = 0

    for item in requests:

        item.total_cost = (
            item.service_cost +
            item.repair_cost +
            item.spare_parts_cost +
            item.other_cost
        )

        total_cost += item.total_cost

    return render(
        request,
        "maintenance_cost.html",
        {
            "requests": requests,
            "total_cost": total_cost,
        }
    )
    # =========================
# USER OFFERS
# =========================

@login_required(login_url="/users/login/")
def user_offers(request):

    offers = Offer.objects.all().order_by("-id")

    return render(
        request,
        "user_offers.html",
        {
            "offers": offers,
        }
    )

