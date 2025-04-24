from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login),
    path("article/view/", views.record_article_view),
    path("article/like/", views.toggle_article_like),
    path("activity/", views.get_user_activity),
]