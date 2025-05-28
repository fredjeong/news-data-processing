from django.shortcuts import render
from django.core.paginator import Paginator
# Create your views here.

from rest_framework import status
from .models import NewsArticle, ArticleLike, ArticleView, ArticleScrap
from .serializers import NewsArticleSerializer, SimpleNewsArticleSerializer, ArticleLikeSerializer, ArticleViewSerializer, ArticleScrapSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import numpy as np
from utils import parse_embedding, cosine_similarity
from accounts.models import User
from django.conf import settings
from elasticsearch import Elasticsearch

"""
전체 기사 목록 조회
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def article_list(request):
    articles = NewsArticle.objects.all()
    serializer = NewsArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



"""
기사 pk를 통해 조회 기사 상세 내용 조회
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def article_detail(request, pk):
    try:
        article = get_object_or_404(NewsArticle, pk=pk)
        serializer = NewsArticleSerializer(article, context={'request': request})
        
        # 조회수, 좋아요수, 스크랩수 추가
        response_data = serializer.data
        response_data['view_count'] = ArticleView.objects.filter(article=article).count()
        response_data['like_count'] = ArticleLike.objects.filter(article=article).count()
        response_data['scrap_count'] = ArticleScrap.objects.filter(article=article).count()
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except NewsArticle.DoesNotExist:
        return Response({'detail': '해당 기사가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

"""
기사 목록 조회
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def article_list_optimized(request):
    categories = {
        1: "전체",
        2: "연예",
        3: "경제",
        4: "교육",
        5: "국제",
        6: "산업",
        7: "정치",
        8: "지역",
        9: "건강",
        10: "문화",
        11: "취미",
        12: "스포츠",
        13: "사건사고",
        14: "사회일반",
        15: "IT/과학",
        16: "여성복지",
        17: "여행레저",
        18: "라이프스타일",
    }

    # 쿼리 파라미터에서 카테고리와 페이지 정보 가져오기
    try:
        category_id = int(request.query_params.get('category', 1))
    except (ValueError, TypeError):
        category_id = 1

    try:
        page = int(request.query_params.get('page', 1))
    except (ValueError, TypeError):
        page = 1

    try:
        page_size = int(request.query_params.get('page_size', 6))
    except (ValueError, TypeError):
        page_size = 6

    # 카테고리별 필터링
    if category_id == 1:
        articles = NewsArticle.objects.all()
    else:
        category_name = categories.get(category_id)
        if category_name:
            articles = NewsArticle.objects.filter(category=category_name)
        else:
            articles = NewsArticle.objects.all()

    # 최신순 정렬(옵션)
    articles = articles.order_by('-write_date')

    # 페이지네이션
    paginator = Paginator(articles, page_size)
    paginated_articles = paginator.get_page(page)
    serializer = NewsArticleSerializer(paginated_articles, many=True)

    response_data = {
        "count": paginator.count,
        "next": paginated_articles.has_next(),
        "previous": paginated_articles.has_previous(),
        "results": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": paginated_articles.number,
        "page_size": page_size
    }
    return Response(response_data, status=status.HTTP_200_OK)

# """
# 기사 목록 조회
# """
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def article_list_optimized(request):
#     categories = {
#         1: "전체",
#         2: "연예",
#         3: "경제",
#         4: "교육",
#         5: "국제",
#         6: "산업",
#         7: "정치",
#         8: "지역",
#         9: "건강",
#         10: "문화",
#         11: "취미",
#         12: "스포츠",
#         13: "사건사고",
#         14: "사회일반",
#         15: "IT/과학",
#         16: "여성복지",
#         17: "여행레저",
#         18: "라이프스타일",
#     }
    
#     # 쿼리 파라미터에서 카테고리와 페이지 정보 가져오기
#     category_id = request.query_params.get('category', 1)
#     page = int(request.query_params.get('page', 1))
#     page_size = 6
    
#     try:
#         category_id = int(category_id)
#     except ValueError:
#         category_id = 1
    
#     # 카테고리별 필터링
#     if category_id == 1:  # 전체
#         articles = NewsArticle.objects.all()
#     else:
#         category_name = categories.get(category_id)
#         if category_name:
#             articles = NewsArticle.objects.filter(category=category_name)
#         else:
#             articles = NewsArticle.objects.all()
    
#     # 전체 개수 계산
#     total_count = articles.count()
#     total_pages = (total_count + page_size - 1) // page_size  # 올림 계산
    
#     # 페이지네이션 적용
#     start_index = (page - 1) * page_size
#     end_index = start_index + page_size
#     paginated_articles = articles[start_index:end_index]
    
#     # 이전/다음 페이지 URL 생성
#     base_url = request.build_absolute_uri().split('?')[0]
#     next_url = None
#     previous_url = None
    
#     if page < total_pages:
#         next_url = f"{base_url}?category={category_id}&page={page + 1}"
    
#     if page > 1:
#         previous_url = f"{base_url}?category={category_id}&page={page - 1}"
    
#     # 시리얼라이저 적용
#     serializer = NewsArticleSerializer(paginated_articles, many=True)
    
#     # 응답 데이터 구성
#     response_data = {
#         "count": total_count,
#         "next": next_url,
#         "previous": previous_url,
#         "results": serializer.data,
#         "total_pages": total_pages,
#         "current_page": page,
#         "page_size": page_size
#     }
    
#     return Response(response_data, status=status.HTTP_200_OK)

"""
연관 기사 추천
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def related_articles(request, pk):
    try:
        article = get_object_or_404(NewsArticle, pk=pk)
    except NewsArticle.DoesNotExist:
        return Response({'detail': '해당 기사가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

    base_emb = parse_embedding(article.content_embedding)
    all_articles = NewsArticle.objects.exclude(pk=pk)
    similarities = []

    for article in all_articles:
        try:
            emb = parse_embedding(article.content_embedding)
            sim = cosine_similarity(base_emb, emb)
            similarities.append((sim, article))
        except Exception:
            continue

    # 유사도 내림차순 정렬 후 상위 5개
    sorted_articles = sorted(similarities, key=lambda x: x[0], reverse=True)
    
    if len(sorted_articles) < 5:
        top_related = sorted_articles
    else:
        top_related = sorted_articles[:5]
    
    top_articles = [a for _, a in top_related]
    data = NewsArticleSerializer(top_articles, many=True).data
    
    return Response(data, status=status.HTTP_200_OK)


"""
기사 검색 
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def search_articles(request):
    query = request.GET.get('q', '')
    
    if not query:
        return Response({'results': []})
    
    try:
        # Elasticsearch 클라이언트 설정
        es = Elasticsearch(
            [f"http://{settings.ES_CONFIG['host']}:{settings.ES_CONFIG['port']}"],
            basic_auth=(settings.ES_CONFIG['user'], settings.ES_CONFIG['password']),
            verify_certs=settings.ES_CONFIG['use_ssl']
        )
        
        # 검색 쿼리 실행
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content", "summary^2", "keywords^2"],
                    "type": "most_fields"
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {},
                    "summary": {}
                }
            },
            "size": 20
        }
        
        # Elasticsearch 검색 실행
        search_results = es.search(index=settings.ES_CONFIG['index'], body=search_query)
        
        # 검색 결과 형식화
        results = []
        for hit in search_results['hits']['hits']:
            source = hit['_source']
            
            # 하이라이트 처리
            highlights = {}
            if 'highlight' in hit:
                for field, highlighted_fragments in hit['highlight'].items():
                    highlights[field] = "...".join(highlighted_fragments)
            
            # PostgreSQL ID를 가져와서 해당 기사 정보 조회
            try:
                article_id = hit['_id']
                article = NewsArticle.objects.get(id=article_id)
                serializer = NewsArticleSerializer(article)
                article_data = serializer.data
                article_data['highlights'] = highlights
                article_data['score'] = hit['_score']
                results.append(article_data)
            except NewsArticle.DoesNotExist:
                # Elasticsearch에는 있지만 PostgreSQL에는 없는 경우
                result = {
                    'id': hit['_id'],
                    'title': source.get('title', ''),
                    'content': source.get('content', ''),
                    'summary': source.get('summary', ''),
                    'writer': source.get('writer', ''),
                    'write_date': source.get('write_date', ''),
                    'category': source.get('category', ''),
                    'url': source.get('url', ''),
                    'keywords': source.get('keywords', []),
                    'highlights': highlights,
                    'score': hit['_score']
                }
                results.append(result)
        
        return Response({'results': results})
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
기사 제목 자동완성
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def suggest_articles(request):
    query = request.GET.get('q', '')
    
    if not query:
        return Response({'suggestions': []})
    
    try:
        # Elasticsearch 클라이언트 설정
        es = Elasticsearch(
            [f"http://{settings.ES_CONFIG['host']}:{settings.ES_CONFIG['port']}"],
            basic_auth=(settings.ES_CONFIG['user'], settings.ES_CONFIG['password']),
            verify_certs=settings.ES_CONFIG['use_ssl']
        )
        
        # 제목 검색 쿼리 실행
        search_query = {
            "query": {
                "match_phrase_prefix": {
                    "title": {
                        "query": query,
                        "max_expansions": 10
                    }
                }
            },
            "_source": ["title"],
            "size": 3
        }
        
        # Elasticsearch 검색 실행
        search_results = es.search(index=settings.ES_CONFIG['index'], body=search_query)
        
        # 검색 결과 형식화
        suggestions = []
        seen_titles = set()  # 중복 제거를 위한 set
        
        for hit in search_results['hits']['hits']:
            title = hit['_source']['title']
            if title not in seen_titles:  # 중복 제거
                suggestions.append({
                    'text': title,
                    'score': hit['_score']
                })
                seen_titles.add(title)
            
        # 점수 기준 내림차순 정렬 후 상위 3개만 반환
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        # suggestions = suggestions[:3]
        
        return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)