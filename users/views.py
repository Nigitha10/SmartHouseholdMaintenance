
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

from .models import UserProfile
from django.shortcuts import render, redirect, get_object_or_404

from email_utils import send_twilio_email


# =========================
# USER REGISTRATION
# =========================


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        mobile_number = request.POST.get("mobile_number", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password or not mobile_number:
            messages.error(request, "All fields are required.")
            return redirect("register")

        if not mobile_number.isdigit() or not 10 <= len(mobile_number) <= 15:
            messages.error(
                request,
                "Enter a valid mobile number using digits only."
            )
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            mobile_number=mobile_number
        )
                # Send registration welcome email
        try:
            if email:
                send_twilio_email(
                    email,
                    "Welcome to Smart Household Maintenance",
                    (
                        "<h2>Welcome to Smart Household Maintenance!</h2>"
                        f"<p>Hello {username},</p>"
                        "<p>Your registration was successful.</p>"
                        "<p>You can now log in and manage your household "
                        "appliance service requests.</p>"
                        "<p>Thank you for joining us!</p>"
                    ),
                )
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                "Registration email failed."
            )

        # SMS testing only; real SMS will not be sent yet.
       

        messages.success(
            request,
            "Registration successful! Please log in."
        )
        return redirect("login")

    return render(request, "users/register.html")



# =========================
# USER LOGIN
# =========================
# =========================
# USER LOGIN
# =========================
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

            print("LOGIN USER:", user.username)
            print("IS SUPERUSER:", user.is_superuser)

            # Check assigned service manager company
            managed_provider = ServiceProvider.objects.filter(
                manager=user
            ).first()

            print("MANAGED PROVIDER:", managed_provider)

            if user.is_superuser:
                return redirect("admin_dashboard")

            if managed_provider is not None:
                return redirect("service_provider_dashboard")

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )
        return redirect("login")

    return render(request, "users/login.html")



# =========================
# USER DASHBOARD
# =========================

@login_required
def dashboard(request):

    # Admin users should use the Admin Dashboard
    if request.user.is_superuser:
        return redirect("admin_dashboard")

    # Check whether the logged-in user manages a service company
    managed_provider = ServiceProvider.objects.filter(
        manager=request.user
    ).first()

    # Service Managers should use their own company dashboard
    if managed_provider is not None:
        return redirect("service_provider_dashboard")

    # Normal user's dashboard
    appliances = Appliance.objects.filter(
        owner=request.user
    )

    appliance_count = appliances.count()

    service_request_count = ServiceRequest.objects.filter(
        user=request.user
    ).count()

    notification_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    recent_requests = ServiceRequest.objects.filter(
        user=request.user
    ).select_related(
        "service_provider",
        "appliance"
    ).order_by("-request_date")[:5]

    recent_notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-id")[:5]

    return render(
        request,
        "dashboard.html",
        {
            "appliances": appliances,
            "appliance_count": appliance_count,
            "service_request_count": service_request_count,
            "notification_count": notification_count,
            "service_requests": recent_requests,
            "recent_requests": recent_requests,
            "recent_notifications": recent_notifications,
        }
    )




# =========================
# ADMIN DASHBOARD
# =========================
@login_required
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
@login_required
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
            "today": today,
        }
    )


# =========================
# ADMIN APPLIANCE LIST
# =========================
@login_required
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
            "appliances": appliances,
        }
    )


# =========================
# ADMIN SERVICE REQUESTS
# =========================
@login_required
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
            "service_requests": service_requests,
        }
    )


# =========================
# ADMIN SERVICE PROVIDERS
# =========================
@login_required
def admin_service_provider_list(request):
    if not request.user.is_superuser:
        return redirect("dashboard")

    providers = ServiceProvider.objects.all().order_by("-id")

    return render(
        request,
        "admin_service_providers.html",
        {
            "providers": providers,
        }
    )


# =========================
# ADMIN OFFERS
# =========================
@login_required
def admin_offers(request):
    if not request.user.is_superuser:
        return redirect("dashboard")

    offers = Offer.objects.all().order_by("-id")

    return render(
        request,
        "admin_offers.html",
        {
            "offers": offers,
        }
    )


# =========================
# ADMIN NOTIFICATIONS
# =========================
@login_required
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
@login_required
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
        service_request.service_cost or 0
        for service_request in ServiceRequest.objects.all()
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
@login_required
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
# USER LOGOUT
# =========================
def user_logout(request):
    logout(request)
    return redirect("login")
@login_required
def view_bill(request, appliance_id):
    appliance = get_object_or_404(
        Appliance,
        id=appliance_id,
        owner=request.user
    )

    if not appliance.bill:
        return redirect("warranty")

    return render(
        request,
        "view_bill.html",
        {
           "bill_url": appliance.bill.url,
            "appliance": appliance,
        }
    )
    # =========================

# =========================
# USER OFFERS
# =========================

@login_required
def user_offers(request):
    offers = Offer.objects.filter(
        is_active=True
    ).select_related(
        "service_provider"
    ).order_by("-id")

    return render(
        request,
        "user_offers.html",
        {"offers": offers}
    )
# =========================
# USER PROFILE
# =========================

@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        mobile_number = request.POST.get("mobile_number", "").strip()

        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        errors = []

        if not first_name:
            errors.append("Please enter your first name.")

        if not email:
            errors.append("Please enter your email address.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Please enter a valid email address.")

        if mobile_number and (
            not mobile_number.isdigit() or len(mobile_number) != 10
        ):
            errors.append("Please enter a valid 10-digit mobile number.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save(
                update_fields=["first_name", "last_name", "email"]
            )

            profile.mobile_number = mobile_number
            profile.save(update_fields=["mobile_number"])

            messages.success(request, "Profile updated successfully!")
            return redirect("user_profile")

    user = request.user

    completed_fields = [
        bool(user.first_name.strip()),
        bool(user.last_name.strip()),
        bool(user.email.strip()),
        bool(profile.mobile_number.strip()),
    ]

    completion = int(
        sum(completed_fields) / len(completed_fields) * 100
    )

    return render(
        request,
        "users/profile.html",
        {
            "profile": profile,
            "completion": completion,
        }
    )

