
from django.core.mail import send_mail
from django.conf import settings


def send_twilio_email(to_email, subject, html_content):
    """
    Existing function name-ai maintain pannrom,
    so existing notification calls ellam work aagum.
    Ippo Gmail SMTP use pannum.
    """
    if not to_email:
        return False

    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=html_content,
        fail_silently=False,
    )

    return True
