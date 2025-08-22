import requests
import uuid
import json
import time

def get_gigachat_token(auth_token, scope='GIGACHAT_API_PERS'):
    """
    Получает токен доступа для GigaChat API.
    
    Args:
        auth_token (str): Базовый токен авторизации
        scope (str): Область действия токена
        
    Returns:
        str: Токен доступа или None в случае ошибки
    """
    rq_uid = str(uuid.uuid4())
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {auth_token}'
    }
    
    payload = {'scope': scope}
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Ошибка получения токена: {str(e)}")
        return None

def check_vegetarian(ingredients, giga_token):
    """
    Проверяет, является ли блюдо вегетарианским по списку ингредиентов.
    
    Args:
        ingredients (list): Список ингредиентов
        giga_token (str): Токен доступа GigaChat
        
    Returns:
        bool: True если вегетарианское, False если нет, None при ошибке
    """
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {giga_token}'
    }
    
    # Подготавливаем текст ингредиентов
    if isinstance(ingredients, list):
        ingredients_text = ', '.join(ingredients)
    else:
        ingredients_text = ingredients.replace('[', '').replace(']', '').replace("'", '')
    
    payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": f"Определи по списку ингредиентов, является ли блюдо вегетарианским. Ответь только True или False. Ингредиенты: {ingredients_text}"
            }
        ],
        "temperature": 0.7,
        "top_p": 0.9,
        "n": 1,
        "stream": False,
        "max_tokens": 10,
        "update_interval": 0
    })
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip() == 'True'
    except Exception as e:
        print(f"Ошибка при обработке ингредиентов: {ingredients_text[:50]}... | Ошибка: {str(e)}")
        return None