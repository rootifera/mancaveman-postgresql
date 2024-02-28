import smtplib
from email.mime.text import MIMEText

from tools.config_manager_redis import get_email_credentials, get_hostname


def send_pw_reset_email(receiver: str, token: str):
    if get_email_credentials() == 'False':
        return {'ERROR': 'Email credentials are not set'}

    user, pw = get_email_credentials()
    hostname = get_hostname()
    from_address = user + '@gmail.com'
    to_address = receiver

    reset_link = 'https://' + hostname + '/forgot-password'

    plain_text = f"""\
    Please use the following link to reset your password:
    {reset_link} \n
    Your reset token: {token}
    """

    msg = MIMEText(plain_text, 'plain')
    msg['Subject'] = "Mancaveman Account Password Reset"
    msg['From'] = from_address
    msg['To'] = to_address

    username = user
    password = pw

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(from_address, to_address, msg.as_string())
