import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from accounts.services import (
    register_user,
    login_user,
    check_email_unique
)


def signup(request):
    context = {}
    if request.POST:
        try:
            register_user(request.POST)
            return redirect('accounts:login')
        except ValidationError as e:
            context = {'errors': e}
    return render(request, template_name='accounts/signup.html', context=context)


def login(request):
    context = {}
    if request.POST:
        is_logged, user_id = login_user(request.POST)
        if is_logged and user_id:
            request.session['logged'] = True
            request.session['user_id'] = user_id
            return redirect('testing:available-tests')
        else:
            context['errors'] = 'Електронна пошта або пароль введені неправильно'
    return render(request, template_name='accounts/login.html', context=context)


def logout(request):
    request.session['logged'] = None
    request.session['user_id'] = None
    return redirect('accounts:login')


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
