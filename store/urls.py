from django.urls import path, include
from . import views

urlpatterns = [
    #DEFAULT URL
    path('', views.home, name='home'),
    #STORE
    path('about/', views.about, name='about'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:cat>', views.category, name='category'),
    #AUTHENTICATION
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('send_email_recovery/', views.send_email_recovery, name='send_email_recovery'),
    path('recovery_page/', views.recovery_page, name='recovery_page'),  # URL para mostrar el formulario de recuperación
    path('verify_recovery_code/', views.verify_recovery_code, name='verify_recovery_code'), 
    path('reset_password/', views.reset_password, name='reset_password'),  
    #USER
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user_info/', views.user_info, name='user_info'),
    path('update_password/', views.update_password, name='update_password'),
    #ADMIN
    path('admin_categories/', views.admin_categories, name='admin_categories'),
    path('update_categories/', views.update_categories, name='update_categories'),
    path('add_categories/', views.add_categories, name='add_categories'),
    path('delete_categories/', views.delete_categories, name='delete_categories'),
    path('admin_products/', views.admin_products, name='admin_products'),
    path('update_products/', views.update_products, name='update_products'),
    path('add_products/', views.add_products, name='add_products'),
    path('delete_products/', views.delete_products, name='delete_products'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('update_users/', views.update_users, name='update_users'),
    path('add_users/', views.add_users, name='add_users'),
    path('delete_users/', views.delete_users, name='delete_users'),
    
]
