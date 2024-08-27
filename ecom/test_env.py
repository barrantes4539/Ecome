import environ
from pathlib import Path

# Inicializa la lectura del archivo .env
env = environ.Env()
environ.Env.read_env(env_file=Path(__file__).resolve().parent.parent / '.env')

# Obtén el valor de DJANGO_SECRET_KEY
secret_key = env('DJANGO_SECRET_KEY', default=None)
print("DJANGO_SECRET_KEY:", secret_key)
