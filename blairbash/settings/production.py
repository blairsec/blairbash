from .base import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['blairbash.org']
STATIC_ROOT = '/var/www/blairbash/static'
