# ABOUTME: Configuration management for the Office Cheer application
# ABOUTME: Handles loading settings from environment variables with sensible defaults

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for the Office Cheer application."""
    
    def __init__(self):
        """Initialize configuration with values from environment variables or defaults."""
        # Database settings
        self.database_path = os.getenv('OFFICE_CHEER_DB_PATH', 'sqlite:///office_cheer.db')
        
        # AWS settings
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        # self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        # self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Bedrock settings for LLM
        self.bedrock_model_id = os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-7-sonnet-20250219-v1:0')
        
        # Bedrock settings for image generation
        self.bedrock_image_model_id = os.getenv('BEDROCK_IMAGE_MODEL_ID', 'amazon.nova-canvas-v1:0')
        
        # Email settings
        self.email_sender = os.getenv('EMAIL_SENDER', 'noreply@example.com')
        self.email_reply_to = os.getenv('EMAIL_REPLY_TO', 'support@example.com')
        self.email_subject_birthday = os.getenv('EMAIL_SUBJECT_BIRTHDAY', 'Happy Birthday, {name}!')
        self.email_subject_anniversary = os.getenv(
            'EMAIL_SUBJECT_ANNIVERSARY', 
            'Congratulations on your {years} Year Anniversary, {name}!'
        )
        
        # Application settings
        self.daily_check_time = os.getenv('DAILY_CHECK_TIME', '08:00')  # 8:00 AM default
        self.lookforward_days = int(os.getenv('LOOKFORWARD_DAYS', '3'))  # Look 3 days ahead by default
        self.check_on_startup = os.getenv('CHECK_ON_STARTUP', 'false').lower() == 'true'
        
        # Development settings
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration settings."""
        # Ensure AWS credentials are set in production
        # if not self._is_development() and (not self.aws_access_key_id or not self.aws_secret_access_key):
        #     raise ValueError(
        #         "AWS credentials are required in production. "
        #         "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
        #     )
    
    def _is_development(self):
        """Check if the application is running in development mode."""
        return self.debug or os.getenv('ENVIRONMENT', 'development').lower() == 'development'


# Example usage of configuration in other modules:
# from office_cheer.config import Config
# config = Config()
# aws_region = config.aws_region