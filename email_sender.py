import smtplib
import json
import os
import time
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Set


class EmailSender:
    def __init__(self, config_file: str = "config.json"):
        """Initialize EmailSender with configuration."""
        print("Initializing EmailSender...")
        
        self.processed_emails: Set[str] = set()
        self.stats = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'invalid': 0,
            'duplicates': 0
        }
        
        self.config = self.load_config(config_file)
        
        self.setup_logging()
        
        print("EmailSender initialized successfully!")
    
    def setup_logging(self):
        """Setup logging to file."""
        try:
            
            self.log_file = open('mail_log.txt', 'a', encoding='utf-8')
            print("Logging setup complete.")
        except Exception as e:
            print(f"Warning: Could not setup logging: {e}")
            self.log_file = None
    
    def log_message(self, message: str):
        """Log a message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {message}"
        
        
        print(log_entry)
        
        
        if self.log_file:
            try:
                self.log_file.write(log_entry + "\n")
                self.log_file.flush()  
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")
    
    def log_email_status(self, email: str, status: str, error_msg: str = ""):
        """Log email processing status."""
        if error_msg:
            message = f"{email} | {status} | {error_msg}"
        else:
            message = f"{email} | {status}"
        self.log_message(message)
    
    def load_config(self, config_file: str) -> Dict:
        """Load SMTP configuration from JSON file or environment variables."""
        try:
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"Configuration loaded from {config_file}")
                return config
            else:
                
                config = {
                    "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
                    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                    "username": os.getenv("SMTP_USERNAME", "dummy@gmail.com"),
                    "password": os.getenv("SMTP_PASSWORD", "dummy_password"),
                    "sender_name": os.getenv("SENDER_NAME", "Automated Mailer"),
                    "subject": os.getenv("EMAIL_SUBJECT", "Your Subject Here"),
                    "body": os.getenv("EMAIL_BODY", "Hello, this is an automated message."),
                    "delay_seconds": int(os.getenv("EMAIL_DELAY", "90"))
                }
                print("✅ Configuration loaded from environment variables")
                return config
        except Exception as e:
            print(f"Failed to load configuration: {str(e)}")
            raise
    
    def is_valid_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    def read_emails_from_csv(self, csv_file: str) -> List[str]:
        """Read and validate emails from CSV file - Simple line-by-line approach."""
        emails = []
        
        try:
            # Simple line-by-line reading - NO CSV MODULE USED
            with open(csv_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            self.log_message(f"INFO | Reading {len(lines)} lines from {csv_file}")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Skip obvious header lines
                if line.lower() in ['email', 'emails', 'mail', 'e-mail']:
                    self.log_message(f"INFO | Skipping header line: {line}")
                    continue
                
                # Extract email from line (handle various separators)
                possible_email = line
                
                # If line contains comma, semicolon, or tab, take first part
                for separator in [',', ';', '\t', '|']:
                    if separator in line:
                        possible_email = line.split(separator)[0].strip()
                        break
                
                # Remove any quotes
                possible_email = possible_email.strip('"\'')
                
                self.log_message(f"INFO | Processing line {line_num}: {possible_email}")
                
                # Validate email
                if not self.is_valid_email(possible_email):
                    self.log_email_status(possible_email, "INVALID EMAIL")
                    self.stats['invalid'] += 1
                    continue
                
                # Check for duplicates
                if possible_email in self.processed_emails:
                    self.log_email_status(possible_email, "DUPLICATE")
                    self.stats['duplicates'] += 1
                    continue
                
                # Add valid email
                emails.append(possible_email)
                self.processed_emails.add(possible_email)
                self.log_message(f"INFO | Added valid email: {possible_email}")
        
        except FileNotFoundError:
            self.log_message(f"ERROR | CSV file '{csv_file}' not found")
            return []
        except Exception as e:
            self.log_message(f"ERROR | Error reading file: {str(e)}")
            return []
        
        self.log_message(f"INFO | Successfully loaded {len(emails)} valid unique emails")
        return emails
    
    def create_email_message(self, recipient: str) -> MIMEMultipart:
        """Create email message."""
        msg = MIMEMultipart()
        msg['From'] = f"{self.config['sender_name']} <{self.config['username']}>"
        msg['To'] = recipient
        msg['Subject'] = self.config['subject']
        
        # Add body
        body = self.config['body']
        msg.attach(MIMEText(body, 'plain'))
        
        return msg
    
    def send_single_email(self, recipient: str) -> bool:
        """Send email to a single recipient."""
        try:
            # Create message
            msg = self.create_email_message(recipient)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.config['smtp_host'], self.config['smtp_port'])
            server.starttls()  # Enable encryption
            
            try:
                server.login(self.config['username'], self.config['password'])
                
                # Send email
                text = msg.as_string()
                server.sendmail(self.config['username'], recipient, text)
                server.quit()
                
                self.log_email_status(recipient, "SENT")
                self.stats['sent'] += 1
                return True
                
            except smtplib.SMTPAuthenticationError:
                self.log_email_status(recipient, "FAILED", "Authentication Failed - Check credentials")
                self.stats['failed'] += 1
                return False
            except smtplib.SMTPConnectError:
                self.log_email_status(recipient, "FAILED", "Connection Error")
                self.stats['failed'] += 1
                return False
            except Exception as smtp_error:
                self.log_email_status(recipient, "FAILED", f"SMTP Error: {str(smtp_error)}")
                self.stats['failed'] += 1
                return False
                
        except Exception as e:
            self.log_email_status(recipient, "FAILED", str(e))
            self.stats['failed'] += 1
            return False
    
    def send_emails_from_csv(self, csv_file: str):
        """Main method to send emails from CSV file."""
        self.log_message("INFO | === Email Sending Process Started ===")
        self.log_message(f"INFO | Using SMTP Host: {self.config['smtp_host']}:{self.config['smtp_port']}")
        self.log_message(f"INFO | Sender: {self.config['username']}")
        self.log_message(f"INFO | Delay between emails: {self.config['delay_seconds']} seconds")
        
        try:
            # Read emails from CSV
            emails = self.read_emails_from_csv(csv_file)
            self.stats['total'] = len(emails)
            
            if not emails:
                self.log_message("INFO | No valid emails found to process")
                return
            
            # Process each email
            for i, email in enumerate(emails, 1):
                self.log_message(f"INFO | Processing email {i}/{len(emails)}: {email}")
                
                # Send email
                success = self.send_single_email(email)
                
                # Add delay between emails (except for the last one)
                if i < len(emails):
                    self.log_message(f"INFO | Waiting {self.config['delay_seconds']} seconds before next email...")
                    time.sleep(self.config['delay_seconds'])
            
        except Exception as e:
            self.log_message(f"ERROR | Critical error during email processing: {str(e)}")
        
        finally:
            self.print_summary()
            if hasattr(self, 'log_file') and self.log_file:
                self.log_file.close()
    
    def print_summary(self):
        """Print and log final summary."""
        self.log_message("INFO | === Email Sending Process Completed ===")
        self.log_message("INFO | SUMMARY:")
        self.log_message(f"INFO | Total emails processed: {self.stats['total']}")
        self.log_message(f"INFO | Successfully sent: {self.stats['sent']}")
        self.log_message(f"INFO | Failed sends: {self.stats['failed']}")
        self.log_message(f"INFO | Invalid emails: {self.stats['invalid']}")
        self.log_message(f"INFO | Duplicate emails: {self.stats['duplicates']}")
        
        # Print to console as well
        print("\n" + "-"*50)
        print("EMAIL SENDING SUMMARY")
        print("-"*50)
        print(f"Total emails processed: {self.stats['total']}")
        print(f"Successfully sent: {self.stats['sent']}")
        print(f"Failed sends: {self.stats['failed']}")
        print(f"Invalid emails: {self.stats['invalid']}")
        print(f"Duplicate emails: {self.stats['duplicates']}")
        print(f"Log file: mail_log.txt")
        print("-"*50)


# Test the class if run directly
if __name__ == "__main__":
    try:
        sender = EmailSender()
        sender.send_emails_from_csv("emails.csv")
    except Exception as e:
        print(f"Error: {e}")