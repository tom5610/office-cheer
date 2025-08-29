# Office Cheer Scripts

This directory contains utility scripts for the Office Cheer application.

## Data Generation

The `generate_data.py` script creates synthetic staff data for testing and demonstration purposes.

### Usage

```bash
# Generate 20 random staff records
python scripts/generate_data.py

# Generate 50 random staff records
python scripts/generate_data.py --count 50

# Generate staff records including some with upcoming birthdays and anniversaries
python scripts/generate_data.py --include-events

# Show help
python scripts/generate_data.py --help
```

### Features

- Generates realistic staff data with random names, emails, and dates
- Creates a mix of staff with different ages and tenure lengths
- With the `--include-events` option, ensures there are upcoming birthdays and anniversaries for testing
- Creates milestone anniversaries (1, 5, 10, etc. years) for better testing

### Example Output

```
Initializing database...
Adding 30 staff records to the database...
Added: John Smith (Birthday: 1980-03-15, Start date: 2015-06-10)
Added: Mary Johnson (Birthday: 1985-07-22, Start date: 2018-02-01)
Added: Robert Brown (Birthday: 1975-11-30, Start date: 2010-09-15)
...

Successfully added 30 out of 30 staff records.

Upcoming events were generated. To see them, run:
office-cheer events upcoming --days 14
```

After running the script, you can use the CLI to check for upcoming events:

```bash
office-cheer events upcoming --days 14
```