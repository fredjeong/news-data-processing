# utils/get_bulk_news.py

import pandas as pd

def get_news_dataframe():
    
    try:
        df = pd.read_csv("./utils/data/ssafy_dataset_news_2024_1st_half.csv", 
                        sep="|",
                        dtype=str) \
            .drop(columns=['category_str']) \
            .dropna(subset=['article']) \
            .sample(n=100, random_state=42) # 테스트용 (실제 사용 시에는 지울 것)
        df['article'] = df['article'].str.replace(r'[\n\t]+', '', regex=True)
        print(f'데이터 로드 완료. 총 {len(df)}건의 데이터가 있습니다.')
        return df
    except Exception as e:
        print(f'데이터 로드 실패: {e}')
        return None


if __name__ == "__main__":
    df = get_news_dataframe()
    
    if df is not None:
        print(df.columns)
        print(df.head())
        print(df['company'].unique())