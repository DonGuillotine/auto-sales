from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
    path('search', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('terms', views.terms, name='terms'),
    path('delivery', views.delivery, name='delivery'),
    path('refund', views.refund, name='refund'),
    path('privacy', views.privacy, name='privacy'),
    path('contact', views.contact, name='contact')
]
