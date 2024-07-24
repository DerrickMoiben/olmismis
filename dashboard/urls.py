from django.urls import path, include
from . import views


urlpatterns = [
    path('cashier-login/', views.cashier_login,  name='cashier-login'),
    path('cashier-signup/', views.cashier_signup, name='cashier-signup'),
    path('cashier-dashboard/', views.cashier_dashboard, name='cashier-dashboard'),
    path('register-new-farmer/', views.register_new_farmer, name='register-new-farmer'),
    path('cashier-farmers/', views.cashier_farmers, name='cashier-farmers'),
    #path('enter-weight/<int:farmer_id>/', views.enter_weight, name='enter-weight'),
    path('announcements/', views.announcements, name='announcements'),
    path('print-farmers-report/', views.print_farmers_report, name='print-farmers-report'),
    path('create_harvest/', views.create_harvest, name='create_harvest'),
    path('update_harvest/', views.update_harvest, name='update_harvest'),
    path('all_harvests/', views.all_harvests, name='all_harvests'),
    path('create_season/', views.create_season, name='create_season'),
    
]