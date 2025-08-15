# 📧 Email Sender

A Python script for sending bulk emails from a CSV file with a configurable delay between each send.  
Supports any SMTP server — just update `config.json` or environment variables, and you’re good to go.

---

## 📂 Project Structure
```
email_sender/
├── emails.csv # CSV file containing recipient emails
├── mail_log.txt # Log file for sent/failed/duplicate/invalid emails
├── config.json # SMTP & mail configuration (can also use environment variables)
├── email_sender.py # Core EmailSender class
├── main.py # Main script with user interaction
├── requirements.txt # Dependencies (uses Python standard library)
└── README.md # Documentation
```


---

## 📄 CSV Format
The `emails.csv` file must contain one email per row.  
Example:

```
email
mail1@example.com
mail2@example.com
mail3@example.com
```


---

## 🛠 Sample `config.json`
```json
{
    "smtp_host": "smtp.example.com",
    "smtp_port": 587,
    "username": "your-email@example.com",
    "password": "your-app-password",
    "sender_name": "Your Name",
    "subject": "Your Subject Here",
    "body": "Plain text email body goes here",
    "delay_seconds": 90
}
```

## 📥 Installation

**Clone the Project**
```bash
git clone https://github.com/yourusername/email_sender.git
cd email_sender
```

**(Optional) Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

**Install Requirements**

```bash
pip install -r requirements.txt
```

---

## Running the Script

```bash
python main.py
```
---

## Logging

```
2025-08-15 10:42:11 | mail1@example.com | SENT
2025-08-15 10:42:12 | mail2@example.com | FAILED | Connection Timeout
2025-08-15 10:42:13 | mail3@example.com | INVALID EMAIL
2025-08-15 10:42:14 | mail1@example.com | DUPLICATE

---

```

