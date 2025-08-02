from django.urls import path
from .views import (
    RegisterView, ProductCreateView, ProductListView, AddToCartView,
    ViewCartView, RemoveFromCartView, CheckoutView,
    FilteredProductListView, ProductUpdateView, ProductDeleteView,
    WishlistView,SalesReportView,LowStockAlertView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('products/', ProductListView.as_view(), name='product-list'),      
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', ViewCartView.as_view(), name='view-cart'),
    path('cart/<int:pk>/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'), 

    path('products/filter/', FilteredProductListView.as_view(), name='filtered-products'),

    path('wishlist/', WishlistView.as_view(), name='wishlist'),  # GET, POST
    path('wishlist/<int:pk>/remove/', WishlistView.as_view(), name='wishlist-remove'),  # DELETE

    path('report/sales/', SalesReportView.as_view(), name='sales-report'),
    path('promos/low-stock/', LowStockAlertView.as_view(), name='low-stock'),


]
