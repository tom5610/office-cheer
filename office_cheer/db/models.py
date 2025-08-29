# ABOUTME: Database models for the Office Cheer application
# ABOUTME: Defines the Staff model and database initialization functions

import os
import logging
from datetime import date
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class Staff(Base):
    """
    Staff model representing an employee with birthday and anniversary information.
    This is the primary model used for tracking events and generating greetings.
    """
    __tablename__ = 'staff'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    alias = Column(String(50), nullable=True)  # Nickname or preferred name
    email_address = Column(String(100), nullable=False, unique=True)
    birthday = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    interests = Column(String(500), nullable=True)  # Comma-separated list of interests
    
    def __init__(self, name, email_address, birthday, start_date, alias=None, interests=None):
        """
        Initialize a Staff instance.
        
        Args:
            name (str): Full name of the employee
            email_address (str): Email address for communication
            birthday (date): Date of birth for birthday monitoring
            start_date (date): Employment start date for work anniversaries
            alias (str, optional): Nickname or preferred name
            interests (str, optional): Comma-separated list of interests
        """
        self.name = name
        self.email_address = email_address
        self.birthday = birthday
        self.start_date = start_date
        self.alias = alias
        self.interests = interests
    
    def __repr__(self):
        """String representation of the Staff object."""
        return f"<Staff(id={self.id}, name='{self.name}', email='{self.email_address}')>"
    
    def get_display_name(self):
        """Get the display name (alias if available, otherwise name)."""
        return self.alias if self.alias else self.name
    
    def get_interests_list(self):
        """Get the list of interests from the comma-separated string."""
        if not self.interests:
            return []
        return [interest.strip() for interest in self.interests.split(',')]
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Staff instance from a dictionary.
        
        Args:
            data (dict): Dictionary with staff data
            
        Returns:
            Staff: New Staff instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['name', 'email_address', 'birthday', 'start_date']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert date strings to date objects if needed
        birthday = data['birthday']
        if isinstance(birthday, str):
            try:
                birthday = date.fromisoformat(birthday)
            except ValueError:
                raise ValueError(f"Invalid birthday format: {birthday}. Use YYYY-MM-DD.")
        
        start_date = data['start_date']
        if isinstance(start_date, str):
            try:
                start_date = date.fromisoformat(start_date)
            except ValueError:
                raise ValueError(f"Invalid start_date format: {start_date}. Use YYYY-MM-DD.")
        
        return cls(
            name=data['name'],
            email_address=data['email_address'],
            birthday=birthday,
            start_date=start_date,
            alias=data.get('alias'),
            interests=data.get('interests')
        )


# Database connection and session management
_engine = None
Session = None


def initialize_database(database_url):
    """
    Initialize the database connection and create tables if they don't exist.
    
    Args:
        database_url (str): SQLAlchemy database URL
        
    Returns:
        bool: True if initialization was successful
    """
    global _engine, Session
    
    try:
        # Create engine and tables
        _engine = create_engine(database_url)
        Base.metadata.create_all(_engine)
        
        # Create session factory
        Session = sessionmaker(bind=_engine)
        
        logger.info(f"Database initialized successfully at {database_url}")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


def get_session():
    """
    Get a new database session.
    
    Returns:
        Session: SQLAlchemy Session object
        
    Raises:
        RuntimeError: If the database has not been initialized
    """
    if Session is None:
        raise RuntimeError("Database not initialized. Call initialize_database first.")
    return Session()


# Example of creating test data
def create_test_data():
    """Create test data in the database for development and testing."""
    session = get_session()
    try:
        # Only add test data if the table is empty
        if session.query(Staff).count() == 0:
            test_staff = [
                Staff(
                    name="John Doe",
                    email_address="john.doe@example.com",
                    birthday=date(1980, 5, 15),
                    start_date=date(2020, 3, 10),
                    alias="Johnny",
                    interests="hiking, photography, cooking"
                ),
                Staff(
                    name="Jane Smith",
                    email_address="jane.smith@example.com",
                    birthday=date(1985, 8, 22),
                    start_date=date(2018, 6, 1),
                    interests="reading, travel, music"
                ),
                Staff(
                    name="Mike Johnson",
                    email_address="mike.johnson@example.com",
                    birthday=date(1975, 2, 28),
                    start_date=date(2015, 9, 15),
                    alias="MJ",
                    interests="sports, gaming, movies"
                )
            ]
            session.add_all(test_staff)
            session.commit()
            logger.info("Test data created successfully")
        else:
            logger.info("Database already contains data, skipping test data creation")
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating test data: {e}")
    finally:
        session.close()