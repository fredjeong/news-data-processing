from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes

# Create your views here.

from .models import NewsArticle
from accounts.models import ArticleView, ArticleLike
from .serializers import NewsArticleSerializer

#@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@api_view(['GET'])
@permission_classes([AllowAny])
def get_article_detail(request, article_id):
    try:
        article = NewsArticle.objects.get(id=article_id)
        serializer = NewsArticleSerializer(
            article,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except NewsArticle.DoesNotExist:
        return Response(
            {'error': '기사를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_article_list(request):
    articles = NewsArticle.objects.all()
    serializer = NewsArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
