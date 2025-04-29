
from pathlib import Path
import environ
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
# from dotenv import load_dotenv

# #Cargar las variables globales
# load_dotenv()

# Inicializa la lectura del archivo .env
env = environ.Env()
environ.Env.read_env(env_file=Path(__file__).resolve().parent.parent / '.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=False)

#HOSTS
ALLOWED_HOSTS = ['ecome-production.up.railway.app', 'https://ecome-production.up.railway.app']
CSRF_TRUSTED_ORIGINS = ['https://ecome-production.up.railway.app']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'cart',
    'payment',
    'whitenoise.runserver_nostatic',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'ecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'store.global_processors.navbar_categories',
                'cart.global_processors.cart',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp.gmail.com'  
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') 


WSGI_APPLICATION = 'ecom.wsgi.application'

#Database
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME':'railway',
        'USER':'postgres',
        'PASSWORD': env('DB_PASSWORD_YO'),
        'HOST':'tramway.proxy.rlwy.net',
        'PORT':'50273',
        #'NAME': BASE_DIR / env('DATABASE_NAME'),
    }
}
print("DATABASE CONFIG:", DATABASES)



# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
TIME_ZONE = env('TIME_ZONE', default='UTC')
USE_I18N = env.bool('USE_I18N', default=True)
USE_TZ = env.bool('USE_TZ', default=True)

#Whitenoise static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files (CSS, JavaScript, Images)
STATIC_URL = env('STATIC_URL', default='static/')
STATICFILES_DIRS = [BASE_DIR / env('STATICFILES_DIRS', default='static/')]
MEDIA_URL = env('MEDIA_URL', default='media/')
MEDIA_ROOT = BASE_DIR / env('MEDIA_ROOT', default='media/')

# Cloudinary settings - Django integration

cloudinary.config (
    CLOUD_NAME = env('CLOUD_NAME'),
    CLOUD_API_KEY = env('CLOUD_API_KEY'),
    CLOUD_API_SECRET = env('CLOUD_API_SECRET'),
)
# cloud name: dgrsokqj9
# api key: nyGA20WTcork2-6xd6Wd7aQXBns
# api name: 782651575152937
# api env variable: CLOUDINARY_URL=cloudinary://<your_api_key>:<your_api_secret>@dgrsokqj9

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
