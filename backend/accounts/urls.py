from django.urls import path, include
from . import views

urlpatterns = [
    # 회원가입 및 로그인 관련
    path('signup/', views.custom_register.as_view(), name='signup'),
    path('login/', views.custom_login.as_view(), name='login'),
    
    # dj_rest_auth의 기본 뷰(로그아웃, 회원정보 등)는 아래에서 처리
    path('', include('dj_rest_auth.urls')),
    
    # 유저 정보 상세 조회, 프로필 수정
    path('<int:pk>/', views.user_details, name='user-detail-with-articles'),

    # 유저 비밀번호 변경
    path('<int:pk>/password/', views.change_password, name='user-password-change'),
    
    # 유저 추천 기사 조회
    path('<int:user_pk>/recommended/', views.recommended_articles, name='recommend-articles-for-user'),

    # 유저 기사 조회 기록 저장
    path('article/view/', views.record_article_view, name='record-article-view'),

    # 유저 기사 좋아요 기록 저장
    path('article/like/', views.toggle_article_like, name='toggle-article-like'),

    # 유저 기사 스크랩 기록 저장
    path('article/scrap/', views.toggle_article_scrap, name='toggle-article-scrap'),

    # 프론트에서 스크랩 여부 확인 필요하여 작성
    path("article/check-like/", views.check_article_like),

    # 프론트에서 스크랩 여부 확인
    path("article/check-scrap/", views.check_article_scrap),

    # 유저 주간 통계 조회
    path('<int:user_pk>/weekly-stats/', views.weekly_stats, name='weekly-stats'),
    

    ## 대시보드 관련 API
    
    # 좋아요 수, 조회 수, 카테고리 수
    path("dashboard/stats/", views.get_dashboard_stats),
    
    # 주요 키워드 빈도      
    path("dashboard/keywords/", views.get_keyword_frequency),
    
    # 최근 일주일 간 읽은 기사 수   
    path("dashboard/weekly-reads/", views.get_weekly_reads),
    
    # 좋아요한 기사 목록    
    path("dashboard/favorites/", views.get_favorite_articles),
    
    # 스크랩한 기사 목록
    path("dashboard/scraps/", views.get_scraped_articles),
]
