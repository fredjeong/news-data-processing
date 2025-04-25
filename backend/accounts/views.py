from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import User, ArticleView, ArticleLike
from .serializers import UserActivitySerializer, UserSerializer
from articles.models import NewsArticle

# Create your views here.


@csrf_exempt
@api_view(['POST'])
def login(request):
    # IP 기반 로그인 시도 횟수 제한
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'login_attempts_{ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 5:  # 5회 이상 실패 시
        return Response(
            {'error': '로그인 시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid(): # 유효성 검사
        user = form.get_user() # form에서 user 객체를 가져옴
        auth_login(request, user) # 로그인 함수 실행
        session_id = request.session.session_key # 세션 키 가져오기
        
        # 로그인 성공 시 시도 횟수 초기화
        cache.delete(cache_key)
        
        response_data = {
            'message': '로그인 성공',
            'session_id': session_id,
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    # 로그인 실패 시 시도 횟수 증가
    cache.set(cache_key, attempts + 1, timeout=300)  # 5분 동안 유지
    
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            if field == '__all__':
                error_messages.append('이메일 또는 비밀번호가 올바르지 않습니다.')
            else:
                error_messages.append(f'{field}: {error}')
    
    return Response(
        {'errors': error_messages},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_article_view(request):
    article_url = request.data.get('url')
    
    if not article_url:
        return Response(
            {'error': 'URL이 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        article = NewsArticle.objects.get(url=article_url)
    except NewsArticle.DoesNotExist:
        return Response(
            {'error': '해당 기사를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    ArticleView.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    return Response(
        {'message': '기사 조회 기록이 저장되었습니다.'},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_article_like(request):
    article_url = request.data.get('url')
    
    if not article_url:
        return Response(
            {'error': 'URL이 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        article = NewsArticle.objects.get(url=article_url)
    except NewsArticle.DoesNotExist:
        return Response(
            {'error': '해당 기사를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    like, created = ArticleLike.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    if not created:
        like.delete()
        return Response(
            {'message': '좋아요가 취소되었습니다.'},
            status=status.HTTP_200_OK
        )
    
    return Response(
        {'message': '좋아요가 등록되었습니다.'},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_activity(request, user_id):
    user = User.objects.get(id=user_id)
    # 최근 조회한 기사
    recent_views = ArticleView.objects.filter(
        user_id=user_id
    ).order_by('-viewed_at')#[:10]
    
    # 좋아요한 기사
    liked_articles = ArticleLike.objects.filter(
        user_id=user_id
    ).order_by('-liked_at')#
    
    data = {
        'recent_views': recent_views,
        'liked_articles': liked_articles
    }
    
    serializer = UserActivitySerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_detail(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)