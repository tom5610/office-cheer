# ABOUTME: Image generation service for the Office Cheer application
# ABOUTME: Creates personalized greeting card images using Amazon Bedrock Canvas

import logging
import os
import json
import base64
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
from pathlib import Path

from office_cheer.db.models import Staff

logger = logging.getLogger(__name__)

class ImageService:
    """
    Service for generating personalized greeting card images using Amazon Bedrock Canvas.
    Images are generated based on staff interests and stored locally or in S3.
    """
    
    def __init__(self, config):
        """
        Initialize the image service.
        
        Args:
            config (Config): Application configuration
        """
        self.config = config
        self.image_model_id = config.bedrock_image_model_id
        
        # Setup Bedrock client if not in development mode
        self.bedrock_client = None
        if not self._is_development():
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key
            )
        
        # Create local directory for storing images
        self.image_dir = Path("generated_images")
        self.image_dir.mkdir(exist_ok=True)
        
        logger.info("Image service initialized")
    
    def generate_birthday_image(self, staff):
        """
        Generate a birthday card image based on staff interests.
        
        Args:
            staff (Staff): Staff member with birthday
            
        Returns:
            str: Path or URL to the generated image
        """
        display_name = staff.get_display_name()
        interests = staff.get_interests_list()
        
        # Create a prompt based on interests
        if interests:
            primary_interest = interests[0]
            prompt = self._create_birthday_prompt(display_name, primary_interest, interests[1:])
        else:
            prompt = self._create_birthday_prompt(display_name)
        
        return self._generate_and_save_image(staff, "birthday", prompt)
    
    def generate_anniversary_image(self, staff, years):
        """
        Generate a work anniversary card image.
        
        Args:
            staff (Staff): Staff member with anniversary
            years (int): Years of service
            
        Returns:
            str: Path or URL to the generated image
        """
        display_name = staff.get_display_name()
        interests = staff.get_interests_list()
        
        # Create a prompt based on interests and years
        if interests:
            primary_interest = interests[0]
            prompt = self._create_anniversary_prompt(display_name, years, primary_interest, interests[1:])
        else:
            prompt = self._create_anniversary_prompt(display_name, years)
        
        return self._generate_and_save_image(staff, f"anniversary_{years}yr", prompt)
    
    def _create_birthday_prompt(self, name, primary_interest=None, other_interests=None):
        """
        Create a prompt for birthday image generation.
        
        Args:
            name (str): Staff display name
            primary_interest (str, optional): Primary interest
            other_interests (list, optional): Other interests
            
        Returns:
            str: Image generation prompt
        """
        # Base prompt for a birthday card
        base_prompt = f"A cheerful, professional digital birthday card for {name}."
        
        # Personalize based on interests
        if primary_interest:
            interest_prompt = f" The design incorporates elements of {primary_interest}"
            if other_interests and len(other_interests) > 0:
                additional = ", ".join(other_interests[:2])  # Limit to first 2 other interests
                interest_prompt += f" along with subtle references to {additional}"
            base_prompt += interest_prompt
        
        # Add styling elements
        style_prompt = " The image is colorful but professional, suitable for a workplace birthday card. It includes festive elements like balloons, cake, or confetti. The overall style is modern and upbeat, with 'Happy Birthday' text prominently displayed."
        
        return base_prompt + style_prompt
    
    def _create_anniversary_prompt(self, name, years, primary_interest=None, other_interests=None):
        """
        Create a prompt for anniversary image generation.
        
        Args:
            name (str): Staff display name
            years (int): Years of service
            primary_interest (str, optional): Primary interest
            other_interests (list, optional): Other interests
            
        Returns:
            str: Image generation prompt
        """
        # Base prompt with milestone significance
        if years == 1:
            milestone = "first year"
            base_prompt = f"A congratulatory digital card celebrating {name}'s first year work anniversary."
        elif years == 5:
            milestone = "5-year"
            base_prompt = f"An elegant digital card celebrating {name}'s 5-year work anniversary milestone."
        elif years == 10:
            milestone = "decade"
            base_prompt = f"A prestigious digital card celebrating {name}'s impressive decade of service."
        elif years >= 20:
            milestone = f"{years}-year"
            base_prompt = f"A distinguished digital card celebrating {name}'s remarkable {years} years of dedicated service."
        else:
            milestone = f"{years}-year"
            base_prompt = f"A professional digital card celebrating {name}'s {years}-year work anniversary."
        
        # Personalize based on interests
        if primary_interest:
            interest_prompt = f" The design incorporates elements of {primary_interest}"
            if other_interests and len(other_interests) > 0:
                additional = ", ".join(other_interests[:1])  # Limit to first other interest
                interest_prompt += f" with subtle references to {additional}"
            base_prompt += interest_prompt
        
        # Add styling elements based on milestone
        if years == 1:
            style_prompt = " The image has a fresh, optimistic feel with bright colors. It includes a '1 Year' text prominently displayed with congratulatory elements."
        elif years <= 5:
            style_prompt = f" The image has a polished, professional look with vibrant colors and a '{years} Years' text prominently displayed with celebratory elements."
        elif years <= 10:
            style_prompt = f" The image has a distinguished appearance with rich colors, possibly gold or silver accents. It includes a '{years} Years' text prominently displayed with achievement symbolism."
        else:
            style_prompt = f" The image has a prestigious, distinguished appearance with elegant colors and gold accents. It includes a '{years} Years' text prominently displayed with symbols of accomplishment and legacy."
        
        return base_prompt + style_prompt
    
    def _generate_and_save_image(self, staff, event_type, prompt):
        """
        Generate an image using Amazon Bedrock and save it.
        
        Args:
            staff (Staff): Staff member
            event_type (str): Type of event ("birthday" or "anniversary_Xyr")
            prompt (str): Image generation prompt
            
        Returns:
            str: Path or URL to the generated image
        """
        if self._is_development():
            # In development mode, return a placeholder URL
            logger.info(f"[DEV MODE] Would generate image with prompt: {prompt[:100]}...")
            return self._get_placeholder_image_path(staff.id, event_type)
        
        try:
            # Call Amazon Bedrock Canvas
            response = self.bedrock_client.invoke_model(
                modelId=self.image_model_id,
                body=json.dumps({
                    "prompt": prompt,
                    "width": 1024,
                    "height": 768
                })
            )
            
            # Process the response to get the image data
            response_body = json.loads(response.get('body').read())
            image_data = response_body.get('images', [None])[0]
            
            if not image_data:
                logger.error("No image data in the response")
                return self._get_placeholder_image_path(staff.id, event_type)
            
            # Save the image to disk
            return self._save_image(staff.id, event_type, image_data)
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._get_placeholder_image_path(staff.id, event_type)
    
    def _save_image(self, staff_id, event_type, image_data):
        """
        Save an image to disk.
        
        Args:
            staff_id (int): Staff ID
            event_type (str): Type of event
            image_data (str): Base64-encoded image data
            
        Returns:
            str: Path to the saved image
        """
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{staff_id}_{event_type}_{timestamp}.png"
            file_path = self.image_dir / filename
            
            # Write the image to disk
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"Image saved to {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return self._get_placeholder_image_path(staff_id, event_type)
    
    def _get_placeholder_image_path(self, staff_id, event_type):
        """
        Get a path for a placeholder image.
        
        Args:
            staff_id (int): Staff ID
            event_type (str): Type of event
            
        Returns:
            str: Path to a placeholder image
        """
        # In a real implementation, you might have default images for different events
        if "birthday" in event_type:
            return "placeholder_birthday.png"
        elif "anniversary" in event_type:
            return "placeholder_anniversary.png"
        else:
            return "placeholder_generic.png"
    
    def _is_development(self):
        """
        Check if the application is running in development mode.
        
        Returns:
            bool: True if in development mode
        """
        return self.config.debug or not (self.config.aws_access_key_id and self.config.aws_secret_access_key)