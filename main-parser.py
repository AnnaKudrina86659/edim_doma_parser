"""
Основной скрипт парсера рецептов с сайта EdimDoma.ru
"""

import pandas as pd
from tqdm import tqdm
from utils.parser import get_image_links, get_recipes_from_page, clean_dataframe
from utils.gigachat import get_gigachat_token, check_vegetarian
from config import PAGES_TO_PARSE, GIGACHAT_CREDENTIALS

def main():
    """
    Основная функция парсера.
    """
    print("🚀 Запуск парсера рецептов EdimDoma.ru")
    
    # Парсим ссылки на изображения
    print("📸 Парсим ссылки на изображения...")
    image_links = []
    
    for page_num in tqdm(range(1, PAGES_TO_PARSE + 1)):
        current_image_links = get_image_links(page_num)
        image_links.extend(current_image_links)
    
    # Создаем DataFrame и очищаем данные
    df_images = pd.DataFrame(image_links)
    df_images_clean = clean_dataframe(df_images)
    df_images_clean.rename(columns={'title_images': 'new_title_images'}, inplace=True)
    
    # Сохраняем промежуточный результат
    df_images_clean.to_excel('база_данных_ссылок.xlsx', index=False)
    print("✅ Ссылки на изображения сохранены в 'база_данных_ссылок.xlsx'")
    
    # Парсим рецепты
    print("🍳 Парсим рецепты...")
    recipes_data = []
    
    for page_num in tqdm(range(1, min(PAGES_TO_PARSE, 50) + 1)):  # Ограничение для демонстрации
        current_recipes = get_recipes_from_page(page_num)
        recipes_data.extend(current_recipes)
    
    # Создаем DataFrame рецептов
    df_recipes = pd.DataFrame(recipes_data)
    df_recipes.to_csv('база_данных_рецептов.csv', index=False)
    print("✅ Рецепты сохранены в 'база_данных_рецептов.csv'")
    
    # Проверяем вегетарианские рецепты с помощью GigaChat
    print("🌱 Проверяем вегетарианские рецепты...")
    
    # Получаем токен для GigaChat
    giga_token = get_gigachat_token(GIGACHAT_CREDENTIALS['auth_token'])
    
    if giga_token:
        df_recipes['is_vegetarian'] = None
        
        for index, row in tqdm(df_recipes.iterrows(), total=len(df_recipes)):
            vegetarian = check_vegetarian(row['ingredients'], giga_token)
            df_recipes.loc[index, 'is_vegetarian'] = vegetarian
            time.sleep(0.5)  # Задержка между запросами
        
        print("✅ Проверка вегетарианских рецептов завершена")
    else:
        print("⚠️  Не удалось получить токен GigaChat, пропускаем проверку")
    
    # Объединяем данные
    print("🔗 Объединяем данные...")
    merged_df = pd.merge(df_recipes, df_images_clean, 
                        left_on='title', right_on='new_title_images', how='inner')
    
    result_database = merged_df.drop('new_title_images', axis=1)
    
    # Очищаем шаги приготовления
    result_database['steps'] = result_database['steps'].apply(
        lambda x: re.sub(r'\s\s+', ', ', str(x)).rstrip(','))
    
    # Сохраняем финальную базу данных
    result_database.to_excel('база_рецептов.xlsx', index=False)
    print("✅ Финальная база данных сохранена в 'база_рецептов.xlsx'")
    
    # Выводим статистику
    print("\n📊 Статистика парсинга:")
    print(f"Всего рецептов: {len(result_database)}")
    if 'is_vegetarian' in result_database.columns:
        veg_count = result_database['is_vegetarian'].sum()
        print(f"Вегетарианских рецептов: {veg_count}")
    
    print("\n🎉 Парсинг завершен успешно!")

if __name__ == "__main__":
    main()