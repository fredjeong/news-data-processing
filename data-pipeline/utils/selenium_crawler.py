from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_content_from_link(url: str) -> str:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.TAG_NAME, 'p'))
        )
        contents = driver.find_elements(By.TAG_NAME, 'p')
        return ''.join(c.text.strip() for c in contents if c.text.strip())
    
    except Exception as e:
        print(f'[Error] 본문 수집 실패: {e}')
        return ''
    
    finally:
        driver.quit()
