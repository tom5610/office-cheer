# Office Cheer - Project Implementation Plan

## Project Overview

Office Cheer is an agentic AI application built with Strands Agents that:
1. Monitors staff birthdays and work anniversaries
2. Creates personalized digital greeting cards based on staff interests
3. Sends cards via email to the staff member and their peers

## Technical Stack

- **Agent Framework**: Strands Agents SDK (Python)
- **LLM for Card Content**: Claude 4 Sonnet (Amazon Bedrock)
- **Image Generation**: Amazon Nova Foundation Model (Amazon Bedrock - Canvas)
- **Email Service**: Amazon SES
- **Database**: SQLite for development, optionally AWS RDS for production
- **Scheduling**: Python schedule library for monitoring dates

## Implementation Plan (Iterative Steps)

### Phase 1: Foundation Setup

#### Step 1.1: Project Structure and Environment Setup
- Initialize project structure
- Set up virtual environment
- Install dependencies (Strands SDK, SQLite, etc.)
- Configure project settings

#### Step 1.2: Database Implementation
- Create SQLite database
- Implement staff table schema 
- Create database utility functions for CRUD operations

#### Step 1.3: Basic Agent Setup
- Initialize Strands Agent
- Configure with Amazon Bedrock for Claude 4 Sonnet
- Create simple agent tools for testing

### Phase 2: Core Functionality

#### Step 2.1: Date Monitoring System
- Implement date utility functions for comparing dates
- Create monitoring service to check for upcoming birthdays/anniversaries
- Add scheduling functionality to run checks daily

#### Step 2.2: Greeting Card Content Generation
- Create prompt engineering for Claude 4 Sonnet
- Develop tools for the agent to generate personalized message content
- Implement content validation and refinement

#### Step 2.3: Digital Card Image Generation
- Set up Amazon Bedrock Canvas integration
- Create image generation prompts based on interests and occasion
- Implement image handling and storage

#### Step 2.4: Email Service Integration
- Set up Amazon SES configuration
- Create email templates
- Implement email sending functionality

### Phase 3: Integration and Enhancement

#### Step 3.1: Full System Integration
- Connect all components into a complete workflow
- Implement error handling and logging
- Add configuration management

#### Step 3.2: Testing and Validation
- Create test data set with mock staff profiles
- Test full workflow with various scenarios
- Implement monitoring and debugging tools

#### Step 3.3: Deployment and Operations
- Prepare deployment configuration
- Set up scheduling for production environment
- Create admin dashboard (optional)

## Detailed Implementation Steps (For Prompt Generation)

### 1. Project Setup Prompts

#### Prompt 1.1: Project Structure and Environment
```
Create the basic project structure for the Office Cheer application. Set up a virtual environment and install necessary dependencies including Strands Agents SDK. Create the following file structure:

- office_cheer/
  - __init__.py
  - config.py (for application configuration)
  - db/
    - __init__.py
    - models.py
    - db_utils.py
  - agents/
    - __init__.py
    - greeting_agent.py
  - services/
    - __init__.py
    - date_service.py
    - email_service.py
    - image_service.py
  - utils/
    - __init__.py
    - date_utils.py
  - main.py (application entry point)

Include a requirements.txt file with all necessary dependencies.
```

#### Prompt 1.2: Configuration Management
```
Create a configuration management system for the Office Cheer application. The configuration should include:

1. Database settings (path for SQLite)
2. AWS credentials and region for Bedrock and SES
3. Email settings (sender, templates)
4. Application settings (schedule timing, lookforward days)

Implement this in the config.py file using environment variables with reasonable defaults for development. Add documentation on how to configure the application.
```

### 2. Database Implementation Prompts

#### Prompt 2.1: Database Schema and Models
```
Create the database models for the Office Cheer application using SQLite. Implement the Staff model according to the specified schema:

- name (string): Full name of the employee
- alias (string): Nickname or preferred name
- email_address (string): Email address for communication
- birthday (date): Date of birth for birthday monitoring
- start_date (date): Employment start date for work anniversaries
- interests (string): Comma-separated list of interests for personalization

Include methods to:
1. Create database tables on application startup
2. Validate data types
3. Convert between database types and Python objects

Implement this in the db/models.py file.
```

#### Prompt 2.2: Database Utilities
```
Create utility functions for database operations in the db/db_utils.py file. Implement functions to:

1. Connect to the SQLite database
2. Add new staff members
3. Update existing staff records
4. Retrieve staff by various criteria (id, email, name)
5. Get staff with upcoming birthdays or anniversaries within a specified timeframe
6. Delete staff records

Ensure proper error handling, connection management, and type safety.
```

### 3. Agent Implementation Prompts

#### Prompt 3.1: Basic Agent Setup
```
Set up a basic Strands Agent for the Office Cheer application in agents/greeting_agent.py. Configure the agent to use Claude 4 Sonnet through Amazon Bedrock.

Include:
1. Agent initialization with appropriate model settings
2. Basic tools for the agent to interact with the application
3. Example prompts for generating greeting messages

Create a factory function that returns a properly configured agent instance.
```

#### Prompt 3.2: Agent Tools Implementation
```
Create tools for the Strands Agent to use in the Office Cheer application. Implement the following tools:

1. get_staff_info(staff_id): Retrieves information about a staff member
2. get_upcoming_events(days_ahead=7): Gets birthdays and anniversaries in the next X days
3. generate_greeting_content(staff_name, event_type, interests): Generates personalized greeting text
4. format_email_body(greeting_content, image_url): Formats content for email delivery

Use the @tool decorator from Strands SDK to make these functions available to the agent.
```

### 4. Core Services Prompts

#### Prompt 4.1: Date Monitoring Service
```
Implement a date monitoring service in services/date_service.py to check for upcoming birthdays and work anniversaries.

Include functions to:
1. Check for upcoming birthdays within a specified timeframe
2. Check for upcoming work anniversaries within a specified timeframe
3. Calculate milestone anniversaries (1 year, 5 years, 10 years, etc.)
4. Schedule daily checks and trigger appropriate actions

Use the utils/date_utils.py module for date comparison and calculation operations.
```

#### Prompt 4.2: Date Utilities
```
Create date utility functions in utils/date_utils.py to support the date monitoring service.

Implement functions to:
1. Compare dates ignoring the year component (for birthday checking)
2. Calculate days between dates
3. Calculate years between dates (for anniversary milestones)
4. Format dates for display in greeting cards and emails
5. Determine if a date falls within a specified window from today
```

#### Prompt 4.3: Image Generation Service
```
Create an image generation service in services/image_service.py to generate digital greeting cards using Amazon Bedrock Canvas.

Implement functions to:
1. Create image generation prompts based on staff interests and occasion
2. Call Amazon Bedrock Canvas API to generate images
3. Store generated images temporarily or permanently
4. Retrieve image URLs for email inclusion

Ensure proper error handling and fallback mechanisms if image generation fails.
```

#### Prompt 4.4: Email Service
```
Implement an email service in services/email_service.py using Amazon SES to send greeting cards.

Include functions to:
1. Configure Amazon SES client
2. Create email templates for birthdays and work anniversaries
3. Personalize email content with staff information and generated content
4. Send emails to the celebrating staff member
5. Send notification emails to peers (optional)
6. Handle email delivery failures and retries
```

### 5. Integration Prompts

#### Prompt 5.1: Main Application Flow
```
Create the main application workflow in main.py that ties all components together.

Implement:
1. Application initialization (database, agent, services)
2. Scheduled job for daily checking of events
3. Workflow for processing each event type:
   - Detecting upcoming birthdays and anniversaries
   - Generating appropriate content with the agent
   - Creating digital cards
   - Sending emails
4. Logging and error handling for the entire process

Make the application runnable as a standalone service.
```

#### Prompt 5.2: Testing and Validation
```
Create a testing module to validate the Office Cheer application functionality.

Implement:
1. Test data generation with mock staff profiles
2. Functions to simulate specific dates for testing birthday/anniversary detection
3. Validation functions to verify generated content and images
4. End-to-end test workflow without sending actual emails

Make the tests easily runnable from the command line.
```

#### Prompt 5.3: CLI Interface
```
Create a command-line interface for the Office Cheer application to allow for:

1. Adding/updating/removing staff members
2. Manually triggering checks for upcoming events
3. Testing greeting generation without sending emails
4. Viewing application status and recent activity

Use argparse or click to implement a clean, user-friendly CLI.
```

### 6. Enhancement Prompts

#### Prompt 6.1: Error Handling and Logging
```
Enhance the Office Cheer application with comprehensive error handling and logging.

Implement:
1. Centralized error handling for all services
2. Detailed logging with different levels (debug, info, warning, error)
3. Error recovery strategies for common failure scenarios
4. Notification system for critical errors

Use Python's logging module and create a consistent error handling pattern across the application.
```

#### Prompt 6.2: Configuration Management Enhancement
```
Enhance the configuration system to support different environments (development, testing, production).

Implement:
1. Environment-specific configuration files
2. Command-line overrides for configuration values
3. Configuration validation to ensure all required values are present
4. Dynamic reconfiguration without application restart (if applicable)

Update the config.py module to support these enhanced capabilities.
```

## Final Integration Steps

These final steps ensure that all components work together seamlessly:

1. Create an initialization script that sets up the database, configures services, and prepares the application for first use
2. Implement a health check mechanism to verify all components are functioning properly
3. Create a documentation file explaining how to use, configure, and extend the application
4. Develop deployment scripts or instructions for running in various environments