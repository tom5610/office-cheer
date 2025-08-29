# ABOUTME: Command-line interface for the Office Cheer application
# ABOUTME: Provides commands for managing staff and testing functionality

import logging
import sys
import click
from datetime import datetime, date
import json

from office_cheer.config import Config
from office_cheer.db.models import initialize_database, create_test_data, Staff
from office_cheer.db.db_utils import (
    add_staff, get_staff_by_id, get_staff_by_email, update_staff, 
    delete_staff, get_all_staff, get_upcoming_birthdays, 
    get_upcoming_anniversaries
)
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


@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx, debug):
    """Office Cheer - Manage staff events and send personalized greetings."""
    # Initialize configuration
    config = Config()
    config.debug = debug
    
    # Initialize database
    initialize_database(config.database_path)
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@cli.group('staff')
def staff_group():
    """Manage staff members."""
    pass


@staff_group.command('list')
@click.pass_context
def list_staff(ctx):
    """List all staff members."""
    staff_list = get_all_staff()
    
    if not staff_list:
        click.echo("No staff members found.")
        return
    
    click.echo("\nStaff List:")
    click.echo("-" * 80)
    click.echo(f"{'ID':<4} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Start Date':<12}")
    click.echo("-" * 80)
    
    for staff in staff_list:
        click.echo(
            f"{staff.id:<4} {staff.name:<20} {staff.email_address:<25} "
            f"{staff.birthday.strftime('%Y-%m-%d'):<12} {staff.start_date.strftime('%Y-%m-%d'):<12}"
        )


@staff_group.command('add')
@click.option('--name', required=True, help='Full name of the staff member')
@click.option('--email', required=True, help='Email address')
@click.option('--birthday', required=True, help='Birthday in YYYY-MM-DD format')
@click.option('--start-date', required=True, help='Employment start date in YYYY-MM-DD format')
@click.option('--alias', help='Nickname or preferred name')
@click.option('--interests', help='Comma-separated list of interests')
@click.pass_context
def add_staff_member(ctx, name, email, birthday, start_date, alias, interests):
    """Add a new staff member."""
    try:
        # Parse dates
        birthday_date = date.fromisoformat(birthday)
        start_date_date = date.fromisoformat(start_date)
        
        # Create staff data dictionary
        staff_data = {
            'name': name,
            'email_address': email,
            'birthday': birthday_date,
            'start_date': start_date_date
        }
        
        if alias:
            staff_data['alias'] = alias
        
        if interests:
            staff_data['interests'] = interests
        
        # Add staff member
        staff = add_staff(staff_data)
        
        if staff:
            click.echo(f"Staff member added successfully with ID: {staff.id}")
        else:
            click.echo("Failed to add staff member.")
    
    except ValueError as e:
        click.echo(f"Error: {e}")


@staff_group.command('update')
@click.argument('staff_id', type=int)
@click.option('--name', help='Full name of the staff member')
@click.option('--email', help='Email address')
@click.option('--birthday', help='Birthday in YYYY-MM-DD format')
@click.option('--start-date', help='Employment start date in YYYY-MM-DD format')
@click.option('--alias', help='Nickname or preferred name')
@click.option('--interests', help='Comma-separated list of interests')
@click.pass_context
def update_staff_member(ctx, staff_id, name, email, birthday, start_date, alias, interests):
    """Update a staff member's information."""
    # Check if staff member exists
    staff = get_staff_by_id(staff_id)
    if not staff:
        click.echo(f"Staff member with ID {staff_id} not found.")
        return
    
    # Create staff data dictionary with only provided fields
    staff_data = {}
    
    if name:
        staff_data['name'] = name
    
    if email:
        staff_data['email_address'] = email
    
    if birthday:
        try:
            staff_data['birthday'] = date.fromisoformat(birthday)
        except ValueError:
            click.echo("Invalid birthday format. Use YYYY-MM-DD.")
            return
    
    if start_date:
        try:
            staff_data['start_date'] = date.fromisoformat(start_date)
        except ValueError:
            click.echo("Invalid start date format. Use YYYY-MM-DD.")
            return
    
    if alias is not None:  # Allow empty string to clear alias
        staff_data['alias'] = alias
    
    if interests is not None:  # Allow empty string to clear interests
        staff_data['interests'] = interests
    
    # Update staff member
    if update_staff(staff_id, staff_data):
        click.echo(f"Staff member with ID {staff_id} updated successfully.")
    else:
        click.echo(f"Failed to update staff member with ID {staff_id}.")


@staff_group.command('delete')
@click.argument('staff_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this staff member?')
@click.pass_context
def delete_staff_member(ctx, staff_id):
    """Delete a staff member."""
    if delete_staff(staff_id):
        click.echo(f"Staff member with ID {staff_id} deleted successfully.")
    else:
        click.echo(f"Failed to delete staff member with ID {staff_id}.")


@staff_group.command('show')
@click.argument('staff_id', type=int)
@click.pass_context
def show_staff_member(ctx, staff_id):
    """Show detailed information for a staff member."""
    staff = get_staff_by_id(staff_id)
    if not staff:
        click.echo(f"Staff member with ID {staff_id} not found.")
        return
    
    click.echo("\nStaff Details:")
    click.echo("-" * 50)
    click.echo(f"ID:            {staff.id}")
    click.echo(f"Name:          {staff.name}")
    click.echo(f"Alias:         {staff.alias or 'N/A'}")
    click.echo(f"Email:         {staff.email_address}")
    click.echo(f"Birthday:      {staff.birthday.strftime('%Y-%m-%d')}")
    click.echo(f"Start Date:    {staff.start_date.strftime('%Y-%m-%d')}")
    
    # Calculate years of service
    from office_cheer.utils.date_utils import years_between
    years = years_between(staff.start_date)
    click.echo(f"Years of Service: {years}")
    
    # Format interests
    interests = staff.get_interests_list()
    if interests:
        click.echo(f"Interests:     {', '.join(interests)}")
    else:
        click.echo("Interests:     None specified")


@cli.group('events')
def events_group():
    """Manage and check for upcoming events."""
    pass


@events_group.command('upcoming')
@click.option('--days', default=7, help='Number of days to look ahead')
@click.pass_context
def show_upcoming_events(ctx, days):
    """Show upcoming birthdays and anniversaries."""
    config = ctx.obj['config']
    date_service = DateMonitoringService(config)
    
    # Get upcoming events
    birthdays = date_service.get_upcoming_birthdays(days)
    anniversaries = date_service.get_upcoming_anniversaries(days)
    
    # Show birthdays
    if birthdays:
        click.echo(f"\nUpcoming Birthdays (next {days} days):")
        click.echo("-" * 60)
        for staff in birthdays:
            days_until = date_service.days_to_next_birthday(staff)
            when = "Today!" if days_until == 0 else f"In {days_until} days"
            click.echo(f"{staff.name:<20} - {staff.birthday.strftime('%m-%d')} - {when}")
    else:
        click.echo(f"\nNo upcoming birthdays in the next {days} days.")
    
    # Show anniversaries
    if anniversaries:
        click.echo(f"\nUpcoming Work Anniversaries (next {days} days):")
        click.echo("-" * 60)
        for staff, years in anniversaries:
            days_until = date_service.days_to_next_anniversary(staff)
            when = "Today!" if days_until == 0 else f"In {days_until} days"
            click.echo(f"{staff.name:<20} - {years} Years - {staff.start_date.strftime('%m-%d')} - {when}")
    else:
        click.echo(f"\nNo upcoming work anniversaries in the next {days} days.")


@events_group.command('process')
@click.option('--dry-run/--no-dry-run', default=True, 
              help='Dry run (no emails sent) or actual processing')
@click.pass_context
def process_events(ctx, dry_run):
    """Process today's events and send notifications."""
    config = ctx.obj['config']
    
    # Force debug mode in dry run
    if dry_run:
        config.debug = True
        click.echo("DRY RUN MODE - No emails will be sent")
    
    date_service = DateMonitoringService(config)
    email_service = EmailService(config)
    image_service = ImageService(config)
    
    try:
        greeting_agent = create_greeting_agent(config)
    except Exception as e:
        click.echo(f"Warning: Could not initialize greeting agent. Using fallback messages. Error: {e}")
        greeting_agent = None
    
    # Get today's events
    today_birthdays = date_service.get_today_birthdays()
    today_anniversaries = date_service.get_today_anniversaries()
    
    if not today_birthdays and not today_anniversaries:
        click.echo("No events to process today.")
        return
    
    # Process birthdays
    for staff in today_birthdays:
        click.echo(f"Processing birthday for {staff.name}...")
        
        # Generate greeting content
        if greeting_agent:
            greeting_content = greeting_agent.generate_birthday_greeting(staff)
        else:
            greeting_content = date_service.format_birthday_message(staff)
        
        # Generate image
        image_url = image_service.generate_birthday_image(staff)
        
        # Send email (will just log in dry run mode)
        if email_service.send_birthday_email(staff, greeting_content, image_url):
            click.echo(f"Birthday email {'would be' if dry_run else 'was'} sent to {staff.name}")
        else:
            click.echo(f"Failed to send birthday email to {staff.name}")
    
    # Process anniversaries
    for staff, years in today_anniversaries:
        click.echo(f"Processing {years}-year anniversary for {staff.name}...")
        
        # Generate greeting content
        if greeting_agent:
            greeting_content = greeting_agent.generate_anniversary_greeting(staff, years)
        else:
            greeting_content = date_service.format_anniversary_message(staff, years)
        
        # Generate image
        image_url = image_service.generate_anniversary_image(staff, years)
        
        # Send email (will just log in dry run mode)
        if email_service.send_anniversary_email(staff, years, greeting_content, image_url):
            click.echo(f"Anniversary email {'would be' if dry_run else 'was'} sent to {staff.name}")
        else:
            click.echo(f"Failed to send anniversary email to {staff.name}")


@cli.group('test')
def test_group():
    """Test application functionality."""
    pass


@test_group.command('setup')
@click.pass_context
def setup_test_data(ctx):
    """Set up test data in the database."""
    create_test_data()
    click.echo("Test data created successfully.")


@test_group.command('greeting')
@click.argument('staff_id', type=int)
@click.option('--type', 'event_type', type=click.Choice(['birthday', 'anniversary']), required=True,
              help='Type of greeting to generate')
@click.option('--years', type=int, help='Years of service (for anniversaries only)')
@click.pass_context
def test_greeting(ctx, staff_id, event_type, years):
    """Test greeting generation for a staff member."""
    config = ctx.obj['config']
    staff = get_staff_by_id(staff_id)
    
    if not staff:
        click.echo(f"Staff member with ID {staff_id} not found.")
        return
    
    try:
        greeting_agent = create_greeting_agent(config)
        
        if event_type == 'birthday':
            greeting = greeting_agent.generate_birthday_greeting(staff)
            click.echo(f"\nBirthday Greeting for {staff.name}:")
        else:  # anniversary
            if not years:
                from office_cheer.utils.date_utils import years_between
                years = years_between(staff.start_date)
                click.echo(f"Using calculated years of service: {years}")
            
            greeting = greeting_agent.generate_anniversary_greeting(staff, years)
            click.echo(f"\n{years}-Year Anniversary Greeting for {staff.name}:")
        
        click.echo("-" * 60)
        click.echo(greeting)
    except Exception as e:
        click.echo(f"Error generating greeting: {e}")


@test_group.command('email')
@click.argument('staff_id', type=int)
@click.option('--type', 'event_type', type=click.Choice(['birthday', 'anniversary']), required=True,
              help='Type of email to test')
@click.option('--years', type=int, help='Years of service (for anniversaries only)')
@click.pass_context
def test_email(ctx, staff_id, event_type, years):
    """Test email generation for a staff member."""
    config = ctx.obj['config']
    config.debug = True  # Force debug mode for testing
    
    staff = get_staff_by_id(staff_id)
    if not staff:
        click.echo(f"Staff member with ID {staff_id} not found.")
        return
    
    # Services
    email_service = EmailService(config)
    date_service = DateMonitoringService(config)
    
    # Generate greeting content
    if event_type == 'birthday':
        greeting_content = date_service.format_birthday_message(staff)
        click.echo("\nTesting birthday email:")
        email_service.send_birthday_email(staff, greeting_content, "placeholder_birthday.png")
    else:  # anniversary
        if not years:
            from office_cheer.utils.date_utils import years_between
            years = years_between(staff.start_date)
            click.echo(f"Using calculated years of service: {years}")
        
        greeting_content = date_service.format_anniversary_message(staff, years)
        click.echo(f"\nTesting {years}-year anniversary email:")
        email_service.send_anniversary_email(staff, years, greeting_content, "placeholder_anniversary.png")


@test_group.command('image')
@click.argument('staff_id', type=int)
@click.option('--type', 'event_type', type=click.Choice(['birthday', 'anniversary']), required=True,
              help='Type of image to test')
@click.option('--years', type=int, help='Years of service (for anniversaries only)')
@click.pass_context
def test_image(ctx, staff_id, event_type, years):
    """Test image generation for a staff member."""
    config = ctx.obj['config']
    config.debug = True  # Force debug mode for testing
    
    staff = get_staff_by_id(staff_id)
    if not staff:
        click.echo(f"Staff member with ID {staff_id} not found.")
        return
    
    image_service = ImageService(config)
    
    if event_type == 'birthday':
        image_path = image_service.generate_birthday_image(staff)
        click.echo(f"Birthday image would be generated at: {image_path}")
    else:  # anniversary
        if not years:
            from office_cheer.utils.date_utils import years_between
            years = years_between(staff.start_date)
            click.echo(f"Using calculated years of service: {years}")
        
        image_path = image_service.generate_anniversary_image(staff, years)
        click.echo(f"{years}-year anniversary image would be generated at: {image_path}")


@cli.command('run')
@click.pass_context
def run_service(ctx):
    """Run the application as a service."""
    from office_cheer.main import OfficeCheers
    
    click.echo("Starting Office Cheer service...")
    app = OfficeCheers()
    
    try:
        click.echo("Running initial check...")
        app.check_events()
        click.echo("Initial check completed")
        
        click.echo(f"Service will check daily at {app.config.daily_check_time}")
        click.echo("Press CTRL+C to exit")
        
        app.run()  # This enters the main loop
    except KeyboardInterrupt:
        click.echo("\nService stopped")
    except Exception as e:
        click.echo(f"Error running service: {e}")


if __name__ == '__main__':
    cli(obj={})