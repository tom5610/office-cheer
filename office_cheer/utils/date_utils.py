# ABOUTME: Date utility functions for the Office Cheer application
# ABOUTME: Provides helper functions for date comparisons, calculations and formatting

from datetime import date, datetime, timedelta
import calendar

def same_month_day(date1, date2):
    """
    Check if two dates have the same month and day (ignoring year).
    
    Args:
        date1 (date): First date
        date2 (date): Second date
        
    Returns:
        bool: True if month and day are the same
    """
    return date1.month == date2.month and date1.day == date2.day


def days_until(target_date, from_date=None):
    """
    Calculate days until a target date.
    If the target date is in the past for this year, calculate for next year.
    
    Args:
        target_date (date): Target date
        from_date (date, optional): Reference date, defaults to today
        
    Returns:
        int: Number of days until the target date
    """
    if from_date is None:
        from_date = date.today()
    
    # Create a date for this year with the same month and day as the target
    this_year_date = date(from_date.year, target_date.month, target_date.day)
    
    # If the date has already passed this year, use next year
    if this_year_date < from_date:
        this_year_date = date(from_date.year + 1, target_date.month, target_date.day)
    
    return (this_year_date - from_date).days


def years_between(start_date, end_date=None):
    """
    Calculate the number of years between two dates.
    
    Args:
        start_date (date): Start date
        end_date (date, optional): End date, defaults to today
        
    Returns:
        int: Number of years
    """
    if end_date is None:
        end_date = date.today()
    
    years = end_date.year - start_date.year
    
    # Adjust if the end date is before the anniversary in the current year
    if end_date.month < start_date.month or (
            end_date.month == start_date.month and end_date.day < start_date.day):
        years -= 1
    
    return years


def is_within_days(check_date, days, from_date=None):
    """
    Check if a date falls within a specified number of days from a reference date.
    
    Args:
        check_date (date): Date to check
        days (int): Number of days to check ahead
        from_date (date, optional): Reference date, defaults to today
        
    Returns:
        bool: True if the date falls within the specified range
    """
    if from_date is None:
        from_date = date.today()
    
    # Create a date for this year with the same month and day as the check date
    this_year_date = date(from_date.year, check_date.month, check_date.day)
    
    # If the date has already passed this year, use next year
    if this_year_date < from_date:
        this_year_date = date(from_date.year + 1, check_date.month, check_date.day)
    
    return 0 <= (this_year_date - from_date).days <= days


def format_date_display(input_date):
    """
    Format a date for display in greeting cards and emails.
    
    Args:
        input_date (date): Date to format
        
    Returns:
        str: Formatted date string (e.g., "August 15th")
    """
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    day = input_date.day
    
    # Handle special cases for 11th, 12th, 13th
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = suffixes.get(day % 10, 'th')
    
    return f"{calendar.month_name[input_date.month]} {day}{suffix}"


def get_next_occurrence(event_date, reference_date=None):
    """
    Get the next occurrence of a recurring event date.
    
    Args:
        event_date (date): The original event date
        reference_date (date, optional): Reference date, defaults to today
        
    Returns:
        date: Date of the next occurrence
    """
    if reference_date is None:
        reference_date = date.today()
    
    # Create a date for this year with the same month and day as the event
    this_year_date = date(reference_date.year, event_date.month, event_date.day)
    
    # If the date has already passed this year, use next year
    if this_year_date < reference_date:
        this_year_date = date(reference_date.year + 1, event_date.month, event_date.day)
    
    return this_year_date


def is_milestone_anniversary(years):
    """
    Check if a number of years represents a milestone anniversary.
    
    Args:
        years (int): Number of years
        
    Returns:
        bool: True if it's a milestone anniversary (1, 5, 10, 15, etc.)
    """
    return years == 1 or (years > 0 and years % 5 == 0)


# Testing the date utilities
if __name__ == "__main__":
    # Example usage and tests
    today = date.today()
    birthday = date(1990, 8, 15)
    start_date = date(2015, 4, 20)
    
    print(f"Today: {today}")
    print(f"Birthday: {birthday}")
    print(f"Start date: {start_date}")
    print(f"Days until next birthday: {days_until(birthday)}")
    print(f"Years of service: {years_between(start_date)}")
    print(f"Is birthday within next 30 days: {is_within_days(birthday, 30)}")
    print(f"Formatted birthday: {format_date_display(birthday)}")
    print(f"Next birthday: {get_next_occurrence(birthday)}")
    print(f"Is 5 years a milestone: {is_milestone_anniversary(5)}")
    print(f"Is 7 years a milestone: {is_milestone_anniversary(7)}")