from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from .serializers import CustomRegisterSerializer, CustomLoginSerializer, UserProfileUpdateSerializer, PasswordChangeSerializer
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
from articles.models import ArticleLike, ArticleView, ArticleScrap, NewsArticle
from .serializers import (
    UserProfileSerializer,
    UserLikedArticleSerializer,
    UserViewedArticleSerializer,
    UserScrappedArticleSerializer,
    SimpleNewsArticleSerializer,
    NewsArticleSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from utils import parse_embedding, cosine_similarity
import numpy as np
from django.db.models import Count
from django.utils import timezone
from django.db.models.functions import TruncDate
import json
import re
from datetime import datetime, timedelta


"""
회원가입 및 로그인 관련
"""
# Create your views here.
class custom_register(RegisterView):
    serializer_class = CustomRegisterSerializer
    
    def create_jwt_response(self, user):
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
            'message': '회원가입이 성공하였습니다.'
        }
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save(request)
            return Response(self.create_jwt_response(user), status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # 회원가입 실패 시 커스텀 메시지 반환
            return Response(
                {
                    "message": "회원가입에 실패하였습니다.",
                    "detail": e.detail  # 에러 상세 정보도 같이 반환
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class custom_login(LoginView):
    serializer_class = CustomLoginSerializer
    
    def create_jwt_response(self, user):
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
            'message': '로그인이 성공하였습니다.'
        }
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            user = self.user
            return Response(self.create_jwt_response(user), status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({
                'message': '로그인에 실패하였습니다.',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


"""
유저 상세 정보 조회
"""
@api_view(['GET', 'PUT'])
def user_details(request, pk):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return Response({'message': '인증이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        user = get_object_or_404(User, pk=pk)
        user_data = UserProfileSerializer(user).data
        
        liked_articles = ArticleLike.objects.filter(user=user).order_by('-liked_at') # 필요 시 뒤에 [:10]와 같은 식으로 추가
        viewed_articles = ArticleView.objects.filter(user=user).order_by('-viewed_at')
        scrapped_articles = ArticleScrap.objects.filter(user=user).order_by('-scrapped_at')
        
        return Response({
            'user': user_data,
            'liked_articles': UserLikedArticleSerializer(liked_articles, many=True).data,
            'viewed_articles': UserViewedArticleSerializer(viewed_articles, many=True).data,
            'scrapped_articles': UserScrappedArticleSerializer(scrapped_articles, many=True).data,
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return Response({'message': '인증이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response({'message': '관리자만 접근 가능합니다.'}, status=status.HTTP_403_FORBIDDEN)
            
        user = get_object_or_404(User, pk=pk)
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '프로필이 성공적으로 업데이트되었습니다.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'message': '프로필 업데이트 실패', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


"""
유저의 기사 조회
"""
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

        ArticleView.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        return Response(
            {'message': '기사 조회 기록이 저장되었습니다.'},
            status=status.HTTP_200_OK
        )        
    except NewsArticle.DoesNotExist:
        return Response(
            {'error': '해당 기사를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )


"""
유저의 기사 좋아요
"""
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


"""
유저의 기사 스크랩
"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_article_scrap(request):
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
    
    scrap, created = ArticleScrap.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    if not created:
        scrap.delete()
        return Response(
            {'message': '스크랩이 취소되었습니다.'},
            status=status.HTTP_200_OK
        )
    
    return Response(
        {'message': '스크랩이 등록되었습니다.'},
        status=status.HTTP_201_CREATED
    )


"""
유저가 특정 기사를 좋아요했는지 확인
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_article_like(request):
    article_url = request.query_params.get('url')
    
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
    
    is_liked = ArticleLike.objects.filter(
        user=request.user,
        article=article
    ).exists()
    
    return Response({
        'is_liked': is_liked
    }, status=status.HTTP_200_OK)



"""
유저의 기록을 바탕으로 특정 기사 추천
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_articles(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'detail': '해당 유저가 존재하지 않습니다.'}, status=404)

    # 최근 상호작용 기사 10개씩 가져오기 (중복 제거)
    viewed_ids = list(ArticleView.objects.filter(user=user).order_by('-viewed_at').values_list('article_id', flat=True)[:10])
    liked_ids = list(ArticleLike.objects.filter(user=user).order_by('-liked_at').values_list('article_id', flat=True)[:10])
    scrapped_ids = list(ArticleScrap.objects.filter(user=user).order_by('-scrapped_at').values_list('article_id', flat=True)[:10])
    interacted_ids = list(set(viewed_ids + liked_ids + scrapped_ids))

    if not interacted_ids:
        return Response({'detail': '추천을 위한 상호작용 기록이 없습니다.'}, status=200)

    # 임베딩 평균 구하기
    embeddings = []
    for article_id in interacted_ids:
        try:
            article = NewsArticle.objects.get(pk=article_id)
            emb = parse_embedding(article.content_embedding)
            embeddings.append(emb)
        except Exception:
            continue

    if not embeddings:
        return Response({'detail': '임베딩 정보가 없습니다.'}, status=200)

    mean_emb = np.mean(embeddings, axis=0)

    # 유저가 상호작용하지 않은 기사만 추천 대상으로
    exclude_ids = set(interacted_ids)
    candidates = NewsArticle.objects.exclude(pk__in=exclude_ids)
    similarities = []
    for article in candidates:
        try:
            emb = parse_embedding(article.content_embedding)
            sim = cosine_similarity(mean_emb, emb)
            similarities.append((sim, article))
        except Exception:
            continue

    # 유사도 내림차순 정렬 후 상위 5개
    sorted_articles = sorted(similarities, key=lambda x: x[0], reverse=True)
    top_articles = [a for _, a in sorted_articles[:5]]
    data = NewsArticleSerializer(top_articles, many=True).data

    return Response(data)


"""
유저의 대시보드 정보 (통계)
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    user = request.user
    
    # 총 읽은 기사 수
    total_views = ArticleView.objects.filter(user=user).count()
    
    # 총 좋아요 수
    total_likes = ArticleLike.objects.filter(user=user).count()
    
    # 총 스크랩 수
    total_scraps = ArticleScrap.objects.filter(user=user).count()
    
    # 자주 읽는 카테고리 (상위 5개)
    viewed_articles = ArticleView.objects.filter(user=user).values_list('article_id', flat=True)
    
    # 카테고리별 집계를 위한 쿼리
    category_counts = []
    
    if viewed_articles:
        # 카테고리별 조회 수 계산
        category_stats = NewsArticle.objects.filter(id__in=viewed_articles) \
            .values('category') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:5]
        
        # None 값 처리 및 결과 형식화
        for item in category_stats:
            if item['category']:  # None이 아닌 경우만 추가
                category_counts.append({
                    'category': item['category'],
                    'count': item['count']
                })
    
    return Response({
        'total_articles': total_views,
        'total_likes': total_likes,
        'total_scraps': total_scraps,
        'favorite_categories': category_counts
    })

"""
키워드 빈도수 계산
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_keyword_frequency(request):
    user = request.user
    
    # 사용자가 읽은 기사 ID 목록
    viewed_articles = ArticleView.objects.filter(user=user).values_list('article_id', flat=True)
    
    # 키워드 빈도수 계산
    keywords_data = []
    
    if viewed_articles:
        # 기사에서 키워드 추출 및 빈도수 계산
        keyword_counts = {}
        articles = NewsArticle.objects.filter(id__in=viewed_articles)

        for article in articles:
            try:
                # 키워드 추출 로직
                article_keywords = []
                
                # 문자열로 저장된 경우 파싱 시도
                if isinstance(article.keywords, str):
                    try:
                        # JSON 형식으로 파싱 시도
                        article_keywords = json.loads(article.keywords)
                    except json.JSONDecodeError:
                        # 정규식으로 추출 시도
                        article_keywords = re.findall(r"'([^']*)'", article.keywords)
                # 이미 리스트인 경우
                elif isinstance(article.keywords, list):
                    article_keywords = article.keywords
                
                # 추출된 키워드 처리
                if article_keywords:
                    # None이 아닌 값만 필터링하고, strip 처리
                    cleaned_keywords = [kw.strip() for kw in article_keywords if kw and isinstance(kw, str)]
                    
                    for kw in cleaned_keywords:
                        if kw:
                            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            except (AttributeError, TypeError):
                # 키워드가 None이거나 처리할 수 없는 형식인 경우 건너뜀
                continue
                
        # 빈도수 기준 내림차순 정렬 후 상위 10개 선택
        keywords_data = [{'keyword': k, 'count': v} for k, v in 
                         sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
    return Response(keywords_data)

"""
최근 일주일간 일별 읽은 기사 수
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weekly_reads(request):
    user = request.user
    
    # 현재 날짜 기준 최근 7일
    today = timezone.now().date()
    days = [(today - timezone.timedelta(days=i)) for i in range(6, -1, -1)]
    
    # 날짜를 한꺼번에 필터링하여 조회수 계산
    week_start = timezone.datetime.combine(days[0], timezone.datetime.min.time())
    week_end = timezone.datetime.combine(days[-1], timezone.datetime.max.time())
    
    views_in_week = ArticleView.objects.filter(
        user=user,
        viewed_at__range=(week_start, week_end)
    )
    
    # 일별로 그룹화하여 개수 계산
    daily_views = views_in_week.annotate(
        view_date=TruncDate('viewed_at')
    ).values('view_date').annotate(
        count=Count('id')
    ).order_by('view_date')
    
    # 일별 조회수 매핑
    view_counts_map = {view['view_date']: view['count'] for view in daily_views}
    
    # 각 날짜에 대한 조회수 결과 (없으면 0)
    daily_counts = []
    for day in days:
        count = view_counts_map.get(day, 0)
        daily_counts.append(count)
    
    return Response(daily_counts)

"""
좋아요한 기사 목록
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorite_articles(request):
    user = request.user

    # 좋아요한 기사 가져오기 (최신순 정렬, 최대 10개)
    liked_articles = ArticleLike.objects.filter(user=user).order_by('-liked_at')[:10]
    
    # 기사 ID 목록
    article_ids = [liked.article_id for liked in liked_articles]
    
    # 좋아요 수와 조회수 미리 계산 (N+1 쿼리 문제 방지)
    like_counts = {}
    view_counts = {}
    
    article_likes = ArticleLike.objects.filter(article_id__in=article_ids).values('article').annotate(count=Count('id'))
    article_views = ArticleView.objects.filter(article_id__in=article_ids).values('article').annotate(count=Count('id'))
    
    for like in article_likes:
        like_counts[like['article']] = like['count']
    
    for view in article_views:
        view_counts[view['article']] = view['count']
    
    # 기사 정보 구성
    articles = []
    for liked in liked_articles:
        try:
            article = liked.article
            
            # 필요한 기사 정보만 선택적으로 포함
            article_data = {
                'id': article.id,
                'title': article.title,
                'category': article.category,
                'writer': article.writer,
                'write_date': article.write_date,
                'url': article.url,
                'summary': article.summary,
                'like_count': like_counts.get(article.id, 0),
                'view_count': view_counts.get(article.id, 0)
            }
            articles.append(article_data)
        except NewsArticle.DoesNotExist:
            # 기사가 삭제된 경우 처리
            continue
        except Exception as e:
            # 기타 예외 처리
            print(f"Error processing article: {e}")
    
    return Response(articles)

"""
비밀번호 변경
"""
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        return Response({'message': '다른 사용자의 비밀번호 변경 시도'}, status=status.HTTP_403_FORBIDDEN)
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=status.HTTP_200_OK)
    return Response({'message': '비밀번호 변경 실패', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_stats(request, user_pk):
    """
    user_id를 쿼리 파라미터로 받아 최근 1주일과 그 전 1주일의 기사 읽기, 좋아요, 스크랩 수 및 증감률을 반환
    """
    user = get_object_or_404(User, pk=user_pk)
    if user != request.user:
        return Response({'message': '다른 사용자의 주간 통계 조회 시도'}, status=status.HTTP_403_FORBIDDEN)

    now = timezone.now()
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)
    last_week_end = this_week_start

    # 이번주
    view_this_week = ArticleView.objects.filter(user=user, viewed_at__gte=this_week_start, viewed_at__lt=now).count()
    like_this_week = ArticleLike.objects.filter(user=user, liked_at__gte=this_week_start, liked_at__lt=now).count()
    scrap_this_week = ArticleScrap.objects.filter(user=user, scrapped_at__gte=this_week_start, scrapped_at__lt=now).count()

    # 저번주
    view_last_week = ArticleView.objects.filter(user=user, viewed_at__gte=last_week_start, viewed_at__lt=last_week_end).count()
    like_last_week = ArticleLike.objects.filter(user=user, liked_at__gte=last_week_start, liked_at__lt=last_week_end).count()
    scrap_last_week = ArticleScrap.objects.filter(user=user, scrapped_at__gte=last_week_start, scrapped_at__lt=last_week_end).count()

    def percent_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    data = {
        'view': {
            'this_week': view_this_week,
            'last_week': view_last_week,
            'percent_change': percent_change(view_this_week, view_last_week)
        },
        'like': {
            'this_week': like_this_week,
            'last_week': like_last_week,
            'percent_change': percent_change(like_this_week, like_last_week)
        },
        'scrap': {
            'this_week': scrap_this_week,
            'last_week': scrap_last_week,
            'percent_change': percent_change(scrap_this_week, scrap_last_week)
        }
    }
    return Response(data, status=status.HTTP_200_OK)


"""
유저가 특정 기사를 스크랩했는지 확인
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_article_scrap(request):
    article_url = request.query_params.get('url')
    
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
    
    is_scraped = ArticleScrap.objects.filter(
        user=request.user,
        article=article
    ).exists()
    
    return Response({
        'is_scraped': is_scraped
    }, status=status.HTTP_200_OK)

"""
스크랩한 기사 목록
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scraped_articles(request):
    user = request.user

    # 스크랩한 기사 가져오기 (최신순 정렬, 최대 10개)
    scrapped_articles = ArticleScrap.objects.filter(user=user).order_by('-scrapped_at')[:10]
    
    # 기사 ID 목록
    article_ids = [scrapped.article_id for scrapped in scrapped_articles]
    
    # 좋아요 수와 조회수 미리 계산 (N+1 쿼리 문제 방지)
    like_counts = {}
    view_counts = {}
    
    article_likes = ArticleLike.objects.filter(article_id__in=article_ids).values('article').annotate(count=Count('id'))
    article_views = ArticleView.objects.filter(article_id__in=article_ids).values('article').annotate(count=Count('id'))
    
    for like in article_likes:
        like_counts[like['article']] = like['count']
    
    for view in article_views:
        view_counts[view['article']] = view['count']
    
    # 기사 정보 구성
    articles = []
    for scrapped in scrapped_articles:
        try:
            article = scrapped.article
            
            # 필요한 기사 정보만 선택적으로 포함
            article_data = {
                'id': article.id,
                'title': article.title,
                'category': article.category,
                'writer': article.writer,
                'write_date': article.write_date,
                'url': article.url,
                'summary': article.summary,
                'like_count': like_counts.get(article.id, 0),
                'view_count': view_counts.get(article.id, 0)
            }
            articles.append(article_data)
        except NewsArticle.DoesNotExist:
            # 기사가 삭제된 경우 처리
            continue
        except Exception as e:
            # 기타 예외 처리
            print(f"Error processing article: {e}")
    
    return Response(articles)