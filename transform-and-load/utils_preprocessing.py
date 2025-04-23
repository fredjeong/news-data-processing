
# (optional) 수신된 JSON 데이터 pydantic 모델(newsarticle)로 매핑하여 구조화

import tiktoken
from langchain_huggingface import HuggingFaceEmbeddings
import ollama

import sys
from os import path

parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(parent_dir)

from config import MODELS_CONFIG


def preprocess_content(content):
    """
    데이터 전처리 - 텍스트 길이 제한  (5000 토큰)
    토큰 수를 제한하여 처리 효율성 확보
    """

    if not content:
        return ""
        
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    
    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)
    
    return content


def transform_extract_keywords(text):
    """
    텍스트 데이터 변환 - 키워드 5개 추출  
    입력 텍스트에서 핵심 키워드를 추출하는 변환 로직
    """
    text = preprocess_content(text)

    response = ollama.chat(model=MODELS_CONFIG['llm_model'], messages = [
        {
            'role': 'system',
            'content': """You are the greatest journalist the world has ever seen. \
                    Your task now is to extract keywords from a news article. \
                    When given text, extract five keywords that represent the content the best. \
                    Make sure you do not give any numbering in the list. \
                    For example, if the top five keywords are apple, banana, kiwi, pineapple, mango, \
                    your output is supposed to be apple, banana, kiwi, pineapple, mango, \
                    not something like 1. apple, 2. banana, 3. kiwi, 4. pineapple, 5. mango. \
                    Double check your answer before you give the output and see if you followed this instruction.
                    """
        },
        {
            'role': 'user',   
            'content': text
        }
    ])
    keywords = response['message']['content']
    return keywords.split(', ')

embeddings = HuggingFaceEmbeddings(
    model_name=MODELS_CONFIG['embedding_model'],
    model_kwargs={"device": "cpu"}
)

def transform_to_embedding(text: str) -> list[float]:
    text = preprocess_content(text)

    embedded_document = embeddings.embed_documents([text])

    return embedded_document[0]


def transform_classify_category(content):
    """
    텍스트 데이터 변환 - 카테고리 분류  
    뉴스 내용을 기반으로 적절한 카테고리로 분류하는 변환 로직
    """
    # zero-shot classification

    # To classify some new text in a zero-shot manner, 
    # we compare its embedding to all class embeddings and predict the class with the highest similarity.

    # content 전체에 대해 임베딩 시행
    content_embedding = transform_to_embedding(content)

    # 임베딩 벡터와 categories의 각 원소들 사이의 코사인 유사도 비교
    categories = ["IT_과학", "건강", "경제", "교육", "국제", "라이프스타일", "문화", "사건사고", "사회일반", "산업", "스포츠", "여성복지", "여행레저", "연예", "정치", "지역", "취미"]
    category_embeddings = [transform_to_embedding(category) for category in categories]
    
    def get_cosine_sim(A, B):
    
        # Calculate dot product
        dot_product = sum(a*b for a, b in zip(A, B))

        # Calculate the magnitude of each vector
        magnitude_A = sum(a*a for a in A)**0.5
        magnitude_B = sum(b*b for b in B)**0.5

        # Compute cosine similarity
        co_sim = dot_product / (magnitude_A * magnitude_B)
        return co_sim
    
    
    similarity_scores = [get_cosine_sim(content_embedding, category_embedding) for category_embedding in category_embeddings]
    
    output_idx = similarity_scores.index(max(similarity_scores))
    output = categories[output_idx]

    return output