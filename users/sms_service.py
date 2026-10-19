
import logging

logger = logging.getLogger(__name__)


def send_sms(mobile_number, message):
    """
    SMS sending function.
    Gateway connect pannum varai console-la mattum test pannuvom.
    Real SMS innum send aagadhu.
    """

    if not mobile_number:
        logger.warning("SMS not sent: mobile number is missing.")
        return False

    print("\n========== SMS TEST ==========")
    print(f"Mobile Number: {mobile_number}")
    print(f"Message: {message}")
    print("==============================\n")

    return True

