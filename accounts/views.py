from django.shortcuts import render
from accounts.services import (
    register_user,
    login_user
)


def signup(request):
    if request.POST:
        register_user(request.POST)
    return render(request, template_name='accounts/signup.html')


def login(request):
    if request.POST:
        is_logged = login_user(request.POST)
        if is_logged:
            request.session['logged'] = True
    return render(request, template_name='accounts/login.html')
