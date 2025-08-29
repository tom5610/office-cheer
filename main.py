#!/usr/bin/env python3
# ABOUTME: Main entry point for the Office Cheer application
# ABOUTME: Allows launching the CLI or running as a service

import os
import sys

from office_cheer.cli import cli
from office_cheer.main import OfficeCheers


def main():
    """
    Main entry point that dispatches to either CLI mode or service mode.
    
    Use --service flag to run as a service, otherwise runs in CLI mode.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--service":
        # Run as a service
        print("Starting Office Cheer service...")
        try:
            app = OfficeCheers()
            app.run()
        except KeyboardInterrupt:
            print("\nService stopped")
        except Exception as e:
            print(f"Error running service: {e}")
    else:
        # Run CLI
        cli(obj={})


if __name__ == "__main__":
    main()