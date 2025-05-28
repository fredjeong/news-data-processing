from rest_framework import serializers
from .models import NewsArticle, ArticleLike, ArticleView, ArticleScrap

# 뉴스 기사 아이디로 기사 조회하는 시리얼라이저
class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'
    
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField() 
    scrap_count = serializers.SerializerMethodField()

    def get_view_count(self, obj):
        return ArticleView.objects.filter(article=obj).count()

    def get_like_count(self, obj):
        return ArticleLike.objects.filter(article=obj).count()
    
    def get_scrap_count(self, obj):
        return ArticleScrap.objects.filter(article=obj).count()

class SimpleNewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ['id', 'title']

# 좋아요 시리얼라이저
class ArticleLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleLike
        fields = '__all__'

# 조회수 시리얼라이저
class ArticleViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleView
        fields = '__all__'

# 스크랩 시리얼라이저
class ArticleScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleScrap
        fields = '__all__'
        
