from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, ChatMessage
from .serializers import ChatMessageSerializer
from articles.models import NewsArticle
from langchain_community.llms import Ollama
from django.shortcuts import get_object_or_404
# import logging
# Create your views here.

from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_api(request):
    article_id = request.data.get('article_id')
    question = request.data.get('question')

    # 기사 전문 가져오기
    try:
        article = get_object_or_404(NewsArticle, id=article_id)
    except NewsArticle.DoesNotExist:
        return Response({'error': 'Article not found.'}, status=404)

    # 세션 생성 또는 가져오기
    session, _ = ChatSession.objects.get_or_create(
        user=request.user, article=article
    )

    # 사용자 메시지 저장
    user_msg = ChatMessage.objects.create(
        session=session, sender='user', message=question
    )

    # Ollama LLM 호출
    llm = Ollama(model="exaone3.5:2.4b")
    
    # 기사 내용과 질문을 명확하게 구조화
    article_content = article.content.strip()
    prompt = (
        "아래 기사를 읽고 질문에 답변해주세요.\n\n"
        "===== 기사 내용 시작 =====\n"
        f"{article_content}\n"
        "===== 기사 내용 끝 =====\n\n"
        f"질문: {question}\n"
        "답변:"
    )
    
    # 최대 토큰 수를 지정하여 응답 생성
    answer = llm(prompt, max_tokens=512)

    # 챗봇 메시지 저장
    bot_msg = ChatMessage.objects.create(
        session=session, sender='bot', message=answer
    )

    # 최신 메시지 반환
    return Response({
        'user_message': ChatMessageSerializer(user_msg).data,
        'bot_message': ChatMessageSerializer(bot_msg).data,
    })
