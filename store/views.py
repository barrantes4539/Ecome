from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, SignUpFormAdmin, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
import json
from cart.cart import  Cart
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .utils import generate_temp_password, store_recovery_code, send_temp_password_email
from django.core.cache import cache
import logging
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods




#ADMIN
def admin_categories(request):
    if request.user.is_authenticated and request.user.is_superuser:
        
        categories = Category.objects.all()
        return render(request, 'admin/admin_categories.html', {'categories':categories})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')
    
@require_POST
def update_categories(request):
    # Ensure the action is 'post'
    if request.POST.get('action') == 'post':
        # Get the category ID and the category name from POST data
        category_id = int(request.POST.get('category_id'))
        category_name = request.POST.get('category_name')

        # Update the category name in the database
        try:
            category = Category.objects.get(id=category_id)
            category.name = category_name
            category.save()
            return JsonResponse({'message': f"Categoría '{category_name}' actualizada correctamente."})
        except Category.DoesNotExist:
            return JsonResponse({'error': 'La categoría especificada no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_POST
def add_categories(request):
    # Ensure the action is 'post'
    if request.POST.get('action') == 'post':
        # Get the category ID and the category name from POST data
        new_category_name = request.POST.get('new_category_name')

        # Update the category name in the database
        try:
            # Create a new Category instance
            new_category = Category(name=new_category_name)
            # Save data in the database
            new_category.save()
            
            messages.success(request, "Categoría agregada exitosamente")
            return JsonResponse({'message': f"Categoría '{new_category_name}' agregada correctamente."})
        except Category.DoesNotExist:
            return JsonResponse({'error': 'La categoría especificada no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_POST
def delete_categories(request):
    # Ensure the action is 'post'
    if request.POST.get('action') == 'post':
        # Get the category ID and the category name from POST data
        category_id = int(request.POST.get('category_id'))
        category_name = request.POST.get('category_name')

        try:
            # Find the category by ID and delete it
            category = Category.objects.get(id=category_id)
            category_name = category.name  # Store category name for response message
            category.delete()
            
            return JsonResponse({'message': f"Categoría '{category_name}' eliminada correctamente."})
        except Category.DoesNotExist:
            return JsonResponse({'error': 'La categoría especificada no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def admin_products(request):
    if request.user.is_authenticated and request.user.is_superuser:
        products = Product.objects.select_related('category').all()
        categories = Category.objects.all()
        return render(request, 'admin/admin_products.html', {'products': products, 'categories':categories})
    else:
        return redirect('home')
    
@require_POST
def update_products(request):
    # Ensure that the request is POST
    if request.POST.get('action') == 'post':
        # Get data
        product_id = int(request.POST.get('product_id'))
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category_id = request.POST.get('product_category')  # Obtener el ID de la categoría
        product_image = request.FILES.get('product_image')  # Obtener la imagen del producto
        
        try:
            # Obtener el producto de la base de datos
            product = Product.objects.get(id=product_id)
            product.name = product_name
            product.sale_price = product_price
            
            # Actualizar la categoría solo si se proporcionó un ID válido y no es 'undefined'
            if product_category_id and product_category_id != 'undefined':
                product.category_id = int(product_category_id)

            # Actualizar la imagen solo si se proporcionó
            if product_image:
                product.image = product_image
            
            # Guardar el producto actualizado
            product.save()
            
            return JsonResponse({'message': f"Producto '{product_name}' actualizado correctamente."})
        
        except Product.DoesNotExist:
            return JsonResponse({'error': 'El producto especificado no existe.'}, status=404)
        
        except ValueError:
            return JsonResponse({'error': 'El ID del producto proporcionado no es válido.'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

@ensure_csrf_cookie
@require_POST
def add_products(request):
    # Verificar que la acción sea un POST
    if request.method == 'POST':
        new_product_name = request.POST.get('new_product_name')
        new_product_price = request.POST.get('new_product_price')
        new_product_category_id = request.POST.get('new_product_category')
        new_product_description = request.POST.get('new_product_description')
        new_product_img = request.FILES.get('new_product_img')

        try:
            # Crear una instancia de Product con los datos recibidos
            new_product = Product(
                name=new_product_name,
                sale_price=new_product_price,
                category_id=new_product_category_id,  # Usar category_id si es una clave externa
                description=new_product_description,
                image=new_product_img
            )
            new_product.save()

            messages.success(request, "Producto agregado exitosamente")
            return JsonResponse({'message': f"Producto '{new_product_name}' agregado correctamente."})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Devolver un error si la solicitud no es un POST
    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_POST
def delete_products(request):
    # Ensure the action is 'post'
    if request.POST.get('action') == 'post':
        # Get the category ID and the category name from POST data
        product_id = int(request.POST.get('product_id'))
        product_name = request.POST.get('product_name')

        try:
            # Find the category by ID and delete it
            product = Product.objects.get(id=product_id)
            product_name = product.name  # Store category name for response message
            product.delete()
            
            return JsonResponse({'message': f"Producto '{product_name}' eliminado correctamente."})
        except Category.DoesNotExist:
            return JsonResponse({'error': 'El producto especificada no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def admin_users(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST":
            if 'add_user' in request.POST:
                form = SignUpFormAdmin(request.POST)
                if form.is_valid():
                    user = form.save(commit=False)
                    user_type = form.cleaned_data['user_type']
                    if user_type == 'admin':
                        user.is_superuser = True
                        user.is_staff = True
                    else:
                        user.is_superuser = False
                        user.is_staff = False
                    form.save()
                    messages.success(request, "El usuario ha sido registrado exitósamente!!")
                    return redirect('admin_users')
                else:
                    error_messages = form.errors.as_data()
                    for field, errors in error_messages.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error.message}")
                    messages.error(request, "Ha habido un error registrando la cuenta, intente de nuevo")
                    return redirect('admin_users')
            # Agregar lógica adicional para otros formularios POST si es necesario

        else:
            form = SignUpFormAdmin()  # Create an empty form instance

        # Fetch all registered users and their related profile data
        users = User.objects.all().select_related('profile')
        
        return render(request, 'admin/admin_users.html', {
            'users': users,
            'form': form,
        })
    else:
        return redirect('home')
    
@require_POST
def update_users(request):
    # Asegúrate de que la solicitud sea POST
    if request.POST.get('action') == 'post':
        # Obtener datos del POST
        user_id = int(request.POST.get('user_id'))
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')

        try:
            # Obtener el usuario de la base de datos
            user = User.objects.get(id=user_id)
            
            # Actualizar los campos del usuario
            user.username = username
            user.email = email
            
            # Actualizar otros campos de UserProfile
            user.profile.phone = phone
            user.profile.address = address
            user.profile.address2 = address2
            user.profile.city = city
            user.profile.state = state
            user.profile.zipcode = zipcode
            user.profile.country = country
            
            # Guardar los cambios en el perfil del usuario
            user.profile.save()
            user.save()
            
            return JsonResponse({'message': f"Usuario '{username}' actualizado correctamente."})
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'El usuario especificado no existe.'}, status=404)
        
        except ValueError:
            return JsonResponse({'error': 'El ID del usuario proporcionado no es válido.'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

@require_POST
def add_users(request):
    # Ensure that the request is POST
    if request.POST.get('action') == 'post':
        # Get data
        product_id = int(request.POST.get('product_id'))
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_category_id = request.POST.get('product_category')  # Obtener el ID de la categoría
        product_image = request.FILES.get('product_image')  # Obtener la imagen del producto
        
        try:
            # Obtener el producto de la base de datos
            product = Product.objects.get(id=product_id)
            product.name = product_name
            product.sale_price = product_price
            
            # Actualizar la categoría solo si se proporcionó un ID válido y no es 'undefined'
            if product_category_id and product_category_id != 'undefined':
                product.category_id = int(product_category_id)

            # Actualizar la imagen solo si se proporcionó
            if product_image:
                product.image = product_image
            
            # Guardar el producto actualizado
            product.save()
            
            return JsonResponse({'message': f"Producto '{product_name}' actualizado correctamente."})
        
        except Product.DoesNotExist:
            return JsonResponse({'error': 'El producto especificado no existe.'}, status=404)
        
        except ValueError:
            return JsonResponse({'error': 'El ID del producto proporcionado no es válido.'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

@require_POST
def delete_users(request):
    #Asegúrate de que la solicitud sea POST
    if request.POST.get('action') == 'post':
        user_id_str = request.POST.get('user_id')

        if not user_id_str:
            return JsonResponse({'error': 'No se proporcionó un ID de usuario.'}, status=400)

        try:
            # Convertir user_id a entero
            user_id = int(user_id_str)

            # Obtener el usuario de la base de datos
            user = User.objects.get(id=user_id)

            # Eliminar el usuario
            user.delete()

            return JsonResponse({'message': f"Usuario con ID {user_id} eliminado correctamente."})

        except User.DoesNotExist:
            return JsonResponse({'error': 'El usuario especificado no existe.'}, status=404)

        except ValueError:
            return JsonResponse({'error': 'El ID del usuario proporcionado no es válido.'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

#END ADMIN

#USERS
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def about(request):
    return render(request, 'about.html', {})

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product})

def category(request, cat):
    #Grab the category from the url
    print(f"Received category: {cat}")
    try:
        
        # Look up the category
        category = Category.objects.get(name=cat)
        print(f"URL category: {category}")
        
        # Look up the product filtered by category
        products = Product.objects.filter(category=category)
        
        return render(request, 'category.html', {'products':products,'category':category})
    except:
        messages.success(request, ('La categoría no existe.'))
        return redirect('home')
#USERS
    
#AUTHENTICATION
def recovery_page(request):
    return render(request, 'auth/recovery_page.html', {})

# def login_user(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
            
#             try:
#                 # Retrieve the profile for the logged-in user
#                 current_user_profile = Profile.objects.get(user=user)
                
#                 # Get the saved cart (old_cart) from database
#                 saved_cart = current_user_profile.old_cart
                
#                 if saved_cart:
#                     try:
#                         # Convert database string to Python dictionary
#                         converted_cart = json.loads(saved_cart)
                        
#                         # Add the loaded cart items to the current session cart
#                         cart = Cart(request)
#                         for key, value in converted_cart.items():
#                             cart.db_add(product=key, quantity=value)
                        
#                         messages.success(request, "Has iniciado sesión")
#                     except json.JSONDecodeError:
#                         messages.error(request, "Error al cargar el carrito guardado")
#                 else:
#                     messages.info(request, "Agrega productos a tu carrito!!")
                
#                 return redirect('home')
            
#             except Profile.DoesNotExist:
#                 messages.error(request, "No se encontró el perfil asociado con su cuenta")
#                 return redirect('login')
            
#         else:
#             messages.error(request, "Usuario o contraseña incorrectos")
#             return redirect('login')
    
#     return render(request, 'auth/login.html', {})

def login_user(request):
    if request.method == "POST":
        login_input = request.POST.get('login')  # Nombre de usuario o correo electrónico
        password = request.POST.get('password')

        # Intentar autenticar usando nombre de usuario
        user = authenticate(request, username=login_input, password=password)

        # Si no se encontró un usuario con el nombre de usuario, intentar con el correo electrónico
        if user is None:
            try:
                # Intentar obtener el usuario por correo electrónico
                user = User.objects.get(email=login_input)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            try:
                # Retrieve the profile for the logged-in user
                current_user_profile = Profile.objects.get(user=user)
                
                # Get the saved cart (old_cart) from database
                saved_cart = current_user_profile.old_cart
                
                if saved_cart:
                    try:
                        # Convert database string to Python dictionary
                        converted_cart = json.loads(saved_cart)
                        
                        # Add the loaded cart items to the current session cart
                        cart = Cart(request)
                        for key, value in converted_cart.items():
                            cart.db_add(product=key, quantity=value)
                        
                        messages.success(request, "Has iniciado sesión")
                    except json.JSONDecodeError:
                        messages.error(request, "Error al cargar el carrito guardado")
                else:
                    messages.info(request, "Agrega productos a tu carrito!!")
                
                return redirect('home')
            
            except Profile.DoesNotExist:
                messages.error(request, "No se encontró el perfil asociado con su cuenta")
                return redirect('login')
            
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect('login')
    
    return render(request, 'auth/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("Has cerrado sesión"))
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                form.add_error('email', "Este correo electrónico ya está registrado.")
                return render(request, 'auth/register.html', {'form': form})
            
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "¡Has sido registrado exitosamente!")
                return redirect('user_info')
            else:
                messages.error(request, "Error al autenticar al usuario.")
        else:
            messages.error(request, "Ha habido un error registrando su cuenta, intente de nuevo")
    else:
        form = SignUpForm()

    return render(request, 'auth/register.html', {'form': form})

def user_info(request):
    if not request.user.is_authenticated:
        return redirect('login')
    #Get current User
    current_user = Profile.objects.get(user__id=request.user.id)
    #Get current User's Shipping Info
    shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
    #Get original User Form
    form = UserInfoForm(request.POST or None, instance=current_user)
    #Get User Shipping Form
    shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
    if form.is_valid() or shipping_form.is_valid():
        #Save Original form
        form.save()
        #Save shipping form
        shipping_form.save()
        messages.success(request, ("Tu información ha sido actualizada exitosamente!!"))
        return redirect('home')
    return render(request, 'user_info.html', {'form': form, 'shipping_form': shipping_form})

def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, ("Tu perfil ha sido actualizado exitosamente!!"))
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'user_profile.html', {'user_form': user_form})


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Has cambiado la contraseña exitosamente")
                login(request, current_user)
                return redirect('user_profile')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, ("Debes iniciar sesión primero"))
        return redirect('login')

@require_http_methods(["GET", "POST"])
def reset_password(request):
    if request.method == 'POST':
        data = request.POST
        email = data.get('email')
        new_password1 = data.get('new_password1')
        new_password2 = data.get('new_password2')

        if new_password1 != new_password2:
            return JsonResponse({'error': 'Las contraseñas no coinciden.'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)
        
        user.set_password(new_password1)
        user.save()
        
        # Actualizar la sesión del usuario actualizada
        update_session_auth_hash(request, user)
        
        return JsonResponse({'success': 'Contraseña actualizada correctamente.', 'redirect_url':'/login/'})
    
    # En caso de solicitud GET, recuperar el email de la sesión
    email = request.session.get('recovery_email', '')
    return render(request, 'auth/reset_password.html', {'email': email})
    
@require_POST
def send_email_recovery(request):
    email = request.POST.get('email')
    
    if not email:
        return JsonResponse({'error': 'El correo electrónico es requerido.'}, status=400)
    
    try:
        # Verificar si el correo electrónico existe en la base de datos
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'No se encontró un usuario con ese correo electrónico.'}, status=404)
        
        # Generar y almacenar el código de recuperación
        temp_password = generate_temp_password()
        store_recovery_code(email, temp_password)
        
        # Enviar el código de recuperación por correo electrónico
        send_temp_password_email(email, temp_password)
        
        return JsonResponse({'message': 'El código de recuperación ha sido enviado a tu correo electrónico.'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
   
logger = logging.getLogger(__name__)
@require_POST
def verify_recovery_code(request):
    email = request.POST.get('email')
    recovery_code = request.POST.get('recoveryCode')
    
    if not email or not recovery_code:
        return JsonResponse({'error': 'Email y código de recuperación son requeridos.'}, status=400)

    stored_code = cache.get(f'recovery_code_{email}')
    
    if stored_code:
        if stored_code == recovery_code:
            cache.delete(f'recovery_code_{email}')
            # Almacenar el email en la sesión
            request.session['recovery_email'] = email
            # Redirigir a la página de restablecimiento de contraseña
            return JsonResponse({'success': True, 'message': 'Código verificado correctamente.'})
        else:
            return JsonResponse({'error': 'Código de recuperación inválido.'}, status=400)
    else:
        return JsonResponse({'error': 'Código de recuperación ha expirado o es inválido.'}, status=400)
#END AUTHENTICATION
