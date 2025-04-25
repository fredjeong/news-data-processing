from django.db import models
from pgvector.django import VectorField
import json

class NewsArticle(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    write_date = models.DateTimeField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    url = models.CharField(max_length=200)
    keywords = models.CharField(max_length=200)
    embedding = VectorField(dimensions=1024)
    summary = models.TextField()

    class Meta:
        db_table = 'news_articles'
        managed = False

    def __str__(self):
        return self.title

    def set_keywords(self, keywords):
        self.keywords = json.dumps(keywords)
    
    def get_keywords(self):
        return json.loads(self.keywords)