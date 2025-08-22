import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from tqdm import tqdm

def get_image_links(page_number):
    """
    Парсит ссылки на изображения и их названия с заданной страницы.
    
    Args:
        page_number (int): Номер страницы для парсинга
        
    Returns:
        list: Список словарей с названиями и ссылками на изображения
    """
    url = f"https://www.edimdoma.ru/retsepty?page={page_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data_links = []
    image_description = soup.find_all("picture", {"class": "card__picture"})
    
    links = []
    titles = []
    
    for item in image_description:
        # Извлекаем ссылку на изображение
        link_item = str(item.find('img'))
        link_result = re.findall('https?://[^"\']+', link_item)
        clean_link = str(link_result).replace('[', '').replace(']', '')
        links.append(clean_link)
        
        # Извлекаем название изображения
        title_result = str(item.find('img'))
        title_resulting = str(re.findall('alt="[^"\']+', title_result))
        title_resulting = title_resulting.replace("['alt=", '').replace("']", '').replace('"', "")
        titles.append(title_resulting)
    
    # Объединяем названия и ссылки
    for title, link in zip(titles, links):
        data_links.append({'title_images': title, 'links_images': link})
    
    return data_links

def get_recipes_from_page(page_number):
    """
    Парсит рецепты с заданной страницы.
    
    Args:
        page_number (int): Номер страницы для парсинга
        
    Returns:
        list: Список словарей с информацией о рецептах
    """
    url = f"https://www.edimdoma.ru/retsepty?page={page_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Находим все карточки рецептов
    card_description = soup.find_all("div", {"class": "card__description"})
    links = []
    
    # Извлекаем ссылки на рецепты
    for item in card_description:
        link_item = item.find('a')['href']
        full_url = f"https://www.edimdoma.ru{link_item}"
        links.append(full_url)
    
    data = []
    
    # Парсим каждый рецепт
    for recipe_link in links:
        response = requests.get(recipe_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            # Извлекаем информацию о рецепте
            title = soup.find('h1', {'class': 'recipe-header__name'}).get_text(strip=True)
            time_for_cook = soup.find('div', {'class': 'entry-stats__value'}).get_text(strip=True)
            
            # Извлекаем ингредиенты
            ingredients = [
                meta['content']
                for meta in soup.find_all('meta', {'itemprop': 'recipeIngredient'})
            ]
            
            # Извлекаем шаги приготовления
            steps = [step.get_text(strip=True) for step in soup.find_all('div', {'class': 'plain-text recipe_step_text'})]
            cleaned_steps = [step.replace('\xa0', '') for step in steps]
            
            # Форматируем шаги с нумерацией
            result_steps = []
            for i, step in enumerate(cleaned_steps, 1):
                result_step = f"{i}. {step}"
                result_steps.append(result_step)
            
            data.append({
                'title': title,
                'time_for_cook': time_for_cook,
                'recipe_url': recipe_link,
                'ingredients': ingredients,
                'steps': result_steps
            })
            
        except AttributeError as e:
            print(f"Ошибка при парсинге рецепта {recipe_link}: {e}")
            continue
        
        # Задержка для избежания блокировки
        time.sleep(1)
    
    return data

def clean_dataframe(df):
    """
    Очищает и обрабатывает DataFrame.
    
    Args:
        df (DataFrame): Исходный DataFrame для очистки
        
    Returns:
        DataFrame: Очищенный DataFrame
    """
    # Удаляем пустые строки и дубликаты
    df_clean = df.replace(r'^\s*$', pd.NA, regex=True).dropna()
    df_clean = df_clean.reset_index(drop=True)
    df_clean = df_clean.drop_duplicates()
    
    # Обрабатываем ссылки на изображения
    df_clean['links_images'] = df_clean['links_images'].str.replace('small', 'wide')
    df_clean['links_images'] = df_clean['links_images'].str.replace("'", "")
    
    return df_clean