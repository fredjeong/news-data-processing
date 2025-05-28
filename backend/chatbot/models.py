from django.db import models
from django.conf import settings
from articles.models import NewsArticle  # 기사 모델 import

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=(('user', 'User'), ('bot', 'Bot')))
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
