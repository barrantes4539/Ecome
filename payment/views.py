from django.shortcuts import render, get_object_or_404, redirect
from cart.cart import Cart
from django.http import JsonResponse
from django.contrib import messages
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime


#Admin
def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        
        #Get the order
        order = Order.objects.get(id=pk)
        #Get the order items
        items = OrderItem.objects.filter(order=pk)
        
        if request.POST:
            status = request.POST['shipping_status'] #True or False
            if status == "true":
                #Get the order
                order = Order.objects.filter(id=pk)
                #Update the status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now) #shipped and date_shipped come from payment/models
            else:
                #Get the order
                order = Order.objects.filter(id=pk)
                #Update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        
        return render(request, "payment/orders.html", {"order":order, "items":items})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status'] #True or False
            num = request.POST['num']
            #Get the order
            order = Order.objects.filter(id=num)
            
            #Grab Date and Time
            now = datetime.datetime.now()
            #Update Order
            order.update(shipped=True, date_shipped=now) #shipped and date_shipped come from payment/models

            #Message and Redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        
        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status'] #True or False
            num = request.POST['num']
            
            #Get the order
            order = Order.objects.filter(id=num)
            #Grab Date and Time
            now = datetime.datetime.now()
            #Update Order
            order.update(shipped=False) #shipped and date_shipped come from payment/models

            #Message and Redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        
        return render(request, "payment/shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

#Customer
def process_order(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_products
        quantities = cart.get_quants
        totals = cart.cart_total()

        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get('my_shipping')

        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None  # Usuario invitado

        # Crear orden
        create_order = Order(
            user=user,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid
        )
        create_order.save()

        # Agregar productos a la orden
        order_id = create_order.pk
        for product in cart_products():
            product_id = product.id
            price = product.sale_price
            for key, value in quantities().items():
                if int(key) == product.id:
                    OrderItem.objects.create(
                        order_id=order_id,
                        product_id=product_id,
                        quantity=value,
                        price=price,
                        user=user if not request.user.is_authenticated else None
                    )

        # Limpiar carrito (cookie y BD si está autenticado)
        if request.user.is_authenticated:
            Profile.objects.filter(user__id=request.user.id).update(old_cart="")
        if "session_key" in request.session:
            del request.session["session_key"]

        # Mostrar mensaje de éxito
        messages.success(request, "¡Tu compra ha sido realizada con éxito!")

        return redirect('home')
    
    else:
        messages.warning(request, "Acceso denegado.")
        return redirect('home')

def billing_info(request):
    
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_products
        quantities = cart.get_quants
        totals = cart.cart_total()
        
        #Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        
        #Check to see if user is Log In
        if request.user.is_authenticated:
            #Get the Billing Form
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals,"shipping_info":request.POST, "billing_form": billing_form})
        else:
            #Get the Billing Form
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals, "shipping_info":request.POST, "billing_form": billing_form})
        
    else:
        messages.success(request, "Acceso Denegado")
        return redirect('home')


def checkout(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_products
    quantities = cart.get_quants
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        #Checkout logged as user 
        return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals, "shipping_form": shipping_form})
    else:
        #Shipping Form
        shipping_form = ShippingForm(request.POST or None)
        # Checkout as guest
        return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals, "shipping_form": shipping_form})
    