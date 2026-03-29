from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

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
    