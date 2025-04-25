from rest_framework import serializers
from .models import ArticleView, ArticleLike, User
from articles.models import NewsArticle

class NewsArticleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'category', 'write_date']

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
    
    recent_views = ArticleViewSerializer(many=True)
    liked_articles = ArticleLikeSerializer(many=True) 