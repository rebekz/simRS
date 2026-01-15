"""Patient Portal Email Service

Service for sending patient portal related emails.
"""
import os
from typing import Optional
from datetime import datetime

from app.core.config import settings


class PatientPortalEmailService:
    """Service for sending patient portal emails

    Note: This is a template service. In production, integrate with
    an email service like SendGrid, AWS SES, or SMTP server.
    """

    def __init__(self):
        self.from_email = getattr(settings, 'PORTAL_EMAIL_FROM', 'no-reply@simrs.hospital.id')
        self.from_name = getattr(settings, 'PORTAL_EMAIL_FROM_NAME', 'SIMRS Patient Portal')
        self.base_url = getattr(settings, 'PORTAL_BASE_URL', 'https://portal.simrs.hospital.id')

    async def send_verification_email(
        self,
        to_email: str,
        patient_name: str,
        verification_code: str,
        expires_in_minutes: int = 15,
    ) -> bool:
        """Send email verification code

        Args:
            to_email: Recipient email address
            patient_name: Patient's name
            verification_code: 6-digit verification code
            expires_in_minutes: Code expiration time

        Returns:
            True if email sent successfully
        """
        subject = "Verify Your Email Address - SIMRS Patient Portal"
        body = self._get_verification_email_body(patient_name, verification_code, expires_in_minutes)

        # TODO: Integrate with actual email service
        # For now, log the email content
        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")

        # Example integration with SendGrid:
        # import sendgrid
        # from sendgrid.helpers.mail import Mail
        # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        # message = Mail(
        #     from_email=self.from_email,
        #     to_emails=to_email,
        #     subject=subject,
        #     html_content=body
        # )
        # response = sg.send(message)
        # return response.status_code == 202

        return True

    async def send_welcome_email(
        self,
        to_email: str,
        patient_name: str,
        portal_url: str,
    ) -> bool:
        """Send welcome email after successful registration

        Args:
            to_email: Recipient email address
            patient_name: Patient's name
            portal_url: URL to patient portal
        """
        subject = "Welcome to SIMRS Patient Portal"
        body = self._get_welcome_email_body(patient_name, portal_url)

        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")

        return True

    async def send_password_reset_email(
        self,
        to_email: str,
        patient_name: str,
        reset_token: str,
        expires_in_hours: int = 1,
    ) -> bool:
        """Send password reset email

        Args:
            to_email: Recipient email address
            patient_name: Patient's name
            reset_token: Password reset token
            expires_in_hours: Token expiration time
        """
        subject = "Reset Your Password - SIMRS Patient Portal"
        reset_link = f"{self.base_url}/auth/reset-password?token={reset_token}"
        body = self._get_password_reset_email_body(patient_name, reset_link, expires_in_hours)

        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")

        return True

    async def send_password_changed_email(
        self,
        to_email: str,
        patient_name: str,
        changed_at: datetime,
    ) -> bool:
        """Send password change confirmation email

        Args:
            to_email: Recipient email address
            patient_name: Patient's name
            changed_at: When password was changed
        """
        subject = "Password Changed - SIMRS Patient Portal"
        body = self._get_password_changed_email_body(patient_name, changed_at)

        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")

        return True

    async def send_account_locked_email(
        self,
        to_email: str,
        patient_name: str,
        locked_until: Optional[datetime] = None,
    ) -> bool:
        """Send account locked notification email

        Args:
            to_email: Recipient email address
            patient_name: Patient's name
            locked_until: When account will be unlocked (None = permanent lock)
        """
        subject = "Account Locked - SIMRS Patient Portal"
        body = self._get_account_locked_email_body(patient_name, locked_until)

        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")

        return True

    def _get_verification_email_body(
        self,
        patient_name: str,
        verification_code: str,
        expires_in_minutes: int,
    ) -> str:
        """Generate HTML body for verification email"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">SIMRS Patient Portal</h1>
    </div>

    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #667eea; margin-top: 0;">Verify Your Email Address</h2>

        <p>Dear <strong>{patient_name}</strong>,</p>

        <p>Thank you for registering for the SIMRS Patient Portal. To complete your registration, please verify your email address by entering the following verification code:</p>

        <div style="background: white; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 30px 0; border-radius: 5px;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #667eea;">
                {verification_code}
            </span>
        </div>

        <p><strong>This code will expire in {expires_in_minutes} minutes.</strong></p>

        <p>If you did not request this verification, please ignore this email or contact our support team.</p>

        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            <strong>Need help?</strong><br>
            Contact our support team:<br>
            Email: support@simrs.hospital.id<br>
            Phone: (021) 1234-5678
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #777; font-size: 12px;">
        <p>This is an automated email. Please do not reply directly.</p>
        <p>&copy; {datetime.now().year} SIMRS Hospital. All rights reserved.</p>
    </div>
</body>
</html>
        """

    def _get_welcome_email_body(self, patient_name: str, portal_url: str) -> str:
        """Generate HTML body for welcome email"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to SIMRS Patient Portal</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">SIMRS Patient Portal</h1>
    </div>

    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #667eea; margin-top: 0;">Welcome, {patient_name}!</h2>

        <p>Your patient portal account has been successfully created and verified.</p>

        <h3 style="color: #333;">What You Can Do:</h3>
        <ul style="line-height: 2;">
            <li>View your complete medical records</li>
            <li>Schedule and manage appointments</li>
            <li>Request prescription refills</li>
            <li>View lab results and radiology reports</li>
            <li>Send secure messages to your healthcare providers</li>
            <li>View and pay bills online</li>
            <li>Upload insurance and ID documents</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{portal_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Access Patient Portal
            </a>
        </div>

        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            <strong>Need help getting started?</strong><br>
            Contact our support team:<br>
            Email: support@simrs.hospital.id<br>
            Phone: (021) 1234-5678
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #777; font-size: 12px;">
        <p>&copy; {datetime.now().year} SIMRS Hospital. All rights reserved.</p>
    </div>
</body>
</html>
        """

    def _get_password_reset_email_body(
        self,
        patient_name: str,
        reset_link: str,
        expires_in_hours: int,
    ) -> str:
        """Generate HTML body for password reset email"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">SIMRS Patient Portal</h1>
    </div>

    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #667eea; margin-top: 0;">Reset Your Password</h2>

        <p>Dear <strong>{patient_name}</strong>,</p>

        <p>We received a request to reset your password. Click the button below to create a new password:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Reset Password
            </a>
        </div>

        <p>Or copy and paste this link into your browser:</p>
        <p style="background: white; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px;">
            {reset_link}
        </p>

        <p><strong>This link will expire in {expires_in_hours} hour(s).</strong></p>

        <p>If you did not request this password reset, please ignore this email or contact our support team immediately.</p>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #777; font-size: 12px;">
        <p>&copy; {datetime.now().year} SIMRS Hospital. All rights reserved.</p>
    </div>
</body>
</html>
        """

    def _get_password_changed_email_body(self, patient_name: str, changed_at: datetime) -> str:
        """Generate HTML body for password changed email"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Changed</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">SIMRS Patient Portal</h1>
    </div>

    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #667eea; margin-top: 0;">Password Successfully Changed</h2>

        <p>Dear <strong>{patient_name}</strong>,</p>

        <p>Your password was successfully changed on <strong>{changed_at.strftime('%B %d, %Y at %I:%M %p')}</strong>.</p>

        <p>If you did not make this change, please contact our support team immediately.</p>

        <p style="margin-top: 30px;">
            Contact our support team:<br>
            Email: support@simrs.hospital.id<br>
            Phone: (021) 1234-5678
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #777; font-size: 12px;">
        <p>&copy; {datetime.now().year} SIMRS Hospital. All rights reserved.</p>
    </div>
</body>
</html>
        """

    def _get_account_locked_email_body(
        self,
        patient_name: str,
        locked_until: Optional[datetime],
    ) -> str:
        """Generate HTML body for account locked email"""
        if locked_until:
            lock_message = f"Your account has been temporarily locked due to multiple failed login attempts. It will be automatically unlocked on <strong>{locked_until.strftime('%B %d, %Y at %I:%M %p')}</strong>."
        else:
            lock_message = "Your account has been locked due to security concerns. Please contact our support team to resolve this issue."

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Locked</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">SIMRS Patient Portal</h1>
    </div>

    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <h2 style="color: #e74c3c; margin-top: 0;">Account Locked</h2>

        <p>Dear <strong>{patient_name}</strong>,</p>

        <p>{lock_message}</p>

        <p>If you believe this is an error, please contact our support team.</p>

        <p style="margin-top: 30px;">
            Contact our support team:<br>
            Email: support@simrs.hospital.id<br>
            Phone: (021) 1234-5678
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #777; font-size: 12px;">
        <p>&copy; {datetime.now().year} SIMRS Hospital. All rights reserved.</p>
    </div>
</body>
</html>
        """
