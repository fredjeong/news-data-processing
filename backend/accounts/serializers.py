from rest_framework import serializers
from .models import ArticleView, ArticleLike
from articles.models import NewsArticle

class NewsArticleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'url', 'category', 'writer', 'write_date']

class ArticleViewSerializer(serializers.ModelSerializer):
    article = NewsArticleSimpleSerializer()

    class Meta:
        model = ArticleView
        fields = ['article', 'viewed_at']

class ArticleLikeSerializer(serializers.ModelSerializer):
    article = NewsArticleSimpleSerializer()

    class Meta:
        model = ArticleLike
        fields = ['article', 'liked_at']

class UserActivitySerializer(serializers.Serializer):
    recent_views = ArticleViewSerializer(many=True)
    liked_articles = ArticleLikeSerializer(many=True) 