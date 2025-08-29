"""Tests for database models."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from office_cheer.db.models import Staff


class TestStaffModel:
    """Test suite for the Staff model."""
    
    def test_create_staff(self, db_session):
        """Test creating a staff member."""
        # Create a new staff member
        staff = Staff(
            name="Test User",
            email_address="test@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1)
        )
        
        db_session.add(staff)
        db_session.commit()
        
        # Verify it was created
        result = db_session.query(Staff).filter_by(email_address="test@example.com").first()
        assert result is not None
        assert result.name == "Test User"
        assert result.birthday == date(1990, 1, 1)
        assert result.start_date == date(2020, 1, 1)
        assert result.alias is None
        assert result.interests is None
    
    def test_create_staff_with_optional_fields(self, db_session):
        """Test creating a staff member with optional fields."""
        # Create a new staff member with optional fields
        staff = Staff(
            name="Test User",
            email_address="test@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1),
            alias="Tester",
            interests="coding, reading"
        )
        
        db_session.add(staff)
        db_session.commit()
        
        # Verify all fields were saved
        result = db_session.query(Staff).filter_by(email_address="test@example.com").first()
        assert result.alias == "Tester"
        assert result.interests == "coding, reading"
    
    def test_staff_unique_email(self, db_session):
        """Test that email addresses must be unique."""
        # Create first staff member
        staff1 = Staff(
            name="User One",
            email_address="duplicate@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1)
        )
        db_session.add(staff1)
        db_session.commit()
        
        # Try to create another with the same email
        staff2 = Staff(
            name="User Two",
            email_address="duplicate@example.com",
            birthday=date(1995, 2, 2),
            start_date=date(2021, 2, 2)
        )
        db_session.add(staff2)
        
        # Should raise an IntegrityError
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_get_display_name(self, db_session):
        """Test the get_display_name method."""
        # Staff with alias
        staff_with_alias = Staff(
            name="Full Name",
            email_address="alias@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1),
            alias="Nickname"
        )
        
        # Staff without alias
        staff_without_alias = Staff(
            name="Full Name",
            email_address="no_alias@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1)
        )
        
        # Check that the display name is the alias when present
        assert staff_with_alias.get_display_name() == "Nickname"
        
        # Check that the display name is the full name when no alias
        assert staff_without_alias.get_display_name() == "Full Name"
    
    def test_get_interests_list(self, db_session):
        """Test the get_interests_list method."""
        # Staff with multiple interests
        staff_with_interests = Staff(
            name="Interest User",
            email_address="interests@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1),
            interests="coding, reading, hiking"
        )
        
        # Staff with one interest
        staff_one_interest = Staff(
            name="One Interest",
            email_address="one@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1),
            interests="gaming"
        )
        
        # Staff with no interests
        staff_no_interests = Staff(
            name="No Interests",
            email_address="none@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1)
        )
        
        # Check multiple interests
        assert staff_with_interests.get_interests_list() == ["coding", "reading", "hiking"]
        
        # Check single interest
        assert staff_one_interest.get_interests_list() == ["gaming"]
        
        # Check no interests
        assert staff_no_interests.get_interests_list() == []
    
    def test_from_dict(self):
        """Test creating a Staff instance from a dictionary."""
        # Complete data
        staff_data = {
            "name": "Dict User",
            "email_address": "dict@example.com",
            "birthday": "1990-03-15",
            "start_date": "2019-07-01",
            "alias": "Dictator",
            "interests": "python, testing, databases"
        }
        
        staff = Staff.from_dict(staff_data)
        
        assert staff.name == "Dict User"
        assert staff.email_address == "dict@example.com"
        assert staff.birthday == date(1990, 3, 15)
        assert staff.start_date == date(2019, 7, 1)
        assert staff.alias == "Dictator"
        assert staff.interests == "python, testing, databases"
        
        # Test with date objects instead of strings
        staff_data_with_dates = {
            "name": "Date User",
            "email_address": "date@example.com",
            "birthday": date(1990, 3, 15),
            "start_date": date(2019, 7, 1)
        }
        
        staff = Staff.from_dict(staff_data_with_dates)
        assert staff.birthday == date(1990, 3, 15)
        assert staff.start_date == date(2019, 7, 1)
    
    def test_from_dict_missing_required(self):
        """Test that from_dict raises an error if required fields are missing."""
        # Missing email
        staff_data_missing_email = {
            "name": "Missing Email",
            "birthday": "1990-03-15",
            "start_date": "2019-07-01"
        }
        
        with pytest.raises(ValueError):
            Staff.from_dict(staff_data_missing_email)
    
    def test_from_dict_invalid_date(self):
        """Test that from_dict raises an error for invalid date formats."""
        # Invalid birthday format
        staff_data_invalid_birthday = {
            "name": "Invalid Birthday",
            "email_address": "invalid@example.com",
            "birthday": "15/03/1990",  # Wrong format
            "start_date": "2019-07-01"
        }
        
        with pytest.raises(ValueError):
            Staff.from_dict(staff_data_invalid_birthday)