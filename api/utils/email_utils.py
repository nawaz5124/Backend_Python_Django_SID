from django.core.mail import EmailMessage
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
def send_email(to, subject, html_body, plain_text=None, reply_to=None, attachments=None, from_email=None, cc=None, bcc=None):
    """
    Core email sender using Django's SMTP backend.
    Parameters:
    - to: str or list of recipient(s)
    - subject: Email subject
    - html_body: Email body (HTML)
    - plain_text: Optional plain text fallback
    - reply_to: Optional reply-to address
    - attachments: Optional list of file paths
    - from_email: Optional override for from address
    - cc: Optional list of CC emails
    - bcc: Optional list of BCC emails
    """
    if isinstance(to, str):
        to = [to]
    email = EmailMessage(
        subject=subject,
        body=plain_text or html_body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=to,
        reply_to=[reply_to or settings.REPLY_TO_EMAIL],
        cc=cc or [],
        bcc=bcc or []
    )
    email.content_subtype = "html"
    if attachments:
        for file_path in attachments:
            email.attach_file(file_path)
    logger.info(f" Sending email to {to} | Subject: {subject}")
    email.send()

def send_donation_receipt(
    to_email,
    name=None,
    amount=None,
    cause=None,
    reference=None,
    template="donation_receipt",
    from_email=None,
    reply_to=None,
    cc=None,
    bcc=None,
    attachments=None
):
    """
    Wrapper for sending donation receipt emails.
    Accepts flexible input and calls `send_email()`.
    Fields are optional for flexibility. Can be extended by template type.
    """
    if template == "donation_receipt":
        subject = "Your Donation Receipt – Camel Foundation"
        html_body = f"""
        <div style="background-color: #f7f9fa; padding: 32px;">
        <div style="font-family: Arial, sans-serif; padding: 24px; color: #333;">
        <h2 style="color: #0B5394;">JazakAllah Khair, {name or 'Valued Donor'}!</h2>

        <p style="font-size: 16px;">
            We are truly grateful for your kind donation of 
            <strong style="color: #27ae60;">{amount or 'an unspecified amount'}</strong> 
            towards <strong>{cause or 'our cause'}</strong>.
        </p>

        <p style="font-size: 16px;">
            Your donation reference: <strong>{reference or 'N/A'}</strong>
        </p>

        <p style="font-size: 16px;">
            May Allah ﷻ reward you manifold for your generosity.
        </p>

        <hr style="margin-top: 30px; margin-bottom: 10px;">

        <p style="font-size: 12px; color: #888;">
            🏢 Camel Foundation – Registered Charity (No. <strong>1180968</strong>)<br>
            🌍 UK-based international NGO supporting holistic education and awareness-raising.<br>
           <!-- 📧 {getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@camelfoundation.org')}  -->
        </p>
        </div>
        </div>
        """
        send_email(
            to=to_email,
            subject=subject,
            html_body=html_body,
            reply_to=reply_to,
            from_email=from_email,
            attachments=attachments,
            cc=cc,
            bcc=bcc
        )
    else:
        logger.warning(f" Unknown template: {template}")
        raise ValueError("Unsupported email template selected.")
