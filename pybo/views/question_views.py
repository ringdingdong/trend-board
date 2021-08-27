import sys
import os

from pybo.models import Question, Document
from pybo.forms import QuestionForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
import json

from twitter import *

import requests
#-----------------------------------------------------------------------
# load our API credentials
#-----------------------------------------------------------------------
consumer_key = "tWSoKJjXG1huVc3a4AtoJdteK"
consumer_secret = "3aOhU0QjVkG1f0Tm1raU6xEjMAy4SiU8KfAZszpomtiG52nCMd"  
access_key = "1395637087836143619-PU6CIt82rK7ZoLBdZ8M13JYd7SXW40"
access_secret = "gFhAQUf28Kw5nkfXhrLU7NKJE9GovrrLGvoWgFlPNzFcW"

@login_required(login_url='common:login')
def question_create(request):
    """
    pybo 질문등록
    """
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()
            question.content = question.content.replace('<', '&lt;').replace('>', '&gt;')
            question.save()
            for img in request.FILES.getlist('imgs'):
                # document 객체를 하나 생성한다.
                document = Document()
                # 외래키로 현재 생성한 Post의 기본키를 참조한다.
                document.post = question
                # imgs로부터 가져온 이미지 파일 하나를 저장한다.
                document.file = img
                # 데이터베이스에 저장
                document.save()
            return redirect('pybo:board')
    else:
        form = QuestionForm()
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)


@login_required(login_url='common:login')
def question_modify(request, question_id):
    """
    pybo 질문수정
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()
            for img in request.FILES.getlist('imgs'):
                print(img)
                # document 객체를 하나 생성한다.
                document = Document()
                # 외래키로 현재 생성한 Post의 기본키를 참조한다.
                document.post = question
                # imgs로부터 가져온 이미지 파일 하나를 저장한다.
                document.image = img
                # 데이터베이스에 저장
                document.save()
            return redirect('pybo:board')
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)


@login_required(login_url='common:login')
def question_delete(request, question_id):
    """
    pybo 질문삭제
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    question.delete()
    return redirect('pybo:index')


def save_user_geolocation(request):
    if request.method == 'POST':
        latitude_ = request.POST['lat']
        longitude_ = request.POST['long']
        
        twitter = Twitter(auth = OAuth(access_key,
                access_secret,
                consumer_key,
                consumer_secret))

        results = twitter.trends.closest(lat = latitude_, long=longitude_)
        results = twitter.trends.place(_id = results[0]['woeid'])
        
        out= []
        for location in results:
            i=100000
            for trend in location["trends"]:
                i-=1000
                out.append({ "tag":trend["name"], "count": i})
        
        return HttpResponse(json.dumps(out), content_type="application/json")
      



