# ABOUTME: Date monitoring service for the Office Cheer application
# ABOUTME: Checks for upcoming birthdays and work anniversaries

import logging
from datetime import date, timedelta

from office_cheer.db import db_utils
from office_cheer.utils import date_utils

logger = logging.getLogger(__name__)

class DateMonitoringService:
    """
    Service for monitoring important dates such as birthdays and work anniversaries.
    This service works with the database to identify upcoming events.
    """
    
    def __init__(self, config):
        """
        Initialize the date monitoring service.
        
        Args:
            config (Config): Application configuration
        """
        self.config = config
        logger.info("Date monitoring service initialized")
    
    def get_upcoming_birthdays(self, days_ahead=None):
        """
        Get staff members with birthdays in the upcoming days.
        
        Args:
            days_ahead (int, optional): Number of days to look ahead, 
                                       defaults to config value
        
        Returns:
            list: List of Staff objects with upcoming birthdays
        """
        if days_ahead is None:
            days_ahead = self.config.lookforward_days
        
        logger.info(f"Checking for birthdays in the next {days_ahead} days")
        upcoming_birthdays = db_utils.get_upcoming_birthdays(days_ahead)
        
        if upcoming_birthdays:
            names = ", ".join([staff.name for staff in upcoming_birthdays])
            logger.info(f"Found {len(upcoming_birthdays)} upcoming birthdays: {names}")
        else:
            logger.info("No upcoming birthdays found")
        
        return upcoming_birthdays
    
    def get_upcoming_anniversaries(self, days_ahead=None):
        """
        Get staff members with work anniversaries in the upcoming days.
        Only returns milestone anniversaries (1 year, 5 years, 10 years, etc.).
        
        Args:
            days_ahead (int, optional): Number of days to look ahead, 
                                       defaults to config value
        
        Returns:
            list: List of tuples (Staff, years) for upcoming anniversaries
        """
        if days_ahead is None:
            days_ahead = self.config.lookforward_days
        
        logger.info(f"Checking for anniversaries in the next {days_ahead} days")
        upcoming_anniversaries = db_utils.get_upcoming_anniversaries(days_ahead)
        
        if upcoming_anniversaries:
            details = ", ".join([f"{staff.name} ({years} years)" 
                               for staff, years in upcoming_anniversaries])
            logger.info(f"Found {len(upcoming_anniversaries)} upcoming anniversaries: {details}")
        else:
            logger.info("No upcoming anniversaries found")
        
        return upcoming_anniversaries
    
    def get_today_birthdays(self):
        """
        Get staff members whose birthday is today.
        
        Returns:
            list: List of Staff objects with birthday today
        """
        logger.info("Checking for birthdays today")
        today_birthdays = db_utils.get_staff_with_birthday_today()
        
        if today_birthdays:
            names = ", ".join([staff.name for staff in today_birthdays])
            logger.info(f"Found {len(today_birthdays)} birthdays today: {names}")
        else:
            logger.info("No birthdays today")
        
        return today_birthdays
    
    def get_today_anniversaries(self):
        """
        Get staff members whose work anniversary is today.
        Only returns milestone anniversaries.
        
        Returns:
            list: List of tuples (Staff, years) for anniversaries today
        """
        logger.info("Checking for anniversaries today")
        today_anniversaries = db_utils.get_staff_with_anniversary_today()
        
        if today_anniversaries:
            details = ", ".join([f"{staff.name} ({years} years)" 
                               for staff, years in today_anniversaries])
            logger.info(f"Found {len(today_anniversaries)} anniversaries today: {details}")
        else:
            logger.info("No anniversaries today")
        
        return today_anniversaries
    
    def format_birthday_message(self, staff):
        """
        Format a basic birthday message for a staff member.
        This is a fallback if the agent-generated message fails.
        
        Args:
            staff (Staff): Staff member with birthday
            
        Returns:
            str: Formatted birthday message
        """
        display_name = staff.get_display_name()
        birthday_date = date_utils.format_date_display(staff.birthday)
        
        return (
            f"Happy Birthday, {display_name}! "
            f"Wishing you a wonderful celebration and a fantastic year ahead. "
            f"The entire team is sending their best wishes on your special day."
        )
    
    def format_anniversary_message(self, staff, years):
        """
        Format a basic work anniversary message for a staff member.
        This is a fallback if the agent-generated message fails.
        
        Args:
            staff (Staff): Staff member with anniversary
            years (int): Number of years
            
        Returns:
            str: Formatted anniversary message
        """
        display_name = staff.get_display_name()
        
        if years == 1:
            return (
                f"Congratulations on your first work anniversary, {display_name}! "
                f"Thank you for your contributions during your first year with us. "
                f"We look forward to many more years together!"
            )
        else:
            return (
                f"Congratulations on your {years}-year work anniversary, {display_name}! "
                f"Your dedication and contributions over the past {years} years "
                f"have been invaluable to our team. Thank you for your continued excellence!"
            )
    
    def days_to_next_birthday(self, staff, reference_date=None):
        """
        Calculate days until the next birthday for a staff member.
        
        Args:
            staff (Staff): Staff member
            reference_date (date, optional): Reference date, defaults to today
            
        Returns:
            int: Number of days until next birthday
        """
        return date_utils.days_until(staff.birthday, reference_date)
    
    def days_to_next_anniversary(self, staff, reference_date=None):
        """
        Calculate days until the next work anniversary for a staff member.
        
        Args:
            staff (Staff): Staff member
            reference_date (date, optional): Reference date, defaults to today
            
        Returns:
            int: Number of days until next anniversary
        """
        return date_utils.days_until(staff.start_date, reference_date)