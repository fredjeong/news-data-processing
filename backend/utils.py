import numpy as np

def parse_embedding(embedding_str):
    # 예: "[0.1,0.2,0.3,...]" 또는 "0.1,0.2,0.3,..." 형태라면
    if embedding_str.startswith('['):
        embedding_str = embedding_str[1:-1]
    return np.array([float(x) for x in embedding_str.split(',')])

def cosine_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
