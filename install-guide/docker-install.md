# Docker Desktop 설치

### 0. Docker란?
- Docker는 애플리케이션을 컨테이너(container)라는 독립된 환경에서 실행할 수 있도록 도와주는 플랫폼입니다.
- 컨테이너는 일종의 작은 가상 머신처럼 동작하지만, 훨씬 가볍고 빠릅니다.
- 예를 들어, Python 웹 서버, 데이터베이스, 머신러닝 모델 등을 Docker로 실행하면
    - 다른 컴퓨터에서도 동일환 환경으로 실행 가능
    - 설치/설정 충돌 없이 독립적으로 운영 가능
- 개발, 테스트, 배포 자동화에 널리 사용됩니다.

### 1. Docker 데스크톱 설치
- [공식 다운로드 링크](https://www.docker.com/)
- 설치 완료 후 Docker 실행

### 2. Docker 정상 연동 확인

```bash
docker --version
docker run hello-world
```

### 3. Docker 기본 명령어 요약

```bash
docker ps # 실행 중인 컨테이너
docker ps -a # 모든 컨테이너
docker images # 이미지 목록
docker rm [ID] # ID가 [ID]인 컨테이너 삭제
docker rmi [ID] # ID가 [ID]인 이미지 삭제
```
