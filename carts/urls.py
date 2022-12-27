from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_or_delete/<int:product_id>/<int:cart_item_id>/', views.remove_or_delete, name='remove_or_delete'),
    path('delete_cart/<int:product_id>/<int:cart_item_id>/', views.delete_cart, name='delete_cart'),
    path('checkout/', views.checkout, name='checkout')
]
