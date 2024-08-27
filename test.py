# test_env.py
import environ

# Inicializa la lectura del archivo .env
env = environ.Env()
environ.Env.read_env()

# Imprime el valor de DJANGO_SECRET_KEY
print("DJANGO_SECRET_KEY:", env('DJANGO_SECRET_KEY', default=None))