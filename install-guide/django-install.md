# Django 설치

### VSCode Extension 설치

- `Django` 설치
- `Database Client` 설치
- `SQLite Viewer` 설치

### Django Extension 환경설정

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

### 가상환경에 Django 및 DRF(Django Rest Framework) 설치

```bash
pip install django djangorestframework
```

### Django 프로젝트 생성 및 실행

1. 프로젝트 생성

```bash
django-admin startproject backend
```

2. `settings.py` 수정

```python
# settings.py
INSTALLED_APPS = [
    "rest_framework",
]
```

3. Migration 수행

```bash
python manage.py makemigrations
python manage.py migrate
```

4. admin 계정 생성

```bash
python manage.py createsuperuser
```

4. 서버 실행

```bash
python manage.py runserver
```

5. 서버 확인

- http://127.0.0.1:8000/ 접속 후 확인
- http://127.0.0.1:8000/admin 접속 후 확인