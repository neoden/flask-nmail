from setuptools import setup

setup(
    name="Flask-NMail",
    version="0.0.1",
    url="https://github.com/neoden/flask-nmail",
    author="Lenar Imamutdinov",
    author_email="lenar.imamutdinov@gmail.com",
    py_modules=['flask_nmail'],
    zip_safe=True,
    include_package_data=True,
    license="MIT",
    description="Flask mail sending with benefits",
    long_description=open("README.md").read()
)
