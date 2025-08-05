from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import JsonResponse  # ✅ add this

def index(request):  # ✅ root view
    return JsonResponse({"message": "Welcome to the Grocery Store API!"})

urlpatterns = [
    path('', index),  # ✅ root URL
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
