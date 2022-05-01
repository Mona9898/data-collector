from email.mime.text import MIMEText
import smtplib

def send_email(email,age,avg_age,count):
    from_email="yym9898@gmail.com"
    from_password="7749879Kkk"
    to_email=email

    subject="Age data"
    message="Hey there, your age is <strong>%s</strong>. Average age of total <strong>%s</strong> participants is <strong>%s</strong>." % (age,count,avg_age) 

    msg=MIMEText(message, 'html')
    msg['Subject']=subject
    msg['To']=to_email
    msg['From']=from_email


    gmail=smtplib.SMTP('smtp.gmail.com',587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email,from_password)
    gmail.send_message(msg)
