from django.urls import path
from . import views

app_name = 'testing'
urlpatterns = [
    path('quiz', views.quiz, name='quiz')
]
