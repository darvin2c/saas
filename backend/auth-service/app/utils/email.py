import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email using SMTP."""
    if not all([settings.EMAIL_HOST, settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD]):
        print(f"Email configuration missing. Would send email to {to_email} with subject: {subject}")
        return True  # Return True for development without email config
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_USERNAME
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


async def send_verification_email(email: str, token: str, tenant_domain: str) -> bool:
    """Send email verification email."""
    verification_url = f"http://localhost:8000/auth/verify-email?token={token}&tenant={tenant_domain}"
    
    html_content = f"""
    <html>
      <body>
        <h2>Verify Your Email Address</h2>
        <p>Hello!</p>
        <p>Please click the link below to verify your email address for {tenant_domain}:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>If you did not create an account, please ignore this email.</p>
        <p>The verification link will expire in 24 hours.</p>
      </body>
    </html>
    """
    
    return await send_email(email, "Verify Your Email Address", html_content)


async def send_reset_password_email(email: str, token: str, tenant_domain: str) -> bool:
    """Send password reset email."""
    reset_url = f"http://localhost:8000/auth/reset-password?token={token}&tenant={tenant_domain}"
    
    html_content = f"""
    <html>
      <body>
        <h2>Reset Your Password</h2>
        <p>Hello!</p>
        <p>You requested to reset your password for {tenant_domain}. Click the link below:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>If you did not request this, please ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
      </body>
    </html>
    """
    
    return await send_email(email, "Reset Your Password", html_content)
