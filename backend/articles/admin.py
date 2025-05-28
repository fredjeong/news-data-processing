from django.contrib import admin
from .models import NewsArticle, ArticleLike, ArticleView, ArticleScrap

# Register your models here.
admin.site.register(NewsArticle)
admin.site.register(ArticleLike)
admin.site.register(ArticleView)
admin.site.register(ArticleScrap)
