Flask-NMail
===========


Installation
------------

    pip install git+https://github.com/neoden/flask-nmail

Usage
-----

```python
    from flask import Flask
    from flask_nmail import Mail

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

Mail.**send_email**(_self_, _html_body_, _text_body_, _subject_, _recipients_, _sender_=None, _individual_emails_=False)

- **html_body** - string with HTML body
- **text_body** - string with plain text body
- **subject** - message subject
- **recipients** - iterator of email addresses or tuples (name, address)
- **sender** - message sender address or tuple (name, address)
- **individual_emails** - if set to True, each recipient will get a separate copy of the message
