import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from studentportal import models


def generate_filename_for_internship(record: models.JobProfile):
    return f"{record.company}_{record.duration_months} months_{record.year}.pdf".replace(" ", "_")


def generate_filename_for_placement(record: models.JobProfile):
    return f"{record.company}_{record.year}.pdf".replace(" ", "_")


def generate_filename_for_hackathon(record: models.HackathonProfile):
    return f"{record.title}_{record.organizer}_{record.get_certificate_type_display()}_{record.year}.pdf".replace(" ", "_")


def generate_filename_for_course(record: models.OnlineCoursesProfile):
    return f"{record.title}_{record.issued_by}_{record.year}.pdf".replace(" ", "_")


def send_forget_password_mail(name, email, password):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Forget Password Request"
    message["From"] = "freshers.algorhythm@gmail.com"
    message["To"] = email

    html = f"""\
    <html>
        <body>
        <p>Hello {name},</p>
        <p>Your credentials to login</p>
        <p>Username / E-mail : {email} </p>
        <p>Password : {password} </p>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part2 = MIMEText(html, "html")

    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("freshers.algorhythm@gmail.com", "ngernvzucedyyhmy")
        server.sendmail("freshers.algorhythm@gmail.com", email, message.as_string())
