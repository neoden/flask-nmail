import os
import re
import uuid
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.charset import Charset
from email.header import Header
from email.utils import formataddr, parseaddr
from email.encoders import encode_quopri

from flask import current_app


class Mail:
    def __init__(self, app=None, **kwargs):
        self.app = app
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, enabled=None, server=None, port=None, sink=None, default_sender=None):
        self.enabled = enabled or app.config.get('MAIL_ENABLED') or True
        self.server = server or app.config.get('MAIL_SERVER') or '127.0.0.1'
        self.port = port or app.config.get('MAIL_PORT') or 25
        # address to send everything to (for testing)
        self.sink = sink or app.config.get('MAIL_SINK')
        self.default_sender = default_sender or app.config.get('MAIL_DEFAULT_SENDER') or 'noreply@example.com'

    @property
    def _app(self):
        if hasattr(self, 'app'):
            return self.app
        else:
            return current_app

    def _extract_statics(self, html):
        """
        Scan HTML for images from /static. When found src is replaced with reference 
        to email attachment.
        Returns augmented HTML and dict with images extracted:
        {
            'image0': <path>,
            'image1': <path>,
            ...
        }
        """
        images = {}
        srcs_found = set()

        re_static_img = re.compile("(?P<img><img\s+[^>]*?src\s*=\s*['\"](?P<src>/static/[^'\"]*?)['\"][^>]*?>)")

        for m in re_static_img.finditer(html):
            src = m.groupdict()['src']
            if src not in srcs_found:
                srcs_found.add(src)
                cid = 'image_{}'.format(uuid.uuid4().hex)
                images[cid] = {
                    'original_path': src,
                    'absolute_path': os.path.join(self._app.root_path, src[1:]),
                }

        for cid, v in images.items():
            html = html.replace(v['original_path'], 'cid:{}'.format(cid))

        return html, {k: v['absolute_path'] for k, v in images.items()}

    @staticmethod
    def _attach_images(msgRoot, images):
        """
        Attach images to email

        msgRoot - MIMEMultipart to put images to
        images - dict as returned from extract_statics: 
            {
                '<name>': <path>,
                ....
            }
        """
        for name, path in images.items():
            with open(path, 'rb') as f:
                msgImage = MIMEImage(f.read())
                msgImage.add_header('Content-ID', '<{}>'.format(name))
                msgImage.add_header('Content-Disposition', 'attachment; filename={}{}'.format(
                                        str(name), get_extension(path)))
                msgRoot.attach(msgImage)

    @staticmethod
    def _contact(address):
        if isinstance(address, tuple):
            return formataddr((Charset('utf-8').header_encode(address[0]), address[1]))
        else:
            return address

    @staticmethod
    def _contact_list(address_list):
        return ', '.join((Mail._contact(address) for address in address_list))

    @staticmethod
    def _address(contact):
        return contact[1] if isinstance(contact, tuple) else contact

    def build_email(self, html_body, text_body, subject, recipients, sender):
        charset = Charset(input_charset='utf-8')

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = charset.header_encode(subject)
        msgRoot['From'] = self._contact(sender)
        msgRoot['To'] = self._contact_list(recipients)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        msgRoot.set_charset('utf-8')

        msgAlternative = MIMEMultipart(_subtype='alternative')
        msgAlternative.set_charset("utf-8")
        msgRoot.attach(msgAlternative)

        msgText = MIMEText(_text=text_body, _subtype='plain', _charset='utf-8')
        msgAlternative.attach(msgText)

        html, images = self._extract_statics(html_body)
        self._attach_images(msgRoot, images)

        msgHtml = MIMEText(_text=html, _subtype='html', _charset='utf-8')
        msgAlternative.attach(msgHtml)

        return msgRoot

    def transfer(self, msgRoot, recipients, sender):
        with smtplib.SMTP(host=self.server, port=self.port) as smtp:
            if self.sink:
                recipients = [self.sink]
            try:
                smtp.sendmail(
                    self._address(sender),
                    [self._address(r) for r in recipients],
                    msgRoot.as_string()
                )
                if self._app.config.get('DEBUG'):
                    self._app.logger.debug('Email sent to: {}'.format(repr([self._address(r) for r in recipients])))
            except smtplib.SMTPRecipientsRefused:
                self._app.logger.error('Email sending failed for: {}'.format(repr(recipients)))


    def send_email(self, html_body, text_body, subject, recipients, sender=None, individual_emails=False):
        """
        Send an email. Static images in html body are converted to attachments.

        recipients - list of email addresses or list of tuples (name, address)
        sender - address or tuple (name, address)
        individual_emails - send each recipient a separate copy

        """
        if not self.enabled:
            return

        sender = sender or self.default_sender
        if not sender:
            raise ValueError('Neither sender nor default sender is set')            

        msgRoot = self.build_email(html_body, text_body, subject, recipients, sender)
        if individual_emails:
            for recipient in recipients:
                self.transfer(msgRoot, [recipient], sender)
        else:
            self.transfer(msgRoot, recipients, sender)


def test():
    import sys
    from flask import Flask

    app = Flask(__name__)
    mail = Mail(app, sink=sys.argv[1])

    mail.send_email(
        html_body="""
        <h1>Test email from Flask-NMail</h1>
        """,
        text_body='Test email from Flask-NMail',
        subject='test email',
        recipients=['test@example.com']
    )


if __name__ == '__main__':
    test()
