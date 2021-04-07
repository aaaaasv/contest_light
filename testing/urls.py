from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'testing'
urlpatterns = [
                  path('quiz/', views.quiz, name='quiz'),
                  path('quiz/submit/', views.quiz_submit, name='quiz-submit'),
                  path('news/', views.news, name='news'),
                  path('news/<slug:slug>/', views.news_detail, name='news_detail'),
                  path('reviews/', views.reviews, name='reviews'),
                  path('quiz_list/', views.quiz_list, name='available_tests')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
