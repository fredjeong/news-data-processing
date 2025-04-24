from django.urls import path
from . import views

urlpatterns = [
    path('<int:article_id>/', views.get_article_detail, name='article-detail'),
] 