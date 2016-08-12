Flask-NMail
===========


Installation
------------

    pip install https://github.com/neoden/flask-nmail

Usage
-----

```python
    from flask import Flask
    from flask_ext.nmail import Mail

    app = Flask(__name__)
    mail = Mail(app)
```

Configuration
-------------

Parameter           | Description
--------------------|---------------------------------------------------
MAIL_ENABLED        | Default is True
MAIL_SERVER         | IP or hostname, default is '127.0.0.1'
MAIL_PORT           | Default is 25
MAIL_SINK           | Address to send everything to (useful for testing)
MAIL_DEFAULT_SENDER | Appears in From


API
---

Mail.send_email(self, html_body, text_body, subject, recipients, sender=None, individual_emails=False)

html_body - string with HTML body
text_body - string with plain text body
subject - message subject
recipients - iterator of email addresses or tuples (name, address)
sender - message sender address or tuple (name, address)
individual_emails - if set to True, each recipient will get a separate copy of the message
