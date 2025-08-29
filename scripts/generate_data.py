#!/usr/bin/env python3
# ABOUTME: Script to generate synthetic staff data for the Office Cheer application
# ABOUTME: Creates random staff records with realistic birthdays and start dates

import sys
import os
import random
from datetime import date, timedelta
import argparse

# Add parent directory to path to allow importing the application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from office_cheer.config import Config
from office_cheer.db.models import initialize_database, Staff
from office_cheer.db.db_utils import add_staff

# Lists for generating synthetic data
first_names = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", 
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", 
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Emily", "Paul", "Donna", "Andrew", "Michelle", "Joshua", "Carol",
    "Kenneth", "Amanda", "Kevin", "Melissa", "Brian", "Deborah", "George", "Stephanie"
]

last_names = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", 
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
    "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez",
    "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans"
]

interests = [
    "photography", "hiking", "cooking", "gardening", "reading", "traveling",
    "painting", "music", "dancing", "writing", "fishing", "gaming", "movies",
    "sports", "yoga", "cycling", "running", "swimming", "skiing", "technology",
    "cars", "fashion", "crafts", "history", "science", "animals", "coffee",
    "wine", "beer", "tea", "coding", "design", "astronomy", "bird watching",
    "woodworking", "knitting", "volunteering", "meditation", "camping", "sailing",
    "investing", "politics", "architecture", "languages", "theater", "concerts"
]

email_domains = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "example.com", "company.com", "organization.org", "enterprise.net"
]


def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


def generate_staff(count):
    """Generate a list of synthetic staff data."""
    staff_data = []
    today = date.today()
    
    # Use fixed range for plausible birth and start dates
    min_birth_year = today.year - 65  # Oldest employee is 65
    max_birth_year = today.year - 22  # Youngest employee is 22
    
    min_start_year = today.year - 25  # Longest tenure is 25 years
    max_start_year = today.year       # Some employees started this year
    
    used_emails = set()
    
    for _ in range(count):
        # Generate name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate unique email
        email = None
        while not email or email in used_emails:
            email_domain = random.choice(email_domains)
            email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"
        used_emails.add(email)
        
        # Generate dates
        birth_year = random.randint(min_birth_year, max_birth_year)
        birth_start = date(birth_year, 1, 1)
        birth_end = date(birth_year, 12, 31)
        birthday = random_date(birth_start, birth_end)
        
        start_year = random.randint(min_start_year, max_start_year)
        # Ensure start date is after person turns 22
        min_start_date = max(date(start_year, 1, 1), date(birth_year + 22, birthday.month, birthday.day))
        max_start_date = date(start_year, 12, 31)
        if min_start_date > max_start_date:
            # If constraints make this impossible, adjust the year
            min_start_date = date(start_year + 1, 1, 1)
            max_start_date = date(start_year + 1, 12, 31)
        start_date = random_date(min_start_date, max_start_date)
        
        # Generate interests (2-5 random interests)
        num_interests = random.randint(2, 5)
        staff_interests = random.sample(interests, num_interests)
        interests_str = ", ".join(staff_interests)
        
        # Generate alias (30% chance of having an alias)
        alias = None
        if random.random() < 0.3:
            alias = first_name[:3] if len(first_name) > 3 else first_name
        
        # Create staff data dictionary
        staff_data.append({
            "name": full_name,
            "email_address": email,
            "birthday": birthday,
            "start_date": start_date,
            "alias": alias,
            "interests": interests_str
        })
    
    return staff_data


def generate_upcoming_events():
    """
    Generate staff with birthdays and anniversaries in the next 14 days.
    This ensures we have some upcoming events to test with.
    """
    staff_data = []
    today = date.today()
    
    # Generate 2-4 upcoming birthdays
    for i in range(random.randint(2, 4)):
        days_ahead = random.randint(1, 14)
        upcoming_date = today + timedelta(days=days_ahead)
        
        birth_year = random.randint(today.year - 60, today.year - 25)
        birthday = date(birth_year, upcoming_date.month, upcoming_date.day)
        
        start_year = random.randint(today.year - 20, today.year - 1)
        start_date = date(start_year, random.randint(1, 12), random.randint(1, 28))
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name} (Birthday in {days_ahead} days)"
        
        email = f"{first_name.lower()}.{last_name.lower()}.bday{i}@example.com"
        
        staff_data.append({
            "name": full_name,
            "email_address": email,
            "birthday": birthday,
            "start_date": start_date,
            "interests": ", ".join(random.sample(interests, 3))
        })
    
    # Generate 2-4 upcoming anniversaries
    for i in range(random.randint(2, 4)):
        days_ahead = random.randint(1, 14)
        upcoming_date = today + timedelta(days=days_ahead)
        
        # Pick milestone years: 1, 5, 10, etc.
        years_options = [1, 5, 10, 15, 20, 25]
        years_ago = random.choice(years_options)
        
        start_date = date(today.year - years_ago, upcoming_date.month, upcoming_date.day)
        
        birth_year = random.randint(today.year - 60, today.year - 25)
        birthday = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name} ({years_ago}-year Anniversary in {days_ahead} days)"
        
        email = f"{first_name.lower()}.{last_name.lower()}.anniv{i}@example.com"
        
        staff_data.append({
            "name": full_name,
            "email_address": email,
            "birthday": birthday,
            "start_date": start_date,
            "interests": ", ".join(random.sample(interests, 3))
        })
    
    return staff_data


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic staff data for Office Cheer")
    parser.add_argument("--count", type=int, default=20, help="Number of staff records to generate")
    parser.add_argument("--include-events", action="store_true", help="Include staff with upcoming events")
    args = parser.parse_args()
    
    print(f"Initializing database...")
    config = Config()
    initialize_database(config.database_path)
    
    # Generate regular staff data
    staff_data = generate_staff(args.count)
    
    # Add staff with upcoming events if requested
    if args.include_events:
        event_staff = generate_upcoming_events()
        staff_data.extend(event_staff)
    
    print(f"Adding {len(staff_data)} staff records to the database...")
    
    success_count = 0
    for data in staff_data:
        staff = add_staff(data)
        if staff:
            success_count += 1
            print(f"Added: {staff.name} (Birthday: {staff.birthday}, Start date: {staff.start_date})")
    
    print(f"\nSuccessfully added {success_count} out of {len(staff_data)} staff records.")
    
    if args.include_events:
        print("\nUpcoming events were generated. To see them, run:")
        print("office-cheer events upcoming --days 14")


if __name__ == "__main__":
    main()