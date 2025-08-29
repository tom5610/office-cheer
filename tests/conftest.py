"""Test configuration for pytest."""
import os
import pytest
import tempfile
from datetime import date

from office_cheer.config import Config
from office_cheer.db.models import initialize_database, Staff, Base
from office_cheer.services.date_service import DateMonitoringService
from office_cheer.services.email_service import EmailService
from office_cheer.services.image_service import ImageService

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def test_config():
    """Create a test configuration."""
    config = Config()
    config.debug = True  # Always use debug mode in tests
    config.database_path = "sqlite:///:memory:"
    return config


@pytest.fixture
def db_session(test_config):
    """Create a test database session."""
    # Create engine and tables
    engine = create_engine(test_config.database_path)
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # Clean up
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_staff():
    """Create a list of test staff members."""
    return [
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


@pytest.fixture
def populate_db(db_session, test_staff):
    """Populate the database with test staff."""
    for staff in test_staff:
        db_session.add(staff)
    db_session.commit()
    return db_session


@pytest.fixture
def date_service(test_config):
    """Create a date monitoring service."""
    return DateMonitoringService(test_config)


@pytest.fixture
def email_service(test_config):
    """Create an email service."""
    return EmailService(test_config)


@pytest.fixture
def image_service(test_config):
    """Create an image service."""
    return ImageService(test_config)