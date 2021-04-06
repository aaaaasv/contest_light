from django.shortcuts import render

def quiz(request):
    return render(request, 'testing/quiz.html')