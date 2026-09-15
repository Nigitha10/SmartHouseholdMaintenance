from django.shortcuts import render, redirect, get_object_or_404
from .models import Appliance
import qrcode
import base64
from io import BytesIO
from datetime import date


def add_appliance(request):
    if request.method == "POST":
        appliance_type = request.POST.get("appliance_type")
        brand = request.POST.get("brand")
        model_number = request.POST.get("model_number")
        customer_care_number = request.POST.get("customer_care_number")
        purchase_date = request.POST.get("purchase_date")
        bill = request.FILES.get("bill")
        service_interval_months = request.POST.get("service_interval_months")

        # Warranty details
        warranty_start_date = request.POST.get("warranty_start_date")
        warranty_expiry_date = request.POST.get("warranty_expiry_date")

        # Service details
        last_service_date = request.POST.get("last_service_date")
        next_service_date = request.POST.get("next_service_date")
        service_type = request.POST.get("service_type")
        service_notes = request.POST.get("service_notes")

        Appliance.objects.create(
            appliance_type=appliance_type,
            brand=brand,
            model_number=model_number,
            customer_care_number=customer_care_number,
            purchase_date=purchase_date,
            bill=bill,
            service_interval_months=service_interval_months,
            warranty_start_date=warranty_start_date,
            warranty_expiry_date=warranty_expiry_date,
            last_service_date=last_service_date,
            next_service_date=next_service_date,
            service_type=service_type,
            service_notes=service_notes
        )

        return redirect("appliance_list")

    return render(request, "appliances/add_appliance.html")


def appliance_list(request):
    appliances = Appliance.objects.all()

    return render(
        request,
        "appliances/appliance_list.html",
        {"appliances": appliances}
    )


def appliance_detail(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)

    return render(
        request,
        "appliances/appliance_detail.html",
        {
            "appliance": appliance,
            "today": date.today()
        }
    )


def edit_appliance(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)

    if request.method == "POST":
        appliance.appliance_type = request.POST.get("appliance_type")
        appliance.brand = request.POST.get("brand")
        appliance.model_number = request.POST.get("model_number")
        appliance.customer_care_number = request.POST.get("customer_care_number")
        appliance.purchase_date = request.POST.get("purchase_date")
        appliance.service_interval_months = request.POST.get(
            "service_interval_months"
        )

        # Warranty details
        appliance.warranty_start_date = request.POST.get(
            "warranty_start_date"
        )
        appliance.warranty_expiry_date = request.POST.get(
            "warranty_expiry_date"
        )

        # Service details
        appliance.last_service_date = request.POST.get(
            "last_service_date"
        )
        appliance.next_service_date = request.POST.get(
            "next_service_date"
        )
        appliance.service_type = request.POST.get("service_type")
        appliance.service_notes = request.POST.get("service_notes")

        appliance.save()

        return redirect("appliance_list")

    return render(
        request,
        "appliances/edit_appliance.html",
        {"appliance": appliance}
    )


def qr_codes(request):
    appliances = Appliance.objects.all()

    qr_data = []

    for appliance in appliances:
        url = f"http://192.168.1.35:8000/appliances/{appliance.id}/"

        qr = qrcode.make(url)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        qr_code = base64.b64encode(
            buffer.getvalue()
        ).decode()

        qr_data.append({
            "appliance": appliance,
            "qr_code": qr_code
        })

    return render(
        request,
        "appliances/qr_codes.html",
        {"qr_data": qr_data}
    )