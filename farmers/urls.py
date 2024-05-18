from django.urls import path
from . import views

urlpatterns = [
    path('farmers/', views.farmers, name='farmers'),
    path('farmer-create/', views.farmer_create, name='farmer-create'),
    path('farmer-update/', views.farmer_update, name='farmer-update'),
    path('farmer-delete/<int:id>/', views.farmer_delete, name='farmer-delete'),
]