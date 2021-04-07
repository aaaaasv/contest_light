from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'accounts'
urlpatterns = [
                  path('signup/', views.signup, name='signup'),
                  path('login/', views.login, name='login'),
                  path('ajax-send-code/', views.ajax_send_code, name='ajax-send-code'),
                  path('ajax-check-code/', views.ajax_check_code, name='ajax-check-code'),
              ] \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
