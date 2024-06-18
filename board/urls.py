from . import views
from django.urls import path, include

urlpatterns = [
    path('admin/', views.admin, name='admin'),
    path('all-farmers/', views.all_farmers, name='all-farmers'),
    path('delete/<int:farmer_id>/', views.delete_farmer, name='delete-farmer'),
    path('print-farmer-report/', views.print_farmer_report, name='print-farmer-report'),
]