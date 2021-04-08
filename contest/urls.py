
from django.urls import path, include
from testing.views import index

urlpatterns = [
    path('', index, name="index"),
    path('accounts/', include('accounts.urls')),
    path('testing/', include('testing.urls')),
]
