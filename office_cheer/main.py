#!/usr/bin/env python3
# ABOUTME: Main entry point for the Office Cheer application
# ABOUTME: Coordinates services and schedules daily checks for events

import logging
import schedule
import time
import sys
from datetime import datetime

from office_cheer.config import Config
from office_cheer.db.models import initialize_database
from office_cheer.services.date_service import DateMonitoringService
from office_cheer.services.email_service import EmailService
from office_cheer.services.image_service import ImageService
from office_cheer.agents.greeting_agent import create_greeting_agent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class OfficeCheers:
    """Main application class that coordinates all services."""
    
    def __init__(self):
        """Initialize the application and its services."""
        self.config = Config()
        initialize_database(self.config.database_path)
        
        self.date_service = DateMonitoringService(self.config)
        self.image_service = ImageService(self.config)
        self.email_service = EmailService(self.config)
        self.greeting_agent = create_greeting_agent(self.config)
        
        logger.info("Office Cheer application initialized")
    
    def check_events(self):
        """
        Check for upcoming birthdays and anniversaries and process them.
        This is the main function that will be scheduled to run daily.
        """
        logger.info("Checking for upcoming events...")
        
        # Get upcoming birthdays and anniversaries
        lookforward_days = self.config.lookforward_days
        upcoming_birthdays = self.date_service.get_upcoming_birthdays(lookforward_days)
        upcoming_anniversaries = self.date_service.get_upcoming_anniversaries(lookforward_days)
        
        # Process birthdays
        for staff in upcoming_birthdays:
            try:
                self._process_birthday(staff)
            except Exception as e:
                logger.error(f"Error processing birthday for {staff.name}: {e}")
        
        # Process anniversaries
        for staff, years in upcoming_anniversaries:
            try:
                self._process_anniversary(staff, years)
            except Exception as e:
                logger.error(f"Error processing anniversary for {staff.name}: {e}")
    
    def _process_birthday(self, staff):
        """Process a birthday event for a staff member."""
        logger.info(f"Processing birthday for {staff.name}")
        
        # Generate greeting content
        greeting_content = self.greeting_agent.generate_birthday_greeting(staff)
        
        # Generate image
        image_url = self.image_service.generate_birthday_image(staff)
        
        # Send email
        self.email_service.send_birthday_email(staff, greeting_content, image_url)
        
        logger.info(f"Birthday processed successfully for {staff.name}")
    
    def _process_anniversary(self, staff, years):
        """Process a work anniversary event for a staff member."""
        logger.info(f"Processing {years}-year anniversary for {staff.name}")
        
        # Generate greeting content
        greeting_content = self.greeting_agent.generate_anniversary_greeting(staff, years)
        
        # Generate image
        image_url = self.image_service.generate_anniversary_image(staff, years)
        
        # Send email
        self.email_service.send_anniversary_email(staff, years, greeting_content, image_url)
        
        logger.info(f"Anniversary processed successfully for {staff.name}")
    
    def run(self):
        """Run the application, setting up the schedule and entering the main loop."""
        # Schedule the daily check
        check_time = self.config.daily_check_time
        schedule.every().day.at(check_time).do(self.check_events)
        logger.info(f"Scheduled daily check at {check_time}")
        
        # Run check_events immediately on startup (optional)
        if self.config.check_on_startup:
            logger.info("Running initial check on startup")
            self.check_events()
        
        # Main loop
        logger.info("Entering main loop")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Sleep for 1 minute between checks


def main():
    """Entry point for the application."""
    try:
        app = OfficeCheers()
        app.run()
    except Exception as e:
        logger.critical(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()