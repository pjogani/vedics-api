from configurations import Configuration
from .common import Common

class Local(Common):
    DEBUG = True
    SECRET_KEY = 'your-secret-key-here'
    ALLOWED_HOSTS = ["*"]

    # Add any local-specific settings here
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'postgres',
            'PORT': '5432',
        }
    }
