from django.urls import path, include
from . import views


urlpatterns = [
    # path('admin/', views.admin, name='admin'),
    path('login/', views.user_login,  name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('register-new-farmer/', views.register_new_farmer, name='register-new-farmer'),
    path('cashier-farmers/', views.cashier_farmers, name='cashier-farmers'),
    path('enter-weight/<int:farmer_id>/', views.enter_weight, name='enter-weight'),
    path('delete/<int:farmer_id>/', views.delete_farmer, name='delete-farmer'),
    path('print-farmer-report/', views.print_farmer_report, name='print-farmer-report'),
]
