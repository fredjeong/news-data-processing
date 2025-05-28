# AI 기반 맞춤형 뉴스 플랫폼 API 명세서

## 목차
1. [소개](#소개)
2. [API 기본 정보](#api-기본-정보)
   - [기본 URL](#기본-url)
   - [인증 방식](#인증-방식)
   - [응답 형식](#응답-형식)
   - [오류 코드](#오류-코드)
3. [기사 API](#기사-api)
   - [기사 목록 조회](#기사-목록-조회)
   - [기사 조회](#기사-조회)
   - [연관 기사 조회](#연관-기사-조회)
   - [추천 기사](#추천-기사)
   - [기사 검색](#기사-검색)
4. [계정 관리 API](#계정-관리-api)
   - [회원가입](#회원가입)
   - [로그인](#로그인)
   - [로그아웃](#로그아웃)
5. [개인 계정 API](#개인-계정-api)
   - [유저 정보 조회](#유저-정보-조회)
   - [프로필 수정](#프로필-수정)
   - [비밀번호 변경](#비밀번호-변경)
6. [조회/좋아요/스크랩 API](#조회좋아요스크랩-api)
   - [기사 조회 기록](#기사-조회-기록)
   - [기사 좋아요](#기사-좋아요)
   - [기사 스크랩](#기사-스크랩)
7. [챗봇 API](#챗봇-api)
   - [응답 생성](#응답-생성)
   - [대화 기록 조회](#대화-기록-조회)

## 소개

AI 기반 맞춤형 뉴스 플랫폼은 인공지능을 활용하여 언어이해와 분석 기술을 통해 사용자에게 최적화된 뉴스 콘텐츠를 제공하는 서비스입니다. 본 플랫폼은 최신 빅데이터 기술과 인공지능을 활용하여 맞춤형 뉴스 콘텐츠를 효율적으로 처리하고, 사용자 개개인에게 맞춤화된 뉴스 경험을 제공합니다.

이 API 명세서는 개발자가 AI 기반 맞춤형 뉴스 플랫폼과 상호작용하는 데 필요한 모든 엔드포인트와 기능을 상세히 설명합니다.

## API 기본 정보

### 기본 URL

모든 API 요청의 기본 URL은 다음과 같습니다:

```
http://127.0.0.1:8000
```

프로덕션 환경에서는 다음 URL을 사용합니다:

```
https://api.news-ai-platform.com
```

### 인증 방식

대부분의 API 엔드포인트는 인증이 필요합니다. 인증은 JWT(JSON Web Token) 기반으로 이루어지며, 토큰은 로그인 API를 통해 발급받을 수 있습니다.

인증이 필요한 API 요청 시 다음과 같이 Authorization 헤더에 Bearer 토큰을 포함해야 합니다:

```
Authorization: Bearer {vault:json-web-token}
```

토큰의 유효 기간은 발급 후 24시간이며, 만료 시 재로그인이 필요합니다.

### 응답 형식

모든 API 응답은 JSON 형식으로 제공됩니다. 기본 응답 구조는 다음과 같습니다:

**성공 응답:**
```json
{
  "message": "요청이 성공적으로 처리되었습니다.",
  "data": { ... }
}
```

**오류 응답:**
```json
{
  "message": "오류가 발생했습니다.",
  "detail": { ... },
  "error_code": "ERROR_CODE"
}
```

### 오류 코드

| 상태 코드 | 오류 코드 | 설명 |
|---------|----------|------|
| 400 | BAD_REQUEST | 잘못된 요청 형식 또는 유효하지 않은 파라미터 |
| 401 | UNAUTHORIZED | 인증 실패 또는 유효하지 않은 토큰 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 요청한 리소스를 찾을 수 없음 |
| 409 | CONFLICT | 리소스 충돌 (예: 이미 존재하는 이메일) |
| 500 | INTERNAL_SERVER_ERROR | 서버 내부 오류 |

## 기사 API

### 기사 목록 조회

**엔드포인트:** `GET /articles/`

**설명:** 아티클(뉴스 기사) 목록을 조회합니다.

**인증 요구사항:** 불필요

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| page | integer | 아니오 | 페이지 번호 (기본값: 1) |
| per_page | integer | 아니오 | 페이지당 기사 수 (기본값: 20, 최대: 100) |
| category | string | 아니오 | 카테고리별 필터링 (예: 정치, 경제, 사회, 문화, 스포츠) |
| sort_by | string | 아니오 | 정렬 기준 (options: date, popularity, relevance) |

**응답:**

```json
[
  {
    "id": 1,
    "title": "테스트 뉴스 기사 1"
  },
  {
    "id": 2,
    "title": "테스트 뉴스 기사 2"
  },
  {
    "id": 3,
    "title": "테스트 뉴스 기사 3"
  },
  ...
]
```

**응답 코드:**
- 200 OK: 성공적으로 기사 목록 반환
- 400 Bad Request: 잘못된 요청 파라미터

### 기사 조회

**엔드포인트:** `GET /articles/{id}/`

**설명:** 기사의 고유 ID를 이용해 특정 기사의 세부 내용을 조회합니다.

**인증 요구사항:** 불필요 (인증 시 사용자 맞춤 정보 제공)

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| id | integer | 예 | 기사의 고유 ID |

**응답:**

```json
{
  "id": 1,
  "title": "테스트 뉴스 기사 1",
  "writer": "기자1",
  "write_date": "2025-05-11T09:19:13.618997Z",
  "category": "정치",
  "content": "이것은 테스트 뉴스 기사 본문입니다. 본문: 1",
  "summary": "테스트 뉴스 기사 1의 요약입니다.",
  "url": "https://news.example.com/article/1",
  "keywords": ["언론", "정치", "국회", "토론"],
  "read_count": 120,
  "like_count": 45,
  "scrap_count": 15
}
```

**응답 코드:**
- 200 OK: 성공적으로 기사 정보 반환
- 404 Not Found: 해당 ID의 기사가 존재하지 않음

### 연관 기사 조회

**엔드포인트:** `GET /articles/{id}/related`

**설명:** 고차원 유사도를 기반으로 특정 기사와 가장 관련성이 높은 기사 5개를 조회합니다.

**인증 요구사항:** 불필요

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| id | integer | 예 | 기준 기사의 고유 ID |
| limit | integer | 아니오 | 반환할 연관 기사 수 (기본값: 5, 최대: 20) |

**응답:**

```json
[
  {
    "id": 40,
    "title": "테스트 뉴스 기사 40"
  },
  {
    "id": 3,
    "title": "테스트 뉴스 기사 3"
  },
  ...
]
```

**응답 코드:**
- 200 OK: 성공적으로 연관 기사 목록 반환
- 404 Not Found: 해당 ID의 기사가 존재하지 않음

### 추천 기사

**엔드포인트:** `GET /accounts/{id}/recommended`

**설명:** 사용자의 이용 기록을 바탕으로 사용자가 관심을 가질만한 기사 5개를 조회합니다. 조회/좋아요/스크랩 별 가중치를 다르게 부여하여 시간에 따라 업데이트되는 사용자의 선호도를 반영합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| id | integer | 예 | 사용자의 고유 ID |
| limit | integer | 아니오 | 반환할 추천 기사 수 (기본값: 5, 최대: 50) |

**응답:**

```json
[
  {
    "id": 8,
    "title": "테스트 뉴스 기사 8"
  },
  {
    "id": 35,
    "title": "테스트 뉴스 기사 35"
  },
  ...
]
```

**응답 코드:**
- 200 OK: 성공적으로 추천 기사 목록 반환
- 401 Unauthorized: 인증 실패
- 403 Forbidden: 다른 사용자의 추천 기사 접근 시도
- 404 Not Found: 해당 ID의 사용자가 존재하지 않음

### 기사 검색

**엔드포인트:** `GET /articles/api/suggest/`

**설명:** Elasticsearch를 이용하여 검색어와 매칭되는 기사를 조회합니다.

**인증 요구사항:** 불필요

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| q | string | 예 | 검색어 |
| page | integer | 아니오 | 페이지 번호 (기본값: 1) |
| per_page | integer | 아니오 | 페이지당 결과 수 (기본값: 10, 최대: 50) |
| sort_by | string | 아니오 | 정렬 기준 (options: relevance, date) |
| date_from | string | 아니오 | 검색 시작 날짜 (YYYY-MM-DD 형식) |
| date_to | string | 아니오 | 검색 종료 날짜 (YYYY-MM-DD 형식) |
| category | string | 아니오 | 카테고리 필터 |

**응답:**

```json
{
  "suggestions": [
    {
      "text": "[시진] 김도연, 10-10 당선",
      "score": 3.740624
    },
    {
      "text": "[시진] kt, 전진 꺾어 3대2 승",
      "score": 3.329117
    },
    ...
  ],
  "total": 15,
  "page": 1,
  "per_page": 10
}
```

**응답 코드:**
- 200 OK: 성공적으로 검색 결과 반환
- 400 Bad Request: 잘못된 검색 파라미터

## 계정 관리 API

### 회원가입

**엔드포인트:** `POST /accounts/signup/`

**설명:** 계정을 생성합니다. 비밀번호는 8자 이상의 문자열로 제한됩니다.

**인증 요구사항:** 불필요

**요청 본문:**

```json
{
  "email": "example3@example.com",
  "password1": "ssafyssafy",
  "password2": "ssafyssafy",
  "first_name": "First",
  "last_name": "User",
  "date_of_birth": "2025-05-01"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| email | string | 예 | 사용자 이메일 (고유값) |
| password1 | string | 예 | 비밀번호 (8자 이상) |
| password2 | string | 예 | 비밀번호 확인 (password1과 일치해야 함) |
| first_name | string | 예 | 이름 |
| last_name | string | 예 | 성 |
| date_of_birth | string | 예 | 생년월일 (YYYY-MM-DD 형식) |

**응답:**

성공 시:
```json
{
  "message": "회원가입에 성공했습니다.",
  "user_id": 20
}
```

실패 시:
```json
{
  "message": "회원가입에 실패했습니다.",
  "detail": {
    "password1": [
      "This password is too short. It must contain at least 8 characters."
    ]
  }
}
```

**응답 코드:**
- 201 Created: 회원가입 성공
- 400 Bad Request: 유효성 검사 실패 (이메일 중복, 비밀번호 불일치 등)

### 로그인

**엔드포인트:** `POST /accounts/login/`

**설명:** 사용자 인증 및 JWT 토큰 발급

**인증 요구사항:** 불필요

**요청 본문:**

```json
{
  "email": "example@example.com",
  "password": "ssafy"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| email | string | 예 | 사용자 이메일 |
| password | string | 예 | 비밀번호 |

**응답:**

성공 시:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 20,
  "email": "example@example.com"
}
```

실패 시:
```json
{
  "non_field_errors": [
    "Unable to log in with provided credentials."
  ]
}
```

**응답 코드:**
- 200 OK: 로그인 성공
- 400 Bad Request: 유효성 검사 실패
- 401 Unauthorized: 인증 실패

### 로그아웃

**엔드포인트:** `POST /accounts/logout/`

**설명:** 현재 로그인된 사용자의 세션을 종료하고 토큰을 무효화합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 본문:**

```json
{
  "email": "example5@example.com"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| email | string | 예 | 로그아웃할 사용자 이메일 |

**응답:**

```json
{
  "detail": "Successfully logged out."
}
```

**응답 코드:**
- 200 OK: 로그아웃 성공
- 401 Unauthorized: 인증 실패

## 개인 계정 API

### 유저 정보 조회

**엔드포인트:** `GET /accounts/{id}/`

**설명:** 특정 유저의 세부 정보를 조회합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| id | integer | 예 | 사용자의 고유 ID |

**응답:**

```json
{
  "user": {
    "id": 20,
    "email": "example@example.com",
    "first_name": "First",
    "last_name": "User",
    "date_of_birth": "2025-05-01",
    "is_active": true,
    "created_at": "2025-05-11T13:29:18.896501Z",
    "updated_at": "2025-05-11T13:29:18.901743Z",
    "preferences": {
      "categories": ["정치", "경제", "기술"],
      "sources": ["한겨레", "조선일보", "BBC"],
      "notification_enabled": true
    },
    "stats": {
      "articles_read": 45,
      "articles_liked": 12,
      "articles_scraped": 8
    }
  }
}
```

**응답 코드:**
- 200 OK: 성공적으로 사용자 정보 반환
- 401 Unauthorized: 인증 실패
- 403 Forbidden: 다른 사용자의 정보 접근 시도
- 404 Not Found: 해당 ID의 사용자가 존재하지 않음

### 프로필 수정

**엔드포인트:** `PUT /accounts/{id}/profile/`

**설명:** 사용자 프로필 정보를 수정합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| id | integer | 예 | 사용자의 고유 ID |

**요청 본문:**

```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "date_of_birth": "1990-01-01",
  "preferences": {
    "categories": ["스포츠", "연예", "기술"],
    "sources": ["중앙일보", "동아일보"],
    "notification_enabled": false
  }
}
```

**응답:**

```json
{
  "message": "프로필이 성공적으로 업데이트되었습니다.",
  "user": {
    "id": 20,
    "email": "example@example.com",
    "first_name": "Updated",
    "last_name": "Name",
    "date_of_birth": "1990-01-01",
    "preferences": {
      "categories": ["스포츠", "연예", "기술"],
      "sources": ["중앙일보", "동아일보"],
      "notification_enabled": false
    },
    "updated_at": "2025-05-26T05:30:18.901743Z"
  }
}
```

**응답 코드:**
- 200 OK: 프로필 업데이트 성공
- 400 Bad Request: 유효하지 않은 데이터
- 401 Unauthorized: 인증 실패
- 403 Forbidden: 다른 사용자의 프로필 수정 시도
- 404 Not Found: 해당 ID의 사용자가 존재하지 않음

### 비밀번호 변경

**엔드포인트:** `PUT /accounts/{id}/password/`

**설명:** 사용자 비밀번호를 변경합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| id | integer | 예 | 사용자의 고유 ID |

**요청 본문:**

```json
{
  "current_password": "ssafyssafy",
  "new_password1": "newpassword123",
  "new_password2": "newpassword123"
}
```

**응답:**

```json
{
  "message": "비밀번호가 성공적으로 변경되었습니다."
}
```

**응답 코드:**
- 200 OK: 비밀번호 변경 성공
- 400 Bad Request: 유효하지 않은 비밀번호 (불일치, 보안 요구사항 미충족 등)
- 401 Unauthorized: 인증 실패 또는 현재 비밀번호 불일치
- 403 Forbidden: 다른 사용자의 비밀번호 변경 시도

## 조회/좋아요/스크랩 API

### 기사 조회 기록

**엔드포인트:** `POST /accounts/article/view/`

**설명:** 사용자가 기사를 조회했음을 기록합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 본문:**

```json
{
  "url": "https://news.example.com/article/1"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| url | string | 예 | 조회한 기사의 URL |

**응답:**

```json
{
  "message": "기사 조회 기록이 저장되었습니다."
}
```

**응답 코드:**
- 200 OK: 조회 기록 저장 성공
- 400 Bad Request: 유효하지 않은 URL
- 401 Unauthorized: 인증 실패
- 404 Not Found: 해당 URL의 기사가 존재하지 않음

### 기사 좋아요

**엔드포인트:** `POST /accounts/article/like/`

**설명:** 사용자가 기사에 좋아요를 표시합니다. 이미 좋아요한 기사에 다시 요청하면 좋아요가 취소됩니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 본문:**

```json
{
  "url": "https://news.example.com/article/5"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| url | string | 예 | 좋아요할 기사의 URL |

**응답:**

좋아요 성공 시:
```json
{
  "message": "좋아요가 등록되었습니다."
}
```

좋아요 취소 시:
```json
{
  "message": "좋아요가 취소되었습니다."
}
```

**응답 코드:**
- 201 Created: 좋아요 등록 성공
- 200 OK: 좋아요 취소 성공
- 400 Bad Request: 유효하지 않은 URL
- 401 Unauthorized: 인증 실패
- 404 Not Found: 해당 URL의 기사가 존재하지 않음

### 기사 스크랩

**엔드포인트:** `POST /accounts/article/scrap/`

**설명:** 사용자가 기사를 스크랩합니다. 이미 스크랩한 기사에 다시 요청하면 스크랩이 취소됩니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 본문:**

```json
{
  "url": "https://news.example.com/article/5"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| url | string | 예 | 스크랩할 기사의 URL |

**응답:**

스크랩 성공 시:
```json
{
  "message": "스크랩이 등록되었습니다."
}
```

스크랩 취소 시:
```json
{
  "message": "스크랩이 취소되었습니다."
}
```

**응답 코드:**
- 201 Created: 스크랩 등록 성공
- 200 OK: 스크랩 취소 성공
- 400 Bad Request: 유효하지 않은 URL
- 401 Unauthorized: 인증 실패
- 404 Not Found: 해당 URL의 기사가 존재하지 않음

## 챗봇 API

### 응답 생성

**엔드포인트:** `POST /chatbot/chat/`

**설명:** LLM에게 질문에 대한 대답을 요청합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 본문:**

```json
{
  "article_id": 1,
  "question": "너는 누구야?"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| article_id | integer | 예 | 질문 대상 기사의 ID |
| question | string | 예 | 사용자 질문 내용 |

**응답:**

```json
{
  "user_message": {
    "id": 17,
    "sender": "user",
    "message": "너는 누구야?",
    "created_at": "2025-05-23T02:57:39.158738Z"
  },
  "bot_message": {
    "id": 18,
    "sender": "bot",
    "message": "저는 AI 뉴스 플랫폼의 챗봇 어시스턴트입니다. 뉴스 기사에 대한 질문이나 추가 정보가 필요하시면 언제든지 물어봐주세요.",
    "created_at": "2025-05-23T02:57:40.258738Z"
  }
}
```

**응답 코드:**
- 200 OK: 성공적으로 응답 생성
- 400 Bad Request: 유효하지 않은 요청 (article_id 또는 question 누락)
- 401 Unauthorized: 인증 실패
- 404 Not Found: 해당 ID의 기사가 존재하지 않음

### 대화 기록 조회

**엔드포인트:** `GET /chatbot/history/{article_id}/`

**설명:** 특정 기사에 대한 사용자의 챗봇 대화 기록을 조회합니다.

**인증 요구사항:** 필수 (Bearer 토큰)

**요청 헤더:**
```
Authorization: Bearer {vault:json-web-token}
```

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| article_id | integer | 예 | 기사의 고유 ID |
| limit | integer | 아니오 | 반환할 대화 기록 수 (기본값: 20) |

**응답:**

```json
{
  "article_id": 1,
  "title": "테스트 뉴스 기사 1",
  "messages": [
    {
      "id": 15,
      "sender": "user",
      "message": "이 기사의 주요 내용이 뭐야?",
      "created_at": "2025-05-23T02:50:12.158738Z"
    },
    {
      "id": 16,
      "sender": "bot",
      "message": "이 기사는 테스트 뉴스 기사로, 주요 내용은 정치 관련 토론에 대한 것입니다. 국회에서 진행된 토론회에서 여야 의원들이 정책에 대해 논의한 내용을 다루고 있습니다.",
      "created_at": "2025-05-23T02:50:13.258738Z"
    },
    {
      "id": 17,
      "sender": "user",
      "message": "너는 누구야?",
      "created_at": "2025-05-23T02:57:39.158738Z"
    },
    {
      "id": 18,
      "sender": "bot",
      "message": "저는 AI 뉴스 플랫폼의 챗봇 어시스턴트입니다. 뉴스 기사에 대한 질문이나 추가 정보가 필요하시면 언제든지 물어봐주세요.",
      "created_at": "2025-05-23T02:57:40.258738Z"
    }
  ]
}
```

**응답 코드:**
- 200 OK: 성공적으로 대화 기록 반환
- 401 Unauthorized: 인증 실패
- 403 Forbidden: 다른 사용자의 대화 기록 접근 시도
- 404 Not Found: 해당 ID의 기사가 존재하지 않음