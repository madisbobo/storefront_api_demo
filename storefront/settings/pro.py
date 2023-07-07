from .common import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['bobbuy-prod-bff4f84a128d.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config() # This module looks for an env variable called DATABASE_URL
}

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'from@madis.com'