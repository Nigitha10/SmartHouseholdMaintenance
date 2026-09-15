from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('appliances/', include('appliances.urls')),
    path('users/', include('users.urls')),
    path('', include('users.urls')),
]