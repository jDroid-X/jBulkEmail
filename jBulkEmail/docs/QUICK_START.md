# 🚀 Gmail Bulk Email Sender - Quick Start Guide

## ✅ Application Created Successfully!

Your Gmail Bulk Email Sender is ready to use!

---

## 📂 Project Location
```
C:\Users\dell\jAnitGravity\BulkEmailSender\
```

## 🎯 How to Run

### Option 1: Desktop Shortcut (Recommended)
- Double-click **"Gmail Bulk Sender"** shortcut on your Desktop

### Option 2: Run Script
- Navigate to project folder
- Double-click **run.bat**

### Option 3: Command Line
```bash
cd C:\Users\dell\jAnitGravity\BulkEmailSender
python bulk_email_sender.py
```

---

## 📧 First Time Setup

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Select **Mail** and generate password
5. **Copy the 16-character password** (spaces don't matter)

### Step 2: Configure App

1. Launch the application
2. Enter your **Gmail address** (e.g., yourname@gmail.com)
3. Paste the **App Password** (NOT your regular password!)
4. Click **💾 Save Settings**

---

## 📝 How to Use

### 1. Prepare Recipients

Create a CSV file with this format:
```csv
email,name
john@example.com,John Doe
jane@example.com,Jane Smith
bob@example.com,Bob Johnson
```

**OR** use a text file with one email per line:
```
john@example.com
jane@example.com
bob@example.com
```

**Sample file provided:** `sample_recipients.csv`

### 2. Compose Email

1.  **Subject**: Enter your email subject
2. **Recipients**: Click **"📎 Attach CSV/TXT"** and select your file
3. **Email Body**: Type or paste your message
4. **Personalization** (Optional): Use `{name}` and `{email}` in body

Example:
```
Dear {name},

Thank you for subscribing with {email}!

Best regards,
Your Team
```

### 3. Configure Options

- **Delay between emails**: 2-5 seconds recommended (avoid spam filters)
- **Enable personalization**: Check to use {name} and {email} placeholders
- **Send as HTML**: Check if your email contains HTML formatting

### 4. Send Emails

1. Click **🔍 Preview** to see how the first email will look
2. Click **📤 Send Emails**
3. Confirm the action
4. Watch the progress bar and logs
5. Click **⏹ Stop** if you need to stop early

---

## 💡 Features

✅ **Gmail Integration** - Secure SMTP with App Password
✅ **Bulk Sending** - Send to unlimited recipients
✅ **Personalization** - Dynamic content per recipient
✅ **Templates** - Save and load email templates
✅ **Progress Tracking** - Real-time status and logs
✅ **Rate Limiting** - Avoid spam filters
✅ **Error Handling** - Detailed logging
✅ **Preview** - Test before sending

---

## 📋 File Structure

```
BulkEmailSender/
├── bulk_email_sender.py    # Main application
├── run.bat                  # Windows launcher
├── config.json              # Saved settings (auto-created)
├── send_logs.txt            # Email logs (auto-created)
├── templates/               # Saved templates (auto-created)
├── sample_recipients.csv    # Sample recipient file
├── requirements.txt         # Python dependencies
└── README.md               # Documentation
```

---

## ⚠️ Important Notes

### Security
- **NEVER share your App Password!**
- Config file stores password locally (keep it safe)
- Logs contain email addresses (be mindful of privacy)

### Gmail Limits
- **500 emails/day** for free Gmail accounts
- **2,000 emails/day** for Google Workspace accounts
- **Delay recommended**: 2-5 seconds between emails

### Best Practices
1. Always use **App Password**, not regular password
2. Test with a small list first
3. Use delays to avoid spam filters
4. Preview before sending
5. Keep recipient lists updated

---

##  🔧 Troubleshooting

### "Authentication failed"
- Use App Password, not regular Gmail password
- Check if 2-Step Verification is enabled
- Regenerate App Password if needed

### "Connection refused"
- Check internet connection
- Gmail SMTP might be blocked by firewall/antivirus
- Try disabling VPN temporarily

### Emails go to spam
- Increase delay between emails (3-5 seconds)
- Use plain text instead of HTML
- Avoid spam trigger words (FREE, CLICK HERE, etc.)
- Warm up: Start with small batches

### Python not found
- Install Python 3.8+ from https://www.python.org/downloads/
- Make sure "Add Python to PATH" was checked during installation

---

## 📊 Logs and Tracking

All sent emails are logged to **send_logs.txt** with:
- Timestamp
- Recipient email
- Success/Failure status
- Error messages (if any)

Click **📋 View Logs** button to open the log file.

---

## 🎨 Templates

Save frequently used emails as templates:

1. Compose your email
2. Click **💾 Save Template**
3. Enter template name
4. Load anytime with **📂 Load Template**

Templates are saved in `templates/` folder as JSON files.

---

## ✨ Tips for Success

1. **Test First**: Send to yourself first to check formatting
2. **Personalize**: Use recipient names for better engagement
3. **Clear Subject**: Write descriptive subject lines
4. **Plain Text**: Consider plain text for better deliverability
5. **Timing**: Send during business hours for better open rates
6. **Follow Up**: Use templates for follow-up campaigns

---

## 🆘 Support

For issues or questions:
1. Check the README.md file
2. Review troubleshooting section above
3. Check Gmail SMTP documentation
4. Verify App Password is correct

---

**Version**: 1.0
**Created**: 2026-02-11
**Platform**: Windows (Python 3.8+)
**License**: MIT

---

## 🎉 You're All Set!

Your Gmail Bulk Email Sender is fully configured and ready to use!

**Next Steps:**
1. Set up your Gmail App Password
2. Prepare your recipient list (CSV/TXT)
3. Launch the app from Desktop shortcut
4. Start sending!

Happy Emailing! 📧✨
