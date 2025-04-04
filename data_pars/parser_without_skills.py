import requests
import csv
import re
from time import sleep
from datetime import datetime

# Словарь технологий и их синонимов
TECH_KEYWORDS = {
    'PYTHON': ['python', 'питон', 'пайтон'],
    'SQL': ['sql', 'postgresql', 'mysql', 'sqlite'],
    'DOCKER': ['docker', 'докер'],
    'GO': ['go', 'golang'],
    'LINUX': ['linux', 'линукс'],
    'GIT': ['git', 'гит'],
    'AWS': ['aws', 'amazon web services'],
    'KUBERNETES': ['kubernetes', 'k8s', 'кубер'],
    'DJANGO': ['django', 'джанго'],
    'FLASK': ['flask', 'фласк'],
    'MATH': [
        'высшая математика', 'математический анализ', 
        'линейная алгебра', 'теория вероятностей',
        'дифференциальные уравнения', 'статистика',
        'дискретная математика', 'численные методы'
    ],
    'DATA_SCIENCE_LIB': [
        'pandas', 'numpy', 'scikit-learn', 'sklearn',
        'matplotlib', 'seaborn', 'tensorflow', 'pytorch',
        'keras', 'statsmodels', 'plotly', 'xgboost'
    ]
}

def extract_tech_skills(text):
    """Извлечение технологий из текста с учетом синонимов"""
    text = text.lower()
    found_skills = set()
    
    for tech, keywords in TECH_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', text, flags=re.IGNORECASE):
                found_skills.add(tech)
                break
    return list(found_skills)

def get_vacancies(params):
    """Получение списка вакансий с обработкой ошибок"""
    try:
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

def get_vacancy_details(vacancy_id):
    """Получение деталей вакансии с задержкой"""
    try:
        url = f'https://api.hh.ru/vacancies/{vacancy_id}'
        response = requests.get(url)
        response.raise_for_status()
        sleep(0.5)  # Соблюдение лимитов API
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения вакансии {vacancy_id}: {e}")
        return None

def process_salary(salary_data):
    """Форматирование данных о зарплате"""
    if not salary_data:
        return None
    
    salary_from = salary_data.get('from')
    salary_to = salary_data.get('to')
    currency = salary_data.get('currency', '')
    
    parts = []
    if salary_from: parts.append(f"от {salary_from}")
    if salary_to: parts.append(f"до {salary_to}")
    if currency: parts.append(currency.upper())
    
    return ' '.join(parts) if parts else None

def main():
    start_time = datetime.now()
    search_query = input('Введите название вакансии: ')
    
    # Параметры запроса
    params = {
        'text': search_query,
        'area': 1,       # Москва
        'page': 0,
        'per_page': 100,  # Максимум на странице
    }

    vacancies_data = []
    
    # Первичный запрос для получения информации о страницах
    first_page = get_vacancies(params)
    if not first_page:
        print("Не удалось получить данные с сервера")
        return

    total_pages = first_page.get('pages', 0)
    print(f"Найдено вакансий: {first_page.get('found', 0)}")
    print(f"Всего страниц для обработки: {total_pages}")

    # Обработка всех страниц
    for page in range(total_pages):
        params['page'] = page
        print(f"Обработка страницы {page+1}/{total_pages}...")
        
        vacancies = get_vacancies(params)
        if not vacancies or 'items' not in vacancies:
            continue
            
        for item in vacancies['items']:
            vacancy = get_vacancy_details(item['id'])
            if not vacancy:
                continue

            # Извлечение данных
            skills = extract_tech_skills(vacancy.get('description', ''))
            
            # Обработка дополнительных полей
            employer = vacancy.get('employer', {})
            salary = process_salary(vacancy.get('salary'))
            experience = vacancy.get('experience', {}).get('name', 'не указан')
            is_remote = 'удален' in vacancy.get('schedule', {}).get('name', '').lower()

            # Сохранение данных
            vacancies_data.append({
                'name': vacancy.get('name', ''),
                'url': vacancy.get('alternate_url', ''),
                'company': employer.get('name', '') if employer else '',
                'salary': salary,
                'experience': experience,
                'remote': is_remote,
                'skills': skills
            })

    # Сохранение в CSV
    if not vacancies_data:
        print("Нет данных для сохранения")
        return

    with open('vacancies_report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Формирование заголовков
        headers = [
            'Должность', 'Ссылка', 'Компания',
            'Зарплата', 'Опыт', 'Удаленная работа'
        ] + list(TECH_KEYWORDS.keys())
        
        writer.writerow(headers)
        
        # Запись данных
        for vac in vacancies_data:
            row = [
                vac['name'],
                vac['url'],
                vac['company'],
                vac['salary'] or 'не указана',
                vac['experience'],
                'Да' if vac['remote'] else 'Нет'
            ]
            row += [1 if tech in vac['skills'] else 0 for tech in TECH_KEYWORDS.keys()]
            writer.writerow(row)

    total_time = datetime.now() - start_time
    print(f"\nОтчет сохранен в vacancies_report.csv")
    print(f"Обработано вакансий: {len(vacancies_data)}")
    print(f"Общее время выполнения: {total_time}")

if __name__ == '__main__':
    main()