"""
Email service stub. In production, wire this up to an SMTP provider
(SendGrid, SES, Mailgun, etc). For local development it just logs to console.
"""
import logging

logger = logging.getLogger("study_connect_ai.email")


def send_password_reset_email(to_email: str, reset_token: str):
    """
    Sends (or in dev, logs) a password reset email containing the reset token/link.
    """
    reset_link = f"http://localhost:5173/reset-password?email={to_email}&token={reset_token}"
    logger.info("Password reset link for %s: %s", to_email, reset_link)
    # TODO: integrate real SMTP/email provider here for production
    return True


def send_welcome_email(to_email: str, name: str):
    logger.info("Welcome email sent to %s (%s)", name, to_email)
    return True
