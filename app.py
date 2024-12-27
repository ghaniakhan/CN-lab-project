from flask import Flask, render_template, request, redirect, jsonify
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

app = Flask(__name__)

# Load email credentials from config file
with open('config.json') as f:
    config = json.load(f)
EMAIL = config['email']
PASSWORD = config['password']

# Database file
EMAILS_DB = 'emails.json'

# Pre-defined email templates
TEMPLATES = {
    'business': 'Dear Sir/Madam,\n\nI hope this email finds you well.\n\nBest regards,\n[Your Name]',
    'casual': 'Hey there!\n\nHow’s everything going?\nLet’s catch up soon.\nCheers!',
    'promotional': 'Hello!\n\nCheck out our latest products at amazing discounts!\n\nVisit our website now!'
}

# Known spam keywords (can be expanded)
SPAM_KEYWORDS = ['free', 'win', 'prize', 'guaranteed', 'limited offer']

def save_email(to, subject, message):
    email_entry = {
        "to": to,
        "subject": subject,
        "message": message,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(EMAILS_DB):
        with open(EMAILS_DB, 'r') as f:
            emails = json.load(f)
    else:
        emails = []

    emails.append(email_entry)

    with open(EMAILS_DB, 'w') as f:
        json.dump(emails, f, indent=4)

def is_spam(message):
    # Check if the message contains any spam keywords
    return any(keyword in message.lower() for keyword in SPAM_KEYWORDS)

@app.route('/')
def index():
    return render_template('index.html', templates=TEMPLATES)

@app.route('/send-email', methods=['POST'])
def send_email():
    to_email = request.form['to']
    subject = request.form['subject']
    message = request.form['message']
    attachment = request.files.get('attachment')

    # Spam filter check
    if is_spam(message):
        return "This message contains spam-like content and was not sent."

    # Email setup
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Handle attachment
    if attachment:
        filename = attachment.filename
        filepath = os.path.join('uploads', filename)
        attachment.save(filepath)

        with open(filepath, 'rb') as attach_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attach_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)

        os.remove(filepath)

    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        save_email(to_email, subject, message)
        return redirect('/sent-emails?success=true')
    except Exception as e:
        return f"Error sending email: {e}"
    


@app.route('/delete-email', methods=['POST'])
def delete_email():
    email_index = int(request.form['email_index'])
    if os.path.exists(EMAILS_DB):
        with open(EMAILS_DB, 'r') as f:
            emails = json.load(f)
        if 0 <= email_index < len(emails):
            emails.pop(email_index)
            with open(EMAILS_DB, 'w') as f:
                json.dump(emails, f, indent=4)
    return redirect('/sent-emails')



@app.route('/search-emails', methods=['GET', 'POST'])
def search_emails():
    if request.method == 'POST':
        search_query = request.form.get('search')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')

        if os.path.exists(EMAILS_DB):
            with open(EMAILS_DB, 'r') as f:
                emails = json.load(f)
        else:
            emails = []

        # Apply search query filter
        if search_query:
            emails = [email for email in emails if search_query.lower() in email['subject'].lower() or
                      search_query.lower() in email['to'].lower() or
                      search_query.lower() in email['message'].lower()]

        # Apply date range filter
        if from_date and to_date:
            emails = [email for email in emails if from_date <= email['date'] <= to_date]

        return render_template('search_emails.html', emails=emails)

    return render_template('search_emails.html', emails=None)



@app.route('/sent-emails', methods=['GET'])
def sent_emails():
    if os.path.exists(EMAILS_DB):
        with open(EMAILS_DB, 'r') as f:
            emails = json.load(f)
    else:
        emails = []

    return render_template('sent_emails.html', emails=emails)


if __name__ == '__main__':
    app.run(debug=True)