import requests
import csv
import re
from time import sleep
from datetime import datetime
from typing import Dict, List, Optional


class VacancyParser:
    """Класс для парсинга вакансий с hh.ru с учетом специализации"""

    # Базовые ключевые слова, общие для всех специальностей
    BASE_KEYWORDS = {
        'GIT': ['git', 'гит'],
        'LINUX': ['linux', 'линукс'],
        'DOCKER': ['docker', 'докер'],
        'AWS': ['aws', 'amazon web services'],
        'KUBERNETES': ['kubernetes', 'k8s', 'кубер']
    }

    # Специфичные ключевые слова для каждой специальности
    SPECIALIZATION_KEYWORDS = {
        'аналитик': {
            'SQL': ['sql', 'postgresql', 'mysql', 'sqlite'],
            'PYTHON': ['python', 'питон', 'пайтон'],
            'BI': ['power bi', 'tableau', 'metabase', 'superset'],
            'EXCEL': ['excel', 'google sheets'],
            'MATH': [
                'статистика', 'теория вероятностей',
                'математический анализ', 'линейная алгебра'
            ],
            'DATA_SCIENCE': [
                'pandas', 'numpy', 'scikit-learn', 'matplotlib',
                'seaborn', 'plotly', 'airflow'
            ]
        },
        'фронтенд': {
            'JAVASCRIPT': ['javascript', 'js', 'ecmascript'],
            'TYPESCRIPT': ['typescript', 'ts'],
            'REACT': ['react', 'react.js'],
            'VUE': ['vue', 'vue.js'],
            'ANGULAR': ['angular'],
            'HTML_CSS': ['html', 'css', 'scss', 'sass'],
            'WEBPACK': ['webpack'],
            'NODEJS': ['node.js', 'nodejs']
        },
        'бэкенд': {
            'PYTHON': ['python', 'питон', 'пайтон'],
            'JAVA': ['java'],
            'C_SHARP': ['c#', 'c sharp'],
            'GO': ['go', 'golang'],
            'NODEJS': ['node.js', 'nodejs'],
            'SPRING': ['spring'],
            'DJANGO': ['django', 'джанго'],
            'FLASK': ['flask', 'фласк'],
            'SQL': ['sql', 'postgresql', 'mysql', 'sqlite'],
            'NOSQL': ['mongodb', 'redis', 'cassandra']
        },
        'кибербезопасность': {
            'SECURITY': ['security', 'безопасность', 'кибербезопасность'],
            'PENTEST': ['pentest', 'тестирование на проникновение'],
            'OWASP': ['owasp'],
            'SIEM': ['siem', 'splunk', 'arcsight'],
            'NETWORK': ['network security', 'сетевая безопасность'],
            'CRYPTO': ['cryptography', 'криптография'],
            'COMPLIANCE': ['gdpr', 'pci dss', 'iso 27001']
        }
    }

    def __init__(self, search_query: str, specialization: str, area: int = 1):
        """
        Инициализация парсера
        :param search_query: Строка поиска (название вакансии)
        :param specialization: Специальность (аналитик, фронтенд, бэкенд, кибербезопасность)
        :param area: ID региона (1 - Москва)
        """
        self.search_query = search_query
        self.specialization = specialization.lower()
        self.area = area
        self.vacancies_data = []
        self.total_pages = 0
        self.total_vacancies = 0
        
        # Проверяем, что указана корректная специализация
        if self.specialization not in self.SPECIALIZATION_KEYWORDS:
            raise ValueError(
                f"Неподдерживаемая специализация. Допустимые значения: {', '.join(self.SPECIALIZATION_KEYWORDS.keys())}"
            )

        # Формируем итоговый словарь ключевых слов для поиска
        self.tech_keywords = {**self.BASE_KEYWORDS, **self.SPECIALIZATION_KEYWORDS[self.specialization]}

    def extract_tech_skills(self, text: str) -> List[str]:
        """Извлечение технологий из текста с учетом синонимов"""
        if not text:
            return []
            
        text = text.lower()
        found_skills = set()
        
        for tech, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text, flags=re.IGNORECASE):
                    found_skills.add(tech)
                    break
        return list(found_skills)

    @staticmethod
    def get_vacancies(params: Dict) -> Optional[Dict]:
        """Получение списка вакансий с обработкой ошибок"""
        try:
            response = requests.get('https://api.hh.ru/vacancies', params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    @staticmethod
    def get_vacancy_details(vacancy_id: str) -> Optional[Dict]:
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

    @staticmethod
    def process_salary(salary_data: Optional[Dict]) -> Optional[str]:
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

    def parse_vacancies(self) -> bool:
        """Основной метод для парсинга вакансий"""
        start_time = datetime.now()
        
        # Параметры запроса
        params = {
            'text': f"{self.search_query} {self.specialization}",
            'area': self.area,
            'page': 0,
            'per_page': 100,
        }

        # Первичный запрос для получения информации о страницах
        first_page = self.get_vacancies(params)
        if not first_page:
            print("Не удалось получить данные с сервера")
            return False

        self.total_pages = first_page.get('pages', 0)
        self.total_vacancies = first_page.get('found', 0)
        print(f"Найдено вакансий: {self.total_vacancies}")
        print(f"Всего страниц для обработки: {self.total_pages}")

        # Обработка всех страниц
        for page in range(min(self.total_pages, 20)):  # Ограничиваем 20 страницами
            params['page'] = page
            print(f"Обработка страницы {page+1}/{self.total_pages}...")
            
            vacancies = self.get_vacancies(params)
            if not vacancies or 'items' not in vacancies:
                continue
                
            for item in vacancies['items']:
                vacancy = self.get_vacancy_details(item['id'])
                if not vacancy:
                    continue

                # Извлечение данных
                skills = self.extract_tech_skills(vacancy.get('description', ''))
                
                # Обработка дополнительных полей
                employer = vacancy.get('employer', {})
                salary = self.process_salary(vacancy.get('salary'))
                experience = vacancy.get('experience', {}).get('name', 'не указан')
                is_remote = 'удален' in vacancy.get('schedule', {}).get('name', '').lower()

                # Сохранение данных
                self.vacancies_data.append({
                    'name': vacancy.get('name', ''),
                    'url': vacancy.get('alternate_url', ''),
                    'company': employer.get('name', '') if employer else '',
                    'salary': salary,
                    'experience': experience,
                    'remote': is_remote,
                    'skills': skills
                })

        total_time = datetime.now() - start_time
        print(f"\nОбработано вакансий: {len(self.vacancies_data)}")
        print(f"Общее время выполнения: {total_time}")
        return True

    def save_to_csv(self, filename: str = None) -> bool:
        """Сохранение данных в CSV-файл"""
        if not self.vacancies_data:
            print("Нет данных для сохранения")
            return False

        if not filename:
            filename = f"{self.specialization}_vacancies.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Формирование заголовков
                headers = [
                    'Должность', 'Ссылка', 'Компания',
                    'Зарплата', 'Опыт', 'Удаленная работа'
                ] + list(self.tech_keywords.keys())
                
                writer.writerow(headers)
                
                # Запись данных
                for vac in self.vacancies_data:
                    row = [
                        vac['name'],
                        vac['url'],
                        vac['company'],
                        vac['salary'] or 'не указана',
                        vac['experience'],
                        'Да' if vac['remote'] else 'Нет'
                    ]
                    row += [1 if tech in vac['skills'] else 0 for tech in self.tech_keywords.keys()]
                    writer.writerow(row)

            print(f"Отчет сохранен в {filename}")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False


if __name__ == '__main__':
    try:
        search_query = input('Введите название вакансии: ')
        specialization = input('Введите специализацию (аналитик/фронтенд/бэкенд/кибербезопасность): ')
        
        parser = VacancyParser(search_query, specialization)
        
        if parser.parse_vacancies():
            parser.save_to_csv()
    except ValueError as e:
        print(e)