import os
from .common import Common

class Production(Common):
    DEBUG = False
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', Common.SECRET_KEY)
    ALLOWED_HOSTS = ["*"]

    INSTALLED_APPS = Common.INSTALLED_APPS + ('gunicorn', 'storages',)

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('DJANGO_AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('DJANGO_AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.getenv('DJANGO_AWS_STORAGE_BUCKET_NAME', '')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_AUTO_CREATE_BUCKET = True
    AWS_QUERYSTRING_AUTH = False

    MEDIA_URL = f'https://s3.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/'

    AWS_HEADERS = {
        'Cache-Control': 'max-age=86400, s-maxage=86400, must-revalidate',
    }