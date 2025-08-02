from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Cart

admin.site.register(User, UserAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']

admin.site.register(Cart, CartAdmin)

