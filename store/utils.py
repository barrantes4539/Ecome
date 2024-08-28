import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage


def generate_temp_password(length=8):
    #Genera una contraseña temporal aleatoria.
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def store_recovery_code(email, code):
    #Almacena el código de recuperación en caché con una expiración de 10 minutos.
    cache.set(f'recovery_code_{email}', code, timeout=600)  # 10 minutos de expiración

def get_recovery_code(email):
    #Recupera el código de recuperación desde caché.
    return cache.get(f'recovery_code_{email}')

def send_temp_password_email(email, temp_password):
    subject = 'Código de Recuperación de Contraseña'

    # URL absoluta para el logo (asegúrate de que el archivo esté accesible en esta URL)
    logo_url = 'https://drive.google.com/uc?id=1opKN2umF-2MOkPhfAnRgnsueljW4XDhd'  # Reemplaza con la URL real de tu logo

    # Contenido del mensaje HTML
    html_message = (
        '<html>'
        '<body>'
        '<div style="text-align: center; padding: 20px;">'
        '<img src="{logo_url}" alt="Logo de Ecom" style="width: 100px; height: auto; border-radius: 50%;" class="img-fluid">'
        '<p>Hola,</p>'
        '<p>Hemos recibido una solicitud para recuperar tu contraseña. A continuación encontrarás tu código de recuperación temporal:</p>'
        '<h2 style="color: #007BFF;">{}</h2>'
        '<p>Por favor, ingrésalo en el formulario de recuperación para restablecer tu contraseña. Este código es válido por 10 minutos.</p>'
        '<p>Si no solicitaste este código, por favor ignora este correo.</p>'
        '<p>Saludos cordiales,</p>'
        '<p>El equipo de soporte</p>'
        '</div>'
        '</body>'
        '</html>'
    ).format(temp_password, logo_url=logo_url)

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        # Utiliza EmailMessage para enviar el correo electrónico con contenido HTML
        email_message = EmailMessage(subject, html_message, from_email, recipient_list)
        email_message.content_subtype = 'html'  # Marca el contenido como HTML
        email_message.send()
    except Exception as e:
        # Aquí puedes registrar el error o manejarlo según tus necesidades
        print(f"Error al enviar el correo: {e}")
