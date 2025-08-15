#!/usr/bin/env python3
"""
Email Sender Application
========================

This application reads email addresses from a CSV file and sends emails to each address
with real-time logging and error handling.
"""

import sys
import os

# Import the EmailSender class
try:
    from email_sender import EmailSender
    print("EmailSender imported successfully")
except ImportError as e:
    print(f" Import Error: {e}")
    print("Make sure email_sender.py is in the same directory")
    sys.exit(1)


def main():
    """Main application entry point."""
    print("Email Sender Application")
    print("-" * 40)
    
    # Parse command line arguments
    csv_file = "emails.csv"
    config_file = "config.json"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        config_file = sys.argv[2]
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        print(f"Please create a CSV file with email addresses or specify correct path.")
        sys.exit(1)
    
    try:
        # Initialize EmailSender
        sender = EmailSender(config_file)
        
        # Confirm before sending
        print(f"\nConfiguration:")
        print(f"- CSV file: {csv_file}")
        print(f"- Config file: {config_file}")
        print(f"- SMTP Host: {sender.config['smtp_host']}:{sender.config['smtp_port']}")
        print(f"- Sender: {sender.config['username']}")
        print(f"- Subject: {sender.config['subject']}")
        print(f"- Delay: {sender.config['delay_seconds']} seconds between emails")
        print(f"- Log file: mail_log.txt")
        
        response = input("\nDo you want to proceed? (y/n): ").lower().strip()
        
        if response == 'y' or response == 'yes':
            # Start email sending process
            sender.send_emails_from_csv(csv_file)
        else:
            print("Operation cancelled by user.")
    
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user (Ctrl+C)")
        print("Check mail_log.txt for partial results.")
    
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        print("Check mail_log.txt for detailed error information.")
        sys.exit(1)


if __name__ == "__main__":
    main()