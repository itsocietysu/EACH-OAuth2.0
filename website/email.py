from threading import Thread
from flask import render_template
from flask_babel import lazy_gettext as _l
from flask_mail import Message


def send_async_email(app, msg, mail):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    from app import mail, app

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(app, msg, mail)).start()


def send_password_reset_email(user):
    from app import app

    token = user.get_reset_password_token()
    send_email(_l('[EACH] Reset Your Password'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token),
               sync=True)
