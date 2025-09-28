from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.utils.jwt_custom_authentication import jwt_required
from api.utils.email_utils import send_donation_receipt
import logging

logger = logging.getLogger("email_api_view")

@api_view(["POST"])
@jwt_required
def send_email_view(request):
    """
    Enhanced email API endpoint to send modular emails.
    Accepts flexible payload including:
    - Required: to_email
    - Optional: name, amount, cause, reference
    - Optional: template, cc, bcc, attachments, reply_to, from_email
    """
    data = request.data
    to_email = data.get("to_email")

    if not to_email:
        return Response({"error": "to_email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        logger.info(f" Sending email with payload: {data}")

        send_donation_receipt(
            to_email=to_email,
            name=data.get("name"),
            amount=data.get("amount"),
            cause=data.get("cause"),
            reference=data.get("reference"),
            template=data.get("template", "donation_receipt"),
            from_email=data.get("from_email"),
            reply_to=data.get("reply_to"),
            cc=data.get("cc"),
            bcc=data.get("bcc"),
            attachments=data.get("attachments")
        )

        return Response({"message": " Email sent successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f" Email send failed: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)