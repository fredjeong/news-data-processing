from django.shortcuts import render

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Create your views here.

@api_view(['POST'])
@method_decorator(csrf_exempt, name='dispatch')
def login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid(): # 유효성 검사
        user = form.get_user() # form에서 user 객체를 가져옴
        auth_login(request, user) # 로그인 함수 실행
        session_id = request.session.session_key # 세션 키 가져오기
        response_data = {
            'message': 'Login successful',
            'session_id': session_id
        }
        return Response(response_data, status=status.HTTP_200_OK)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)