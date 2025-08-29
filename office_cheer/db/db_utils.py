# ABOUTME: Database utility functions for the Office Cheer application
# ABOUTME: Provides CRUD operations and specialized queries for staff events

import logging
from datetime import date, datetime, timedelta
from sqlalchemy import extract
from sqlalchemy.exc import SQLAlchemyError

from office_cheer.db.models import Staff, get_session

logger = logging.getLogger(__name__)

# Staff CRUD operations

def add_staff(staff_data):
    """
    Add a new staff member to the database.
    
    Args:
        staff_data (dict): Dictionary with staff data
        
    Returns:
        Staff: Created Staff object or None if failed
    """
    session = get_session()
    try:
        staff = Staff.from_dict(staff_data)
        session.add(staff)
        session.commit()
        logger.info(f"Added new staff member: {staff.name} (ID: {staff.id})")
        return staff
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding staff member: {e}")
        return None
    finally:
        session.close()


def get_staff_by_id(staff_id):
    """
    Get a staff member by ID.
    
    Args:
        staff_id (int): Staff ID
        
    Returns:
        Staff: Staff object or None if not found
    """
    session = get_session()
    try:
        staff = session.query(Staff).filter(Staff.id == staff_id).first()
        return staff
    except Exception as e:
        logger.error(f"Error retrieving staff member by ID {staff_id}: {e}")
        return None
    finally:
        session.close()


def get_staff_by_email(email):
    """
    Get a staff member by email address.
    
    Args:
        email (str): Email address
        
    Returns:
        Staff: Staff object or None if not found
    """
    session = get_session()
    try:
        staff = session.query(Staff).filter(Staff.email_address == email).first()
        return staff
    except Exception as e:
        logger.error(f"Error retrieving staff member by email {email}: {e}")
        return None
    finally:
        session.close()


def update_staff(staff_id, staff_data):
    """
    Update a staff member's information.
    
    Args:
        staff_id (int): Staff ID
        staff_data (dict): Dictionary with staff data to update
        
    Returns:
        bool: True if update was successful
    """
    session = get_session()
    try:
        staff = session.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            logger.warning(f"Staff member with ID {staff_id} not found")
            return False
        
        # Update fields that are present in the data
        for key, value in staff_data.items():
            if hasattr(staff, key):
                # Handle date conversions
                if key in ['birthday', 'start_date'] and isinstance(value, str):
                    value = date.fromisoformat(value)
                setattr(staff, key, value)
        
        session.commit()
        logger.info(f"Updated staff member: {staff.name} (ID: {staff.id})")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating staff member {staff_id}: {e}")
        return False
    finally:
        session.close()


def delete_staff(staff_id):
    """
    Delete a staff member.
    
    Args:
        staff_id (int): Staff ID
        
    Returns:
        bool: True if deletion was successful
    """
    session = get_session()
    try:
        staff = session.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            logger.warning(f"Staff member with ID {staff_id} not found")
            return False
        
        session.delete(staff)
        session.commit()
        logger.info(f"Deleted staff member: {staff.name} (ID: {staff.id})")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting staff member {staff_id}: {e}")
        return False
    finally:
        session.close()


def get_all_staff():
    """
    Get all staff members.
    
    Returns:
        list: List of Staff objects
    """
    session = get_session()
    try:
        staff_list = session.query(Staff).all()
        return staff_list
    except Exception as e:
        logger.error(f"Error retrieving all staff members: {e}")
        return []
    finally:
        session.close()


# Special queries for events

def get_upcoming_birthdays(days_ahead=7):
    """
    Get staff with birthdays in the next N days.
    
    Args:
        days_ahead (int): Number of days to look ahead
        
    Returns:
        list: List of Staff objects with upcoming birthdays
    """
    session = get_session()
    try:
        today = date.today()
        upcoming_staff = []
        
        # We need to check each staff member individually since SQLite doesn't have good date functions
        all_staff = session.query(Staff).all()
        
        for staff in all_staff:
            # Get this year's birthday
            this_year_bday = date(today.year, staff.birthday.month, staff.birthday.day)
            
            # If the birthday already passed this year, check next year's birthday
            if this_year_bday < today:
                this_year_bday = date(today.year + 1, staff.birthday.month, staff.birthday.day)
            
            # Check if the birthday is within the specified range
            if (this_year_bday - today).days <= days_ahead:
                upcoming_staff.append(staff)
        
        return upcoming_staff
    except Exception as e:
        logger.error(f"Error retrieving upcoming birthdays: {e}")
        return []
    finally:
        session.close()


def get_upcoming_anniversaries(days_ahead=7):
    """
    Get staff with work anniversaries in the next N days.
    
    Args:
        days_ahead (int): Number of days to look ahead
        
    Returns:
        list: List of tuples (Staff, years) with upcoming anniversaries
    """
    session = get_session()
    try:
        today = date.today()
        upcoming_anniversaries = []
        
        # We need to check each staff member individually
        all_staff = session.query(Staff).all()
        
        for staff in all_staff:
            # Get this year's anniversary
            this_year_anniversary = date(today.year, staff.start_date.month, staff.start_date.day)
            
            # If the anniversary already passed this year, check next year's anniversary
            if this_year_anniversary < today:
                this_year_anniversary = date(today.year + 1, staff.start_date.month, staff.start_date.day)
            
            # Check if the anniversary is within the specified range
            if (this_year_anniversary - today).days <= days_ahead:
                # Calculate years of service
                years = today.year - staff.start_date.year
                if today < date(today.year, staff.start_date.month, staff.start_date.day):
                    years -= 1
                
                # Only include milestone anniversaries (1, 5, 10, 15, etc.)
                if years > 0 and (years == 1 or years % 5 == 0):
                    upcoming_anniversaries.append((staff, years))
        
        return upcoming_anniversaries
    except Exception as e:
        logger.error(f"Error retrieving upcoming anniversaries: {e}")
        return []
    finally:
        session.close()


def get_staff_with_birthday_today():
    """
    Get staff members whose birthday is today.
    
    Returns:
        list: List of Staff objects with birthday today
    """
    session = get_session()
    try:
        today = date.today()
        
        birthday_staff = []
        all_staff = session.query(Staff).all()
        
        for staff in all_staff:
            if staff.birthday.month == today.month and staff.birthday.day == today.day:
                birthday_staff.append(staff)
        
        return birthday_staff
    except Exception as e:
        logger.error(f"Error retrieving staff with birthdays today: {e}")
        return []
    finally:
        session.close()


def get_staff_with_anniversary_today():
    """
    Get staff members whose work anniversary is today.
    
    Returns:
        list: List of tuples (Staff, years) with anniversary today
    """
    session = get_session()
    try:
        today = date.today()
        
        anniversary_staff = []
        all_staff = session.query(Staff).all()
        
        for staff in all_staff:
            if staff.start_date.month == today.month and staff.start_date.day == today.day:
                years = today.year - staff.start_date.year
                
                # Only include milestone anniversaries (1, 5, 10, 15, etc.)
                if years > 0 and (years == 1 or years % 5 == 0):
                    anniversary_staff.append((staff, years))
        
        return anniversary_staff
    except Exception as e:
        logger.error(f"Error retrieving staff with anniversaries today: {e}")
        return []
    finally:
        session.close()