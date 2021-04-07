import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail

from accounts.services import (
    register_user,
    login_user,
    check_email_unique
)


def signup(request):
    if request.POST:
        register_user(request.POST)
    return render(request, template_name='accounts/signup.html')


def login(request):
    if request.POST:
        is_logged, user_id = login_user(request.POST)
        if is_logged:
            request.session['logged'] = True
            request.session['user_id'] = user_id
    return render(request, template_name='accounts/login.html')


def ajax_send_code(request):
    email = request.GET.get('email')
    is_unique = check_email_unique(email)
    if not is_unique:
        return JsonResponse({'email_unique': 'false'}, status=200)

    code = random.sample(range(1, 9), 4)
    code = ' '.join(str(i) for i in code)
    send_mail(
        'Ваш код активації',
        code,
        'n0stalgia195@gmail.com',
        (email,),
        fail_silently=False
    )
    code = code.replace(' ', '')
    print(code)
    request.session['activation_code'] = code

    return HttpResponse()


def ajax_check_code(request):
    correct_code = request.session.get('activation_code')
    user_code = request.GET.get('userCode')
    is_confirmed = 'true'
    if user_code == correct_code:
        is_confirmed = 'true'
        request.session['email_confirmed'] = True
    print(user_code, correct_code, is_confirmed)
    return JsonResponse({"is_confirmed": is_confirmed}, status=200)


