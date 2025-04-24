from rest_framework import serializers
from .models import NewsArticle
from accounts.models import ArticleView, ArticleLike

class NewsArticleSerializer(serializers.ModelSerializer):
    view_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'content', 'url', 'category',
            'writer', 'write_date', 'keywords',
            'view_count', 'like_count', 'is_liked'
        ]
        read_only_fields = ['id', 'write_date']

    def get_view_count(self, obj):
        return ArticleView.objects.filter(article=obj).count()

    def get_like_count(self, obj):
        return ArticleLike.objects.filter(article=obj).count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ArticleLike.objects.filter(
                user=request.user,
                article=obj
            ).exists()
        return False 