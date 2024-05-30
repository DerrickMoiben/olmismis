from django.urls import path, include
from . import views


urlpatterns = [
    path('login/', views.user_login,  name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('register-new-farmer/', views.register_new_farmer, name='register-new-farmer'),
    path('all-farmers/', views.all_farmers, name='all-farmers'),
    path('enter-weight/<int:farmer_id>/', views.enter_weight, name='enter-weight'),
    path('delete/<int:farmer_id>/', views.delete_farmer, name='delete-farmer'),
]
