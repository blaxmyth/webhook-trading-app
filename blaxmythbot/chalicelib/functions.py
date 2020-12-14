import json, datetime, requests, math, smtplib, jinja2, os
from chalicelib import config

def render(template_path, response): #jinja helper function to render templates
    path, filename = os.path.split(template_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(response)

def send_email(response):
    #email properties
    from_email = 'cbonnette215@gmail.com'
    to_email = 'cbonnette215@gmail.com'
    subject = 'Blaxmyth Trade Bot Transaction'
    message = json.dumps(response, indent=4)

    #email send request
    try:
        smtp_server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587) #create smtp server
        smtp_server.starttls() #start session encryption
        smtp_server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD) #connect to server with creds
        msg = 'From: ' + from_email + '\nTo: ' + to_email + '\nSubject: ' + subject + '\n\n' + message #build email header message
        smtp_server.sendmail(from_email, to_email, msg) #send email (from, to, message)

        print ('Email sent!')
    except Exception as e:
        print(e)
        print ('ERROR: Unable to send email')