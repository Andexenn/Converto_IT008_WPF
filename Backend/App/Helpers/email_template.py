"""Create email template"""

from typing import Optional

from Schemas.user import UserData
from Entities.user import User

def get_email_template(email_type: str, user: User, otp_code: Optional[str] = None, expiry_hours: int = 1):
    """Email template"""
    templates = {
        "forgot_password": {
            "subject": "Password Reset Request",
            "body": f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Password Reset Request</h2>
                    <p>Hello {user.FirstName, user.LastName},</p>
                    <p>We received a request to reset your password. Enter this OTP code for reset password</p>
                    <p style="font-style: Bold">
                        {otp_code}
                    </p>
                    <p>This link will expire in {expiry_hours} hours.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br>Converto</p>
                </body>
            </html>
            """
        },
        "welcome": {
            "subject": "Welcome to Our Platform!",
            "body": f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Welcome aboard!</h2>
                    <p>Hello {user.FirstName,  user.LastName},</p>
                    <p>Thank you for joining us. We're excited to have you on board!</p>
                    <p>Get started by exploring your dashboard and customizing your preferences.</p>
                    <br>
                    <p>Best regards,<br>Converto</p>
                </body>
            </html>
            """
        },
    }

    template = templates.get(email_type, {
        "subject": "Notification",
        "body": "<p>Notification message</p>"
    })

    return template["subject"], template["body"]