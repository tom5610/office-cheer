# Office Cheer

An agentic AI application for sending personalized greetings on staff birthdays and work anniversaries.

## Description

Office Cheer is a Python application built with [Strands Agents](https://github.com/strands-agents/sdk-python) that:

1. Monitors staff birthdays and work anniversaries
2. Creates personalized digital greeting cards based on staff interests
3. Sends cards via email to the staff member and their peers

The application uses Claude 4 Sonnet from Amazon Bedrock to create personalized greeting messages and Amazon Nova Foundation Model from Amazon Bedrock Canvas to generate digital greeting cards.

## Features

- Automated monitoring of staff birthdays and work anniversaries
- Personalized greeting messages tailored to each staff member's interests
- Custom-generated digital greeting cards
- Email delivery through Amazon SES
- Command-line interface for managing staff and events
- Support for running as a standalone service

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/office-cheer.git
cd office-cheer

# Install the package and dependencies
pip install -e .

# For development, install with testing dependencies
pip install -e ".[test]"
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# Database settings
OFFICE_CHEER_DB_PATH=sqlite:///office_cheer.db

# AWS settings
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Email settings
EMAIL_SENDER=noreply@example.com
EMAIL_REPLY_TO=support@example.com

# Application settings
DAILY_CHECK_TIME=08:00
LOOKFORWARD_DAYS=3
CHECK_ON_STARTUP=false

# Development settings
DEBUG=true
```

## Usage

### CLI Commands

Office Cheer provides a command-line interface for managing staff and events:

```bash
# Show available commands
office-cheer --help

# List all staff members
office-cheer staff list

# Add a new staff member
office-cheer staff add --name "John Doe" --email "john@example.com" --birthday "1990-05-15" --start-date "2020-03-10" --interests "hiking, photography, cooking"

# Show upcoming events
office-cheer events upcoming --days 7

# Process today's events (dry run mode)
office-cheer events process --dry-run

# Process today's events (actual sending)
office-cheer events process --no-dry-run

# Run as a service
office-cheer run
```

### Running as a Service

To run Office Cheer as a service:

```bash
# Using the CLI
office-cheer run

# Or using the main script
python main.py --service
```

## Development

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=office_cheer

# Create test data
office-cheer test setup
```

### Project Structure

- `office_cheer/`: Main package
  - `db/`: Database models and utilities
  - `agents/`: Strands Agent implementation
  - `services/`: Core services (date, email, image)
  - `utils/`: Utility functions
  - `main.py`: Application main class
  - `cli.py`: Command-line interface
  - `config.py`: Configuration management
- `tests/`: Test suite
- `main.py`: Entry point script

## License

MIT License