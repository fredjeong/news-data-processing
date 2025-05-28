# Django 설치

### 1. VSCode Extension 설치

- `Django` 설치
- `Database Client` 설치
- `SQLite Viewer` 설치

### 2. Django Extension 환경설정

1. `ctrl(command)` + `shift` + `p`
2. `json` 검색
3. `Preferences: Open User Settings (JSON)` 선택
4. `settings.json` 파일에 아래 코드 붙여넣고 저장

```json
{
  // 아래 라인부터 드래그
  // Django
  "files.associations": {
    "**/*.html": "html",
	  "**/templates/**/*.html": "django-html",
    "**/templates/**/*": "django-txt",
    "**/requirements{/**,*}.{txt,in}": "pip-requirements"
  },
  "emmet.includeLanguages": {
    "django-html": "html"
  },
  "[django-html]": {
    "editor.autoClosingBrackets": "always"
	},
  // 여기까지 선택 후 복사
}
```

### 3. 가상환경에 아래 라이브러리 설치

    ```bash
    pip3 install django djangorestframework django-cors-headers requests dotenv
    ```

### 4. `./config/settings.py`에 하기 내용 추가 

```python
# .env파일로 부터 환경변수 불러오기
import os
from dotenv import load_dotenv
load_dotenv()

# 환경변수 불러오기
SECRET_KEY = os.getenv('SECRET_KEY')
POSTGRESQL_USERNAME = os.getenv('POSTGRESQL_USERNAME')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')

INSTALLED_APPS = {
    ...
    rest_framework,
    corsheaders,
    ...
}

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    ...
]
```

### 5. SQLite 대신 PostgreSQL과 연동

#### 5.1 (Optional) 기존 DB 삭제

1. PostgreSQL 접속
    
    ```bash
    sudo -i -u [username] psql -U postgres
    ```

2. PostgreSQL 비밀번호 입력

3. 기존 DB 삭제
    - 아래 커맨드 입력
        ```bash
        DROP DATABASE news;
        ```
    - 만약 다른 세션에서 해당 DB를 참고하고 있다면 아래 커맨드를 통해 pid 조회
        ```sql
        SELECT pid, usename, client_addr, state, query, backend_start
        FROM pg_stat_activity
        WHERE datname = 'news' AND pid <> pg_backend_pid(); -- Exclude your current session
        ```
    - 조회된 pid 사용 후 아래 커맨드 입력
        ```bash
        SELECT pg_terminate_backend(pid);
        ```
    - DB 삭제
        ```bash
        DROP DATABASE news;
        ```

#### 5.2 (optional) 새로운 DB 생성, pgvector 확장 설치, 테이블 생성

```bash
CREATE DATABASE news;

\c news;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    writer VARCHAR(255) NOT NULL,
    write_date TIMESTAMP NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    url VARCHAR(200) UNIQUE NOT NULL,
    keywords JSON DEFAULT '[]'::json,
    title_embedding VECTOR(1024) NOT NULL,
    content_embedding VECTOR(1024) NOT NULL
);
```

#### 5.3 PostgreSQL과 연동

```python
# ./config/settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "news",
        "USER": POSTGRESQL_USERNAME,
        "PASSWORD": POSTGRESQL_PASSWORD,
        "HOST": "localhost",
        "PORT": 5432,
    }
}
```

### 6. articles, accounts, chatbots 앱 생성

```bash
django-admin startapp articles
django-admin startapp accounts
django-admin startapp chatbot
```

```python
# ./config/settings.py

INSTALLED_APPS = [
    ...
    'articles',
    'accounts',
    'chatbot',
    ...
]
```

### 7. accounts 앱

1. 라이브러리 설치
    ```bash
    pip3 install djangorestframework-simplejwt dj-rest-auth django-allauth
    ```

2. `./config/settings.py` 설정
    ```python
    # ./config/settings.py

    INSTALLED_APPS = [
        ...
        'rest_framework.authtoken',
        'rest_framework_simplejwt',
        'dj_rest_auth',
        'dj_rest_auth.registration',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        ...
    ]

    AUTH_USER_MODEL = 'accounts.User'
    SITE_ID = 1
    REST_USE_JWT = True

    ACCOUNT_EMAIL_VERIFICATION = 'none' # 회원가입 과정에서 이메일 인증 사용 X

    ACCOUNT_AUTHENTICATION_METHOD = 'email' # 로그인 인증 방법으로 email 지정
    ACCOUNT_EMAIL_REQUIRED = True            # email 필드 사용 o
    ACCOUNT_USERNAME_REQUIRED = False        # username 필드 사용 x
    ACCOUNT_USER_MODEL_USERNAME_FIELD = 'email' # username 필드 사용 x

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        )
    }

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    }

    MIDDLEWARE = [
        ...
        'allauth.account.middleware.AccountMiddleware', # 회원가입 과정에서 이메일 인증 사용 X
        ...
    ]
    ```

3. `./accounts/models.py` 설정
    - Username 대신 이메일을 사용하는 등 변경사항이 존재하기 때문에 BaseUserManager를 상속받아 커스텀 헬퍼 클래스를 만들어야 함
        ```python
        # ./accounts/models.py

        from django.db import models
        from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

        class UserManager(BaseUserManager):

            def create_user(self, email, first_name, last_name, date_of_birth, password, **kwargs):
                if not email:
                    raise ValueError('Users must have an email address')

                user = self.model(
                    email=self.normalize_email(email),
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                )
                user.set_password(password)
                user.save(using=self._db)
                return user

            def create_superuser(self, email=None, first_name=None, last_name=None, date_of_birth=None, password=None, **extra_fields):
                superuser = self.create_user(
                    email=self.normalize_email(email),
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                    password=password,
                )
                superuser.is_admin = True
                superuser.save(using=self._db)
                return superuser


        class User(AbstractBaseUser, PermissionsMixin):
            
            email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
            date_of_birth = models.DateField(null=False, blank=False)
            first_name = models.CharField(max_length=30, null=False, blank=False)
            last_name = models.CharField(max_length=30, null=False, blank=False)
            is_admin = models.BooleanField(default=False)
            is_active = models.BooleanField(default=True)
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)

            USERNAME_FIELD = 'email'
            REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth']

            objects = UserManager()

            def __str__(self):
                return self.last_name + ', ' + self.first_name
        ```

4. 필수 입력 필드를 변경했으므로 Custom Register Serializer 설정
    ```python
    # ./accounts/serializers.py
    from dj_rest_auth.registration.serializers import RegisterSerializer
    from rest_framework import serializers

    class CustomRegisterSerializer(RegisterSerializer):
        username = None

        date_of_birth = serializers.DateField()
        first_name = serializers.CharField(required=True)
        last_name = serializers.CharField(required=True)

        def save(self, request):
            user = super().save(request)
            user.date_of_birth = self.data.get('date_of_birth')
            user.first_name = self.data.get('first_name')
            user.last_name = self.data.get('last_name')
            user.save()
            return user
    ```

    ```python
    # ./accounts/views.py

    from dj_rest_auth.registration.views import RegisterView
    from .serializers import CustomRegisterSerializer

    # Create your views here.
    class CustomRegisterAPIView(RegisterView):
        serializer_class = CustomRegisterSerializer
    ```

5. Adapter 설정
    - django-allauth는 기본적으로 사용자 정의 필드를 저장하지 않음
    - 따라서 클래스의 인터페이스를 사용자 정의 인터페이스로 변환하는 패턴인 어댑터 패턴이 필요
    - 어댑터를 사용하면 호환되지 않는 클래스를 연결할 수 있음
    - 사용자 정의 필드를 저장하기 위해 커스텀 어댑터를 별도로 정의해야 함
        ```python
        # ./accounts/adapter.py

        from allauth.account.adapter import DefaultAccountAdapter
        from allauth.account.utils import user_field


        class CustomUserAccountAdapter(DefaultAccountAdapter):

            def clean_username(self, username, shallow=False):
                # username을 사용하지 않으므로 무시
                return None

            def generate_unique_username(self, txts, regex=None):
                # username을 사용하지 않으므로 무시
                return None

            def save_user(self, request, user, form, commit=True):
                """
                Saves a new `User` instance using information provided in the
                signup form.
                """

                user = super().save_user(request, user, form, commit=False)
                user_field(user, 'email', request.data.get('email'))
                user_field(user, 'first_name', request.data.get('first_name'))
                user_field(user, 'last_name', request.data.get('last_name'))
                user_field(user, 'date_of_birth', request.data.get('date_of_birth'))

                user.save()
                
                return user
        ```
    - ./config/settings.py 설정
        ```python
        # ./config/settings.py

        ACCOUNT_ADAPTER = 'accounts.adapter.CustomUserAccountAdapter'
        ```

6. Admin 설정
    ```python
    # ./accounts/admin.py

    from django.contrib import admin
    from .models import User

    admin.site.register(User)
    ```

### 8. articles 앱

1. 라이브러리 설치
    ```bash
    pip3 install elasticsearch numpy
    ```

2. 기존 DB 테이블을 모델로 변환

    ```bash
    python3 manage.py inspectdb news_articles > articles/models.py
    ```

3. Elasticsearch 관련 설정

    ```python
    # ./config/settings.py

    ES_CONFIG = {
        "host": "localhost",
        "port": 9200,
        "index": "news_articles",
        "user": "elastic",
        "password": "elastic123",
        "use_ssl": False
    }
    ```

4. 유저-기사 간 상호작용(좋아요/조회수/스크랩) 모델 생성

5. 상호작용별 가중치 생성

### 9. chatbot 앱

1. 라이브러리 설치
    ```bash
    pip3 install langchain_community
    ```

2. 챗봇 세션 관련 모델 추가

    ```python
    # ./chatbot/models.py
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
    ```

### 10. Migrations 수행

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 11. 더미 데이터 생성

```bash
python3 manage.py generate_dummy_articles
```

### 12. 서버 실행

```bash
python3 manage.py runserver
```


### 11. 모델 설정

## Reference

- [\[DRF\] dj-rest-auth를 활용한 (아주 간편한) JWT 회원가입/로그인
](https://velog.io/@kjyeon1101/DRF-dj-rest-auth%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%EC%95%84%EC%A3%BC-%EA%B0%84%ED%8E%B8%ED%95%9C-JWT-%ED%9A%8C%EC%9B%90%EA%B0%80%EC%9E%85%EB%A1%9C%EA%B7%B8%EC%9D%B8)

- [\[TIL\] dj_rest_auth Custom 회원가입 만들기 (+ Custom model)
](https://medium.com/@heeee/til-dj-rest-auth-custom-%ED%9A%8C%EC%9B%90%EA%B0%80%EC%9E%85-%EB%A7%8C%EB%93%A4%EA%B8%B0-custom-model-f1ad5a29f170)

- [JWT와 session의 개념 및 차이점 정리](https://velog.io/@jellyjw/JWT%EC%99%80-session)
