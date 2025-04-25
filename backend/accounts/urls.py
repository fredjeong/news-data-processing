from django.urls import path, include
from . import views

urlpatterns = [
    # path("login/", views.login),
    path("", include('dj_rest_auth.urls')),
    path("article/view/", views.record_article_view),
    path("article/like/", views.toggle_article_like),
    path("<int:user_id>/", views.get_user_activity),
    path('signup/', include('dj_rest_auth.registration.urls')),
    # path("<int:user_id>/", views.get_user_detail),
]