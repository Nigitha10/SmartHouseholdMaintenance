from django.shortcuts import render, redirect, get_object_or_404
from .models import Appliance
from django.contrib.auth.decorators import login_required
from service_provider.models import Notification, ServiceRequest

import qrcode
import base64
from io import BytesIO
from datetime import date


# =========================================================
# ADD APPLIANCE
# =========================================================

def add_appliance(request):

    if request.method == "POST":

        appliance_type = request.POST.get("appliance_type")
        brand = request.POST.get("brand")
        model_number = request.POST.get("model_number")
        customer_care_number = request.POST.get("customer_care_number")
        purchase_date = request.POST.get("purchase_date")
        bill = request.FILES.get("bill")

        service_interval_months = (
            request.POST.get("service_interval_months") or 6
        )

        # Warranty details
        warranty_start_date = request.POST.get(
            "warranty_start_date"
        )

        warranty_expiry_date = request.POST.get(
            "warranty_expiry_date"
        )

        # Service details
        last_service_date = request.POST.get(
            "last_service_date"
        )

        next_service_date = request.POST.get(
            "next_service_date"
        )

        service_type = request.POST.get(
            "service_type"
        ) or ""

        service_notes = request.POST.get(
            "service_notes"
        ) or ""
                # Maintenance Cost
        service_cost = request.POST.get(
            "service_cost"
        ) or 0

        repair_cost = request.POST.get(
            "repair_cost"
        ) or 0

        spare_parts_cost = request.POST.get(
            "spare_parts_cost"
        ) or 0

        other_cost = request.POST.get(
            "other_cost"
        ) or 0

        # Create appliance
        appliance = Appliance.objects.create(
            owner=request.user,
            appliance_type=appliance_type,
            brand=brand,
            model_number=model_number,
            customer_care_number=customer_care_number,
            purchase_date=purchase_date,
            bill=bill,
            service_interval_months=service_interval_months,

            warranty_start_date=(
                warranty_start_date
                if warranty_start_date
                else None
            ),

            warranty_expiry_date=(
                warranty_expiry_date
                if warranty_expiry_date
                else None
            ),

            last_service_date=(
                last_service_date
                if last_service_date
                else None
            ),

            next_service_date=(
                next_service_date
                if next_service_date
                else None
            ),

            service_type=service_type,
            service_notes=service_notes,
                     

            service_cost=service_cost,
            repair_cost=repair_cost,
            spare_parts_cost=spare_parts_cost,
            other_cost=other_cost
        )

        # Public Render URL for QR Code
        appliance.qr_code = (
            f"https://smarthouseholdmaintenance.onrender.com/"
            f"appliances/{appliance.id}/"
        )

        appliance.save()

        return redirect("appliance_list")

    return render(
        request,
        "appliances/add_appliance.html"
    )
    



# =========================================================
# APPLIANCE LIST
# =========================================================

@login_required
def appliance_list(request):
    appliances = Appliance.objects.filter(owner=request.user)

    return render(
        request,
        "appliances/appliance_list.html",
        {"appliances": appliances}
    )


# =========================================================
# APPLIANCE DETAIL
# =========================================================

def appliance_detail(request, pk):

    appliance = get_object_or_404(
        Appliance,
        pk=pk
    )

    return render(
        request,
        "appliances/appliance_detail.html",
        {
            "appliance": appliance,
            "today": date.today()
        }
    )


# =========================================================
# EDIT APPLIANCE
# =========================================================

def edit_appliance(request, pk):

    appliance = get_object_or_404(
        Appliance,
        pk=pk
    )

    if request.method == "POST":

        # Basic information
        appliance.appliance_type = request.POST.get(
            "appliance_type"
        )

        appliance.brand = request.POST.get(
            "brand"
        )

        appliance.model_number = request.POST.get(
            "model_number"
        )

        appliance.customer_care_number = request.POST.get(
            "customer_care_number"
        ) or ""

        # Purchase date
        purchase_date = request.POST.get(
            "purchase_date"
        )

        if purchase_date:
            appliance.purchase_date = purchase_date

        # Service interval
        appliance.service_interval_months = (
            request.POST.get(
                "service_interval_months"
            ) or 6
        )

        # Warranty start date
        warranty_start = request.POST.get(
            "warranty_start_date"
        )

        appliance.warranty_start_date = (
            warranty_start
            if warranty_start
            else None
        )

        # Warranty expiry date
        warranty_expiry = request.POST.get(
            "warranty_expiry_date"
        )

        appliance.warranty_expiry_date = (
            warranty_expiry
            if warranty_expiry
            else None
        )

        # Last service date
        last_service = request.POST.get(
            "last_service_date"
        )

        appliance.last_service_date = (
            last_service
            if last_service
            else None
        )

        # Next service date
        next_service = request.POST.get(
            "next_service_date"
        )

        appliance.next_service_date = (
            next_service
            if next_service
            else None
        )

        # Service details
        appliance.service_type = (
            request.POST.get(
                "service_type"
            ) or ""
        )

        appliance.service_notes = (
            request.POST.get(
                "service_notes"
            ) or ""
        )

        # Maintenance Cost
        appliance.maintenance_cost = (
            request.POST.get(
                "maintenance_cost"
            ) or 0
        )

        # Save changes
        appliance.save()

        return redirect(
            "appliance_list"
        )

    return render(
        request,
        "appliances/edit_appliance.html",
        {
            "appliance": appliance
        }
    )


# =========================================================
# QR CODES
# =========================================================

def qr_codes(request):

    appliances = Appliance.objects.all()

    qr_data = []

    for appliance in appliances:

        # Create URL if QR URL doesn't exist
        if not appliance.qr_code:

            appliance.qr_code = (
                f"https://smarthouseholdmaintenance.onrender.com/"
                f"appliances/{appliance.id}/"
            )

            appliance.save()

        url = appliance.qr_code

        # Generate QR code
        qr = qrcode.make(url)

        buffer = BytesIO()

        qr.save(
            buffer,
            format="PNG"
        )

        # Convert image to Base64
        qr_code = base64.b64encode(
            buffer.getvalue()
        ).decode()

        qr_data.append(
            {
                "appliance": appliance,
                "qr_code": qr_code
            }
        )

    return render(
        request,
        "appliances/qr_codes.html",
        {
            "qr_data": qr_data
        }
    )


# =========================================================
# SERVICE & MAINTENANCE
# =========================================================

def service(request):

    appliances = Appliance.objects.all()

    return render(
        request,
        "appliances/service.html",
        {
            "appliances": appliances
        }
    )


# =========================================================
# REMINDERS
# =========================================================

@login_required
def reminders(request):

    appliances = Appliance.objects.filter(
        owner=request.user
    )

    today = date.today()

    for appliance in appliances:

        # Warranty Reminder
        if appliance.warranty_expiry_date:

            days_left = (
                appliance.warranty_expiry_date - today
            ).days

            if days_left < 0:
                message = (
                    f"Warranty expired for "
                    f"{appliance.brand} {appliance.model_number}."
                )

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

            elif days_left <= 30:
                message = (
                    f"Warranty for {appliance.brand} "
                    f"{appliance.model_number} expires in "
                    f"{days_left} days."
                )

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

        # Service Reminder
        if appliance.next_service_date:

            service_days_left = (
                appliance.next_service_date - today
            ).days

            if service_days_left < 0:
                message = (
                    f"Service is overdue for "
                    f"{appliance.brand} "
                    f"{appliance.model_number}."
                )

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

            elif service_days_left <= 7:
                message = (
                    f"Service for {appliance.brand} "
                    f"{appliance.model_number} is due in "
                    f"{service_days_left} days."
                )

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

    return render(
        request,
        "appliances/reminders.html",
        {
            "appliances": appliances
        }
    )

# =========================================================
# MAINTENANCE HISTORY
# =========================================================

def history(request):

    appliances = Appliance.objects.all()

    return render(
        request,
        "appliances/history.html",
        {
            "appliances": appliances
        }
    )


# =========================================================
# MAINTENANCE COST
# =========================================================

@login_required
def maintenance_cost(request):

    appliances = Appliance.objects.filter(
        owner=request.user
    )

    service_requests = ServiceRequest.objects.filter(
        user=request.user,
        status="Completed"
    ).order_by("-request_date")

    return render(
        request,
        "appliances/maintenance_cost.html",
        {
            "appliances": appliances,
            "service_requests": service_requests,
        }
    )
def health_score(request):

    appliances = Appliance.objects.all()
    today = date.today()

    for appliance in appliances:

        score = 100

        # 1. Warranty expired
        if appliance.warranty_expiry_date:
            if appliance.warranty_expiry_date < today:
                score -= 15

        # 2. No service history
        if not appliance.last_service_date:
            score -= 15

        # 3. Service overdue
        if appliance.next_service_date:
            if appliance.next_service_date < today:
                score -= 20

        # 4. Maintenance cost
        if appliance.maintenance_cost:

            if appliance.maintenance_cost >= 5000:
                score -= 20

            elif appliance.maintenance_cost >= 2000:
                score -= 10

            elif appliance.maintenance_cost >= 1000:
                score -= 5

        # Keep score between 0 and 100
        appliance.health_score = max(0, min(score, 100))

        appliance.save()

    return render(
        request,
        "appliances/health_score.html",
        {
            "appliances": appliances
        }
    )
def ai_assistant(request):

    response = ""

    if request.method == "POST":

        question = request.POST.get("question", "").strip().lower()

        if question:

            # 👋 Greeting
            if question in [
                "hi",
                "hello",
                "hey",
                "hii",
                "hai",
                "good morning",
                "good evening",
                "good afternoon"
            ]:
                response = (
                    "Hi! 👋😊 Welcome to your AI Maintenance Assistant! "
                    "I'm here to help you with your household appliances, "
                    "maintenance, warranty, service and appliance care. 🔧🏠 "
                    "What appliance would you like help with today?"
                )

            # ❤️ Friendly response
            elif (
                "love you" in question
                or "luv you" in question
            ):
                response = (
                    "Aww, that's so sweet! 😊💙 "
                    "I'm always happy to help you with your appliance "
                    "questions and maintenance needs! 🔧🏠✨"
                )

            # 🙏 Thank You
            elif (
                "thank you" in question
                or "thanks" in question
                or "thankyou" in question
            ):
                response = (
                    "You're very welcome! 😊💙 "
                    "I'm always happy to help you with your appliance "
                    "maintenance questions. 🔧✨"
                )

            # ❄️ AC
            elif (
                "ac" in question
                or "air conditioner" in question
            ):

                if (
                    "not cooling" in question
                    or "no cooling" in question
                    or "cooling problem" in question
                    or "cool" in question
                ):
                    response = (
                        "If your AC is not cooling properly ❄️, you can first "
                        "check whether the air filter needs cleaning and make "
                        "sure the outdoor unit has proper airflow. "
                        "Also check that the temperature setting is appropriate. "
                        "If the problem continues, please contact a qualified technician. 🔧😊"
                    )

                elif "service" in question:
                    response = (
                        "Regular AC servicing can help maintain cooling "
                        "performance and efficiency. ❄️🔧 "
                        "Keep the filter clean and follow the recommended "
                        "service schedule. 😊"
                    )

                elif "maintenance" in question:
                    response = (
                        "For AC maintenance ❄️😊, keep the air filter clean, "
                        "make sure airflow is not blocked and follow the "
                        "recommended service schedule. 🔧"
                    )

                else:
                    response = (
                        "Sure! 😊 I can help you with your AC. ❄️ "
                        "You can ask me about cooling problems, service, "
                        "maintenance, warranty or general AC care."
                    )

            # 🧊 Refrigerator
            elif (
                "fridge" in question
                or "refrigerator" in question
            ):

                if (
                    "not cooling" in question
                    or "cooling" in question
                ):
                    response = (
                        "If your refrigerator is not cooling properly 🧊, "
                        "check the temperature setting and make sure the "
                        "door is closing properly. Keep the ventilation areas "
                        "clear. If the issue continues, contact a qualified technician. 🔧😊"
                    )

                elif (
                    "maintenance" in question
                    or "service" in question
                ):
                    response = (
                        "For refrigerator maintenance 🧊😊, keep the inside "
                        "clean, check the door seal and make sure ventilation "
                        "is not blocked. Follow the recommended service schedule. 🔧"
                    )

                else:
                    response = (
                        "Sure! 😊 I can help with your refrigerator. 🧊 "
                        "You can ask about cooling, maintenance, service, "
                        "warranty or general refrigerator care."
                    )

            # 🧺 Washing Machine
            elif (
                "washing machine" in question
                or "washing" in question
            ):

                if (
                    "vibration" in question
                    or "shaking" in question
                    or "noise" in question
                ):
                    response = (
                        "If your washing machine is vibrating or making unusual "
                        "noise 🧺, make sure it is placed on a stable, level surface "
                        "and avoid overloading it. If the problem continues, "
                        "consider contacting a qualified technician. 🔧😊"
                    )

                elif (
                    "maintenance" in question
                    or "service" in question
                ):
                    response = (
                        "For washing machine maintenance 🧺😊, keep the drum "
                        "and filter clean, check the water supply and follow "
                        "the recommended service schedule."
                    )

                else:
                    response = (
                        "Sure! 😊 I can help with your washing machine. 🧺 "
                        "You can ask about maintenance, vibration, cleaning, "
                        "service or warranty."
                    )

            # 📺 TV
            elif (
                "tv" in question
                or "television" in question
            ):

                if (
                    "not working" in question
                    or "problem" in question
                ):
                    response = (
                        "For a TV problem 📺😊, you can first check the power "
                        "connection and remote batteries. If the issue continues, "
                        "please contact the manufacturer's support or a qualified technician."
                    )

                elif (
                    "maintenance" in question
                    or "clean" in question
                ):
                    response = (
                        "For TV care 📺✨, keep the screen clean using suitable "
                        "screen-cleaning methods and keep the ventilation areas "
                        "clear. Avoid applying liquid directly to the screen."
                    )

                else:
                    response = (
                        "Sure! 😊 I can help with your TV. 📺 "
                        "You can ask about basic care, cleaning, power problems, "
                        "service or warranty."
                    )

            # 💧 Water Purifier
            elif (
                "water purifier" in question
                or "purifier" in question
            ):

                if "filter" in question:
                    response = (
                        "Water-purifier filters should be replaced according "
                        "to the manufacturer's recommended schedule. 💧😊 "
                        "You can keep the filter replacement and service dates "
                        "updated in your maintenance system."
                    )

                elif (
                    "maintenance" in question
                    or "service" in question
                ):
                    response = (
                        "Regular water-purifier maintenance is important for "
                        "proper operation. 💧🔧 "
                        "Keep track of filter replacement and service dates."
                    )

                else:
                    response = (
                        "Sure! 😊 I can help with your water purifier. 💧 "
                        "You can ask about filters, maintenance, service or warranty."
                    )

            # 🛡️ Warranty
            elif "warranty" in question:

                if (
                    "what is" in question
                    or "meaning" in question
                ):
                    response = (
                        "A warranty 🛡️ is a manufacturer's or seller's promise "
                        "to cover certain repairs or replacements for a specified "
                        "period, subject to its terms and conditions. 😊"
                    )

                else:
                    response = (
                        "Sure! 🛡️😊 You can check your appliance's warranty "
                        "start date and expiry date in the Warranty Management "
                        "section of the system."
                    )

            # 🔧 Service / Maintenance
            elif (
                "service" in question
                or "maintenance" in question
                or "maintain" in question
            ):
                response = (
                    "Regular appliance maintenance helps keep appliances "
                    "working properly and can help identify problems early. 🔧😊 "
                    "You can check the Service & Maintenance section for "
                    "your appliance schedule and service information."
                )

            # 💰 Maintenance Cost
            elif (
                "cost" in question
                or "price" in question
                or "expense" in question
            ):
                response = (
                    "You can keep track of your appliance maintenance expenses "
                    "in the Maintenance Cost section. 💰😊 "
                    "Recording service costs can help you understand your "
                    "maintenance spending over time."
                )

            # ❤️ Health Score
            elif (
                "health score" in question
                or "health" in question
                or "score" in question
            ):
                response = (
                    "Your Appliance Health Score ❤️🔧 is calculated using "
                    "information such as warranty status, service information "
                    "and maintenance cost. "
                    "You can check the Health Score section to see your appliance's condition."
                )

            # 📅 Reminder
            elif (
                "reminder" in question
                or "remind" in question
                or "due" in question
            ):
                response = (
                    "You can check the Reminders & Notifications section 🔔😊 "
                    "for warranty expiry and upcoming service dates."
                )

            # 📱 QR Code
            elif (
                "qr" in question
                or "qr code" in question
            ):
                response = (
                    "Each appliance can have its own QR code 📱😊. "
                    "You can use the QR Codes section to access appliance "
                    "information quickly."
                )

            # 🏠 Appliance care
            elif (
                "appliance" in question
                or "household" in question
            ):
                response = (
                    "Of course! 🏠😊 I can help you manage and maintain your "
                    "household appliances. You can ask me about AC, refrigerator, "
                    "washing machine, TV, water purifier, warranty, service, "
                    "maintenance cost or health score. 🔧💙"
                )

            # ❓ Unrelated question
            else:
                response = (
                    "I'm here mainly to help with your household appliances. 😊🔧 "
                    "Could you please ask me something related to an appliance? "
                    "For example: 'My AC is not cooling', "
                    "'When should I service my fridge?', or "
                    "'How can I maintain my washing machine?' 🏠✨"
                )

    return render(
        request,
        "appliances/ai_assistant.html",
        {
            "response": response
        }
    )
@login_required
def reminders(request):
    appliances = Appliance.objects.filter(owner=request.user)
    today = date.today()

    warranty_reminders = []
    service_reminders = []

    for appliance in appliances:

        # =========================
        # Warranty Reminder
        # =========================
        if appliance.warranty_expiry_date:
            days_left = (
                appliance.warranty_expiry_date - today
            ).days

            if days_left < 0:
                message = (
                    f"{appliance.brand} {appliance.appliance_type} "
                    "warranty has expired."
                )

                warranty_reminders.append({
                    "appliance": appliance,
                    "message": "Warranty has expired.",
                    "type": "Expired",
                })

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

            elif days_left <= 30:
                message = (
                    f"{appliance.brand} {appliance.appliance_type} "
                    f"warranty expires in {days_left} day(s)."
                )

                warranty_reminders.append({
                    "appliance": appliance,
                    "message": f"Warranty expires in {days_left} day(s).",
                    "type": "Expiring Soon",
                })

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

        # =========================
        # Service Reminder
        # =========================
        if appliance.next_service_date:
            service_days_left = (
                appliance.next_service_date - today
            ).days

            if service_days_left < 0:
                message = (
                    f"{appliance.brand} {appliance.appliance_type} "
                    "service is overdue."
                )

                service_reminders.append({
                    "appliance": appliance,
                    "message": "Service is overdue.",
                    "type": "Overdue",
                })

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

            elif service_days_left <= 30:
                message = (
                    f"{appliance.brand} {appliance.appliance_type} "
                    f"service is due in {service_days_left} day(s)."
                )

                service_reminders.append({
                    "appliance": appliance,
                    "message": f"Service due in {service_days_left} day(s).",
                    "type": "Upcoming",
                })

                if not Notification.objects.filter(
                    user=request.user,
                    message=message
                ).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=message
                    )

    return render(
        request,
        "appliances/reminders.html",
        {
            "warranty_reminders": warranty_reminders,
            "service_reminders": service_reminders,
        },
    )