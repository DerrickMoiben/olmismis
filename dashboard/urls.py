from django.urls import path, include
from . import views


urlpatterns = [
    # path('admin/', views.admin, name='admin'),
    path('cashier-login/', views.cashier_login,  name='cashier-login'),
    path('cashier-signup/', views.cashier_signup, name='cashier-signup'),
    path('cashier-dashboard/', views.cashier_dashboard, name='cashier-dashboard'),
    path('register-new-farmer/', views.register_new_farmer, name='register-new-farmer'),
    path('cashier-farmers/', views.cashier_farmers, name='cashier-farmers'),
    #path('enter-weight/<int:farmer_id>/', views.enter_weight, name='enter-weight'),
]
