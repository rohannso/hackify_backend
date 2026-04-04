# accounts/utils.py
import threading
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email_async(subject, message, recipient_list, html_message=None):
    """Send email in background thread to avoid blocking requests"""
    def _send():
        try:
            logger.info(f"📧 Attempting to send email to {recipient_list}")
            logger.info(f"📧 Using SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            logger.info(f"📧 From: {settings.DEFAULT_FROM_EMAIL}")
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,  # Changed to False to see errors
            )
            logger.info(f"✅ Email sent successfully to {recipient_list}")
        except Exception as e:
            logger.error(f"❌ Email sending failed: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()

def send_otp_email(user, otp_code, email_type='verification'):
    """
    Send OTP email with HTML template
    email_type: 'verification' or 'password_reset'
    """
    
    if email_type == 'verification':
        subject = 'Hackify - Email Verification Code'
    else:
        subject = 'Hackify - Password Reset Code'
    
    # Plain text message
    message = f'''
Hello {user.name},

Your verification code is: {otp_code}

This code will expire in 10 minutes.

Best regards,
Hackify Team
    '''
    
    logger.info(f"🔔 Queuing OTP email for {user.email}")
    
    # Send asynchronously
    send_email_async(
        subject=subject,
        message=message,
        recipient_list=[user.email],
    )