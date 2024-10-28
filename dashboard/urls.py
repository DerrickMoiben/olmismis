from django.urls import path, include
from . import views


urlpatterns = [
    path('cashier-login/', views.cashier_login,  name='cashier-login'),
    path('cashier-signup/', views.cashier_signup, name='cashier-signup'),
    path('cashier-dashboard/', views.cashier_dashboard, name='cashier-dashboard'),
    path('register-new-farmer/', views.register_new_farmer, name='register-new-farmer'),
    path('cashier-farmers/', views.cashier_farmers, name='cashier-farmers'),
    path('announcements/', views.announcements, name='announcements'),
    path('print-farmers-report/', views.print_farmers_report, name='print-farmers-report'),
    path('create_harvest/', views.create_harvest, name='create_harvest'),
    path('update_harvest/<int:harvest_id>/', views.update_harvest, name='update_harvest'),
    path('create_season/', views.create_season, name='create_season'),
    path('select_harvest/', views.select_harvest, name='select_harvest'),
    path('manage_harvests/', views.manage_harvests, name='manage_harvests'),
    path('delete_harvest/<int:pk>/', views.delete_harvest, name='delete_harvest'),
    path('delete_season/<int:pk>/', views.delete_season, name='delete_season'),
    path('update_season/<int:season_id>/', views.update_season, name='update_season'),
    path('select_harvest_for_payment/', views.select_harvest_for_payment, name='select_harvest_for_payment'),  # URL for selecting harvest
    path('process-payments/<int:selected_harvest_id>/', views.process_payments, name='process_payments'),  # URL for processing payments
    path('cashier_edit_weight/', views.cashier_edit_weight, name='cashier_edit_weight'),  # URL for editing weigth
    path('print-payment-summary/', views.print_payment_summary, name='print_payment_summary'),
]