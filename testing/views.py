from django.shortcuts import render
from .services import (
    update_results,
    get_news_list,
    get_one_news,
    get_reviews_list,
    create_review,
    get_available_quiz,
    set_user_grade
)


def quiz(request):
    context = {}
    if request.session.get('logged') and request.session.get('user_id'):
        availabe_quiz_url = get_available_quiz(request.session.get('user_id'))

        context = {'quiz_url': availabe_quiz_url}
    return render(request, 'testing/quiz.html', context=context)


def quiz_submit(request):
    update_results()


def news(request):
    context = get_news_list()
    return render(request, 'testing/news_list.html', context=context)


def news_detail(request, slug):
    news = get_one_news(slug)
    context = {
        'news': news
    }
    return render(request, 'testing/news_detail.html', context=context)


def reviews(request):
    if request.POST and request.POST.get('review_text') and request.session.get('user_id'):
        create_review(request.session['user_id'], request.POST.get('review_text'))
    context = get_reviews_list()
    return render(request, 'testing/reviews.html', context=context)


def quiz_list(request):
    context = {}

    if request.session.get('logged') and request.session.get('user_id'):
        availabe_quiz_url = get_available_quiz(request.session.get('user_id'))
        if request.POST:
            grade_id = request.POST.get('grade')
            set_user_grade(request.session.get('user_id'), grade_id)

        context = {'quiz': availabe_quiz_url}
    return render(request, 'testing/quiz_list.html', context=context)
