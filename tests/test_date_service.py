"""Tests for date monitoring service."""
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from office_cheer.services.date_service import DateMonitoringService
from office_cheer.db.models import Staff


class TestDateMonitoringService:
    """Test suite for the DateMonitoringService class."""
    
    def test_get_upcoming_birthdays(self, date_service, populate_db, test_staff):
        """Test getting upcoming birthdays."""
        # Mock today's date to a fixed value
        with patch('office_cheer.db.db_utils.date') as mock_date:
            # Set today to January 1, 2023
            mock_date.today.return_value = date(2023, 1, 1)
            
            # Mike's birthday is February 28, which is within the next 60 days
            upcoming_birthdays = date_service.get_upcoming_birthdays(60)
            
            assert len(upcoming_birthdays) == 1
            assert upcoming_birthdays[0].name == "Mike Johnson"
    
    def test_get_upcoming_anniversaries(self, date_service, populate_db, test_staff):
        """Test getting upcoming anniversaries."""
        # Mock today's date to a fixed value
        with patch('office_cheer.db.db_utils.date') as mock_date:
            # Set today to January 1, 2023
            mock_date.today.return_value = date(2023, 1, 1)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs) if args else date(2023, 1, 1)
            
            # The 5-year anniversary for Jane is coming up on June 1, 2023
            # Since it's a milestone (5 years), it should be included
            upcoming_anniversaries = date_service.get_upcoming_anniversaries(365)  # Look ahead a full year
            
            # We should find at least one milestone anniversary
            assert len(upcoming_anniversaries) >= 1
            
            # Check that Jane's 5-year anniversary is found
            found_jane = False
            for staff, years in upcoming_anniversaries:
                if staff.name == "Jane Smith" and years == 5:
                    found_jane = True
                    break
            
            assert found_jane, "Jane's 5-year anniversary was not found"
    
    def test_get_today_birthdays(self, date_service, populate_db, test_staff):
        """Test getting birthdays that fall on today's date."""
        # Mock today's date to match John's birthday
        with patch('office_cheer.db.db_utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 5, 15)  # John's birthday is May 15
            
            today_birthdays = date_service.get_today_birthdays()
            
            assert len(today_birthdays) == 1
            assert today_birthdays[0].name == "John Doe"
    
    def test_get_today_anniversaries(self, date_service, populate_db, test_staff):
        """Test getting anniversaries that fall on today's date."""
        # Mock today's date to match Jane's start date
        with patch('office_cheer.db.db_utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 6, 1)  # Jane's start date is June 1
            
            # This is her 5-year anniversary (2018 -> 2023)
            today_anniversaries = date_service.get_today_anniversaries()
            
            assert len(today_anniversaries) == 1
            assert today_anniversaries[0][0].name == "Jane Smith"
            assert today_anniversaries[0][1] == 5  # 5 years
    
    def test_format_birthday_message(self, date_service):
        """Test formatting a birthday message."""
        staff = Staff(
            name="Test User",
            email_address="test@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1),
            alias="Tester"
        )
        
        message = date_service.format_birthday_message(staff)
        
        # Check that the message contains the display name
        assert "Tester" in message
        assert "Birthday" in message or "birthday" in message
    
    def test_format_anniversary_message(self, date_service):
        """Test formatting an anniversary message."""
        staff = Staff(
            name="Test User",
            email_address="test@example.com",
            birthday=date(1990, 1, 1),
            start_date=date(2020, 1, 1),
            alias="Tester"
        )
        
        # Test first year message
        first_year_message = date_service.format_anniversary_message(staff, 1)
        assert "Tester" in first_year_message
        assert "first" in first_year_message.lower()
        
        # Test multi-year message
        five_year_message = date_service.format_anniversary_message(staff, 5)
        assert "Tester" in five_year_message
        assert "5" in five_year_message or "five" in five_year_message.lower()
    
    def test_days_to_next_birthday(self, date_service):
        """Test calculating days to next birthday."""
        # Mock today's date
        with patch('office_cheer.utils.date_utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 1, 1)
            
            # Birthday later this year
            staff_future_birthday = Staff(
                name="Future Birthday",
                email_address="future@example.com",
                birthday=date(1990, 3, 15),  # March 15
                start_date=date(2020, 1, 1)
            )
            
            # Birthday already passed this year
            staff_past_birthday = Staff(
                name="Past Birthday",
                email_address="past@example.com",
                birthday=date(1990, 12, 25),  # December 25
                start_date=date(2020, 1, 1)
            )
            
            # Check days to next birthday
            assert date_service.days_to_next_birthday(staff_future_birthday) == 73  # Jan 1 to Mar 15
            assert date_service.days_to_next_birthday(staff_past_birthday) == 358  # Jan 1 to Dec 25
    
    def test_days_to_next_anniversary(self, date_service):
        """Test calculating days to next work anniversary."""
        # Mock today's date
        with patch('office_cheer.utils.date_utils.date') as mock_date:
            mock_date.today.return_value = date(2023, 1, 1)
            
            # Anniversary later this year
            staff_future_anniversary = Staff(
                name="Future Anniversary",
                email_address="future@example.com",
                birthday=date(1990, 1, 1),
                start_date=date(2020, 3, 15)  # March 15
            )
            
            # Anniversary already passed this year
            staff_past_anniversary = Staff(
                name="Past Anniversary",
                email_address="past@example.com",
                birthday=date(1990, 1, 1),
                start_date=date(2020, 12, 25)  # December 25
            )
            
            # Check days to next anniversary
            assert date_service.days_to_next_anniversary(staff_future_anniversary) == 73  # Jan 1 to Mar 15
            assert date_service.days_to_next_anniversary(staff_past_anniversary) == 358  # Jan 1 to Dec 25