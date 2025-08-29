# ABOUTME: Email service for the Office Cheer application
# ABOUTME: Handles formatting and sending emails using Amazon SES

import logging
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from office_cheer.db.models import Staff

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for sending email notifications for birthdays and anniversaries.
    Uses Amazon SES for email delivery.
    """
    
    def __init__(self, config):
        """
        Initialize the email service.
        
        Args:
            config (Config): Application configuration
        """
        self.config = config
        self.sender_email = config.email_sender
        self.reply_to_email = config.email_reply_to
        
        # Initialize SES client if not in development mode
        self.ses_client = None
        if not self._is_development():
            self.ses_client = boto3.client(
                'ses',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key
            )
        
        logger.info("Email service initialized")
    
    def send_birthday_email(self, staff, greeting_content, image_url=None):
        """
        Send a birthday email to a staff member.
        
        Args:
            staff (Staff): Staff member with birthday
            greeting_content (str): Personalized greeting message
            image_url (str, optional): URL to the birthday card image
            
        Returns:
            bool: True if email was sent successfully
        """
        subject = self._format_subject(self.config.email_subject_birthday, staff)
        body_html = self._format_birthday_email(staff, greeting_content, image_url)
        
        return self._send_email(staff.email_address, subject, body_html)
    
    def send_anniversary_email(self, staff, years, greeting_content, image_url=None):
        """
        Send a work anniversary email to a staff member.
        
        Args:
            staff (Staff): Staff member with anniversary
            years (int): Years of service
            greeting_content (str): Personalized greeting message
            image_url (str, optional): URL to the anniversary card image
            
        Returns:
            bool: True if email was sent successfully
        """
        subject = self._format_subject(self.config.email_subject_anniversary, staff, years)
        body_html = self._format_anniversary_email(staff, years, greeting_content, image_url)
        
        return self._send_email(staff.email_address, subject, body_html)
    
    def _send_email(self, recipient_email, subject, body_html):
        """
        Send an email using Amazon SES.
        
        Args:
            recipient_email (str): Recipient email address
            subject (str): Email subject
            body_html (str): Email body in HTML format
            
        Returns:
            bool: True if email was sent successfully
        """
        if self._is_development():
            # In development mode, just log the email content
            logger.info(f"[DEV MODE] Email would be sent to: {recipient_email}")
            logger.info(f"[DEV MODE] Subject: {subject}")
            logger.info(f"[DEV MODE] Body: {body_html[:100]}...")
            return True
        
        try:
            # Create a multipart message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Reply-To'] = self.reply_to_email
            
            # Attach HTML content
            msg.attach(MIMEText(body_html, 'html'))
            
            # Send the email using Amazon SES
            response = self.ses_client.send_raw_email(
                Source=self.sender_email,
                Destinations=[recipient_email],
                RawMessage={'Data': msg.as_string()}
            )
            
            logger.info(f"Email sent successfully to {recipient_email}, MessageId: {response['MessageId']}")
            return True
        except ClientError as e:
            logger.error(f"Error sending email to {recipient_email}: {e}")
            return False
    
    def _format_subject(self, subject_template, staff, years=None):
        """
        Format the email subject with placeholders.
        
        Args:
            subject_template (str): Subject template with placeholders
            staff (Staff): Staff member
            years (int, optional): Years of service (for anniversaries)
            
        Returns:
            str: Formatted subject string
        """
        display_name = staff.get_display_name()
        
        if years is not None:
            return subject_template.format(name=display_name, years=years)
        else:
            return subject_template.format(name=display_name)
    
    def _format_birthday_email(self, staff, greeting_content, image_url=None):
        """
        Format the HTML body for a birthday email.
        
        Args:
            staff (Staff): Staff member
            greeting_content (str): Personalized greeting message
            image_url (str, optional): URL to the birthday card image
            
        Returns:
            str: HTML email body
        """
        display_name = staff.get_display_name()
        
        # Start with header
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: #0066cc;">Happy Birthday, {display_name}! 🎂</h1>
            </div>
            <div style="padding: 20px; background-color: #ffffff; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="font-size: 16px; line-height: 1.5; color: #333333;">{greeting_content}</p>
        """
        
        # Add image if available
        if image_url:
            html += f"""
                <div style="text-align: center; margin: 20px 0;">
                    <img src="{image_url}" alt="Birthday Card" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                </div>
            """
        
        # Add footer
        html += """
                <p style="font-size: 14px; margin-top: 30px; color: #666666;">
                    This message was automatically generated by the Office Cheer system.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_anniversary_email(self, staff, years, greeting_content, image_url=None):
        """
        Format the HTML body for an anniversary email.
        
        Args:
            staff (Staff): Staff member
            years (int): Years of service
            greeting_content (str): Personalized greeting message
            image_url (str, optional): URL to the anniversary card image
            
        Returns:
            str: HTML email body
        """
        display_name = staff.get_display_name()
        
        # Determine appropriate emoji
        if years == 1:
            emoji = "🎉"  # First year
        elif years <= 5:
            emoji = "🌟"  # Early milestone
        elif years <= 10:
            emoji = "🏆"  # Mid milestone
        else:
            emoji = "🏅"  # Major milestone
        
        # Start with header
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f0f7ff; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: #003366;">Congratulations on {years} Years! {emoji}</h1>
            </div>
            <div style="padding: 20px; background-color: #ffffff; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="font-size: 16px; line-height: 1.5; color: #333333;">{greeting_content}</p>
        """
        
        # Add image if available
        if image_url:
            html += f"""
                <div style="text-align: center; margin: 20px 0;">
                    <img src="{image_url}" alt="Anniversary Card" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                </div>
            """
        
        # Add footer
        html += """
                <p style="font-size: 14px; margin-top: 30px; color: #666666;">
                    This message was automatically generated by the Office Cheer system.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _is_development(self):
        """
        Check if the application is running in development mode.
        
        Returns:
            bool: True if in development mode
        """
        return self.config.debug or not (self.config.aws_access_key_id and self.config.aws_secret_access_key)