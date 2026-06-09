# Gmail Bulk Email Sender

A lightweight desktop application for sending bulk emails via Gmail SMTP.

## Features

✅ **Gmail Integration** - Uses Gmail SMTP with App Password  
✅ **Bulk Sending** - Load recipients from CSV or TXT files  
✅ **Personalization** - Use {name} and {email} placeholders  
✅ **Templates** - Save and load email templates  
✅ **Progress Tracking** - Real-time progress bar and logs  
✅ **Rate Limiting** - Configurable delay between emails  
✅ **HTML Support** - Send HTML or plain text emails  
✅ **Error Handling** - Detailed logging of sent/failed emails  

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Method 1: Run Python Script
```bash
python bulk_email_sender.py
```

### Method 2: Use Desktop Shortcut
Double-click **"Gmail Bulk Sender.lnk"** on your desktop

## Gmail Setup

1. **Enable 2-Step Verification** in your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Create an **App Password** for Mail
4. Copy the 16-character password
5. Paste it in the app (NOT your regular password!)

## Recipient File Format

### CSV Format (Recommended)
```csv
email,name
john@example.com,John Doe
jane@example.com,Jane Smith
```

### TXT Format
```
john@example.com
jane@example.com
bob@example.com
```

## Personalization

Use these placeholders in your email body:
- `{name}` - Recipient's name
- `{email}` - Recipient's email address

Example:
```
Dear {name},

Thank you for signing up with {email}!
```

## Logs

All sent emails are logged to `send_logs.txt` with timestamps and status.

## Safety Features

- Confirmation dialog before sending
- Delay between emails to avoid spam filters
- Detailed error reporting
- Ability to stop sending anytime

## Troubleshooting

**"Authentication failed"**
- Make sure you're using an App Password, not your regular Gmail password
- Check if 2-Step Verification is enabled

**"Connection refused"**
- Check your internet connection
- Gmail SMTP might be blocked by firewall

**Emails go to spam**
- Add delay between emails (2-5 seconds recommended)
- Use plain text instead of HTML
- Avoid spam trigger words

## Support

Created with ❤️ for efficient bulk email sending.

---

**Version:** 1.0  
**License:** MIT  
**Platform:** Windows (Python 3.8+)
