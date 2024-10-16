FROM python:3.11

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

# Install Python dependencies
#RUN pip install Django djangorestframework psycopg2-binary django-cors-headers Pillow django-oauth-toolkit requests-oauthlib djangorestframework-simplejwt pyotp qrcode
RUN pip install Django djangorestframework psycopg2 django-cors-headers Pillow django-oauth-toolkit requests-oauthlib djangorestframework-simplejwt pyotp qrcode pytz

# Django: High-level Python web framework
# djangorestframework: Toolkit for building Web APIs in Django
# psycopg2-binary: PostgreSQL database adapter for Python
# django-cors-headers: Handles CORS headers for Django responses
# Pillow: Python Imaging Library -> Upload Avatars
# django-oauth-toolkit: Provides OAuth2 implementation for Django
# requests-oauthlib: Library for making OAuth1 and OAuth2 requests
# djangorestframework-simplejwt: JWT authentication backend for Django REST Framework
# pyotp: Python implementation of the One-Time Password (OTP) algorithm -> 2FA
# qrcode: QR code generator in Python -> 2FA
# pytz: es una biblioteca de Python que proporciona funcionalidades para trabajar con zonas horarias.

COPY ./runserver.sh /usr/bin/
RUN chmod +x /usr/bin/runserver.sh

COPY ./wait-for-it.sh /usr/bin/
RUN chmod +x /usr/bin/wait-for-it.sh

EXPOSE 9090

CMD ["/usr/bin/wait-for-it.sh", "tournament_postgres", "5555", "/usr/bin/runserver.sh"]