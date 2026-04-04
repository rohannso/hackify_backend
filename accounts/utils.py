from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading
from django.core.mail import send_mail
from django.conf import settings

def send_email_async(subject, message, recipient_list, html_message=None):
    """Send email in background thread"""
    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=True,  # Don't crash if email fails
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    thread = threading.Thread(target=_send)
    thread.start()

import threading
from django.core.mail import send_mail
from django.conf import settings

def send_email_async(subject, message, recipient_list, html_message=None):
    """Send email in background thread"""
    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=True,  # Don't crash if email fails
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    thread = threading.Thread(target=_send)
    thread.start()

def send_otp_email(user, otp_code, email_type='verification'):
    """
    Send OTP email with HTML template
    email_type: 'verification' or 'password_reset'
    """
    
    if email_type == 'verification':
        subject = 'Hackify - Email Verification Code'
        template = 'emails/otp_verification.html'
    else:
        subject = 'Hackify - Password Reset Code'
        template = 'emails/password_reset.html'
    
    # Render HTML email
    html_message = render_to_string(template, {
        'user_name': user.name,
        'otp_code': otp_code,
    })
    
    # Plain text fallback
    plain_message = f'''
Hello {user.name},

Your verification code is: {otp_code}

This code will expire in 10 minutes.

Best regards,
Hackify Team
    '''
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
