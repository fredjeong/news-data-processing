# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings


class NewsArticle(models.Model):
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    write_date = models.DateTimeField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    summary = models.TextField()
    url = models.CharField(unique=True, max_length=200)
    keywords = models.TextField(blank=True, null=True)  # This field type is a guess.
    title_embedding = models.TextField()  # This field type is a guess.
    content_embedding = models.TextField()  # This field type is a guess.

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'news_articles'

class ArticleLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')  # 한 유저가 한 기사에 한 번만 좋아요

class ArticleView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

class ArticleScrap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    scrapped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')  # 한 유저가 한 기사에 한 번만 스크랩
