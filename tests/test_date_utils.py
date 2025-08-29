"""Tests for date utilities."""
import pytest
from datetime import date, timedelta

from office_cheer.utils.date_utils import (
    same_month_day, days_until, years_between, is_within_days, 
    format_date_display, get_next_occurrence, is_milestone_anniversary
)


class TestDateUtils:
    """Test suite for date utility functions."""
    
    def test_same_month_day(self):
        """Test same_month_day function."""
        # Same month and day, different year
        assert same_month_day(date(2020, 5, 15), date(2021, 5, 15)) is True
        
        # Different month
        assert same_month_day(date(2020, 5, 15), date(2020, 6, 15)) is False
        
        # Different day
        assert same_month_day(date(2020, 5, 15), date(2020, 5, 16)) is False
        
        # Different month and day
        assert same_month_day(date(2020, 5, 15), date(2020, 6, 16)) is False
    
    def test_days_until(self):
        """Test days_until function."""
        today = date(2023, 6, 1)  # Fixed date for testing
        
        # Birthday later this year
        assert days_until(date(2000, 6, 15), today) == 14
        
        # Birthday already passed this year
        assert days_until(date(2000, 5, 15), today) == 348  # Next year's birthday
        
        # Birthday is today
        assert days_until(date(2000, 6, 1), today) == 0
    
    def test_years_between(self):
        """Test years_between function."""
        today = date(2023, 6, 1)  # Fixed date for testing
        
        # Exactly 5 years
        assert years_between(date(2018, 6, 1), today) == 5
        
        # Almost 5 years (one day short)
        assert years_between(date(2018, 6, 2), today) == 4
        
        # More than 5 years
        assert years_between(date(2018, 5, 31), today) == 5
        
        # Less than a year
        assert years_between(date(2022, 7, 1), today) == 0
    
    def test_is_within_days(self):
        """Test is_within_days function."""
        today = date(2023, 6, 1)  # Fixed date for testing
        
        # Today
        assert is_within_days(date(2000, 6, 1), 7, today) is True
        
        # Within next 7 days
        assert is_within_days(date(2000, 6, 5), 7, today) is True
        
        # Exactly 7 days away
        assert is_within_days(date(2000, 6, 8), 7, today) is True
        
        # More than 7 days away
        assert is_within_days(date(2000, 6, 9), 7, today) is False
        
        # Past date this year (should check next year)
        assert is_within_days(date(2000, 5, 25), 7, today) is False
    
    def test_format_date_display(self):
        """Test format_date_display function."""
        # Regular date
        assert format_date_display(date(2023, 5, 15)) == "May 15th"
        
        # Dates with special suffixes
        assert format_date_display(date(2023, 5, 1)) == "May 1st"
        assert format_date_display(date(2023, 5, 2)) == "May 2nd"
        assert format_date_display(date(2023, 5, 3)) == "May 3rd"
        assert format_date_display(date(2023, 5, 4)) == "May 4th"
        
        # Dates with "th" suffix due to 11-13 special case
        assert format_date_display(date(2023, 5, 11)) == "May 11th"
        assert format_date_display(date(2023, 5, 12)) == "May 12th"
        assert format_date_display(date(2023, 5, 13)) == "May 13th"
    
    def test_get_next_occurrence(self):
        """Test get_next_occurrence function."""
        today = date(2023, 6, 1)  # Fixed date for testing
        
        # Future date this year
        future_date = date(2000, 6, 15)
        assert get_next_occurrence(future_date, today) == date(2023, 6, 15)
        
        # Past date this year
        past_date = date(2000, 5, 15)
        assert get_next_occurrence(past_date, today) == date(2024, 5, 15)
        
        # Today
        same_date = date(2000, 6, 1)
        assert get_next_occurrence(same_date, today) == date(2023, 6, 1)
    
    def test_is_milestone_anniversary(self):
        """Test is_milestone_anniversary function."""
        # First year is a milestone
        assert is_milestone_anniversary(1) is True
        
        # 5, 10, 15, etc. are milestones
        assert is_milestone_anniversary(5) is True
        assert is_milestone_anniversary(10) is True
        assert is_milestone_anniversary(15) is True
        assert is_milestone_anniversary(20) is True
        
        # Non-milestone years
        assert is_milestone_anniversary(2) is False
        assert is_milestone_anniversary(7) is False
        assert is_milestone_anniversary(13) is False
        
        # Zero is not a milestone
        assert is_milestone_anniversary(0) is False