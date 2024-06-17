import smtplib

def restock_email(email_sender, email_password, email_receiver, subject, message):
    """
    Sends an email using the provided credentials and message details.

    Parameters:
    email_sender (str): The sender's email address.
    email_password (str): The sender's email password or app-specific password.
    email_receiver (str): The recipient's email address.
    subject (str): The subject of the email.
    message (str): The body of the email.
    """
    text = f"Subject: {subject}\n\n{message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, text)
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Failed to authenticate: {e}")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"Recipient address rejected: {e}")
    except smtplib.SMTPSenderRefused as e:
        print(f"Sender address rejected: {e}")
    except smtplib.SMTPDataError as e:
        print(f"SMTP data error: {e}")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.quit()

if __name__ == '__main__':
    email_sender = 'prathapj.ei20@bmsce.ac.in'
    email_password = 'njipmbrcobpjwcim' 
    email_receiver = 'kushalm518@gmail.com'
    subject = 'Rectock Alert'
    message = 'restock items'

    restock_email(email_sender, email_password, email_receiver, subject, message)