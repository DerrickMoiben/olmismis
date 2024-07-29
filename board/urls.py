from . import views
from django.urls import path

urlpatterns = [
    path('singp/', views.singup, name='singup'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('all-farmers/', views.all_farmers, name='all-farmers'),
    path('delete/<int:farmer_id>/', views.delete_farmer, name='delete-farmer'),
    path('print-farmer-report/', views.print_farmer_report, name='print-farmer-report'),
    path('edit_farmer/<int:farmer_id>/', views.edit_farmer, name='edit_farmer'),
    path('add_farmer_with_number/', views.add_farmer_with_number, name='add_farmer_with_number'),
    path('admin/edit-requests/', views.admin_edit_requests, name='admin_edit_requests'),
    path('admin/approve-request/<int:request_id>/', views.approve_edit_request, name='approve_edit_request'),
    path('admin/reject-request/<int:request_id>/', views.reject_edit_request, name='reject_edit_request'),
]