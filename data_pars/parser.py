import requests
import csv

def get_vacancies(params):
    vac = requests.get('https://api.hh.ru/vacancies', params=params)
    try:
        return vac.json()
    except Exception as e:
        print('Error', vac.status_code)


def get_vacance(id):
    url = f'https://api.hh.ru/vacancies/{id}'
    resp = requests.get(url)
    try:
        return resp.json()
    except Exception as e:
        print('Error', vac.status_code)


text = input('Введите название вакансии: ')
params = {
    'text': text,
    'page': 0,
    'per_page': 100,
    'area': 1,
}

first_page = get_vacancies(params)
pages = first_page.get('pages')

set_skills = {}
pars_vacancies = list()

while params['page'] <= pages:
    cur_vacancies = get_vacancies(params)
    if not cur_vacancies:
        break
    for vac in cur_vacancies.get('items', []):
        cur_vac_by_id = get_vacance(vac.get('id'))
        if not cur_vac_by_id:
            continue
        key_skills = cur_vac_by_id.get('key_skills', [])
        vac_data = {
            'url': cur_vac_by_id.get('alternate_url'),
            'name': cur_vac_by_id.get('name'),
            'area': params['area'],
            'skills': [skill['name'] for skill in key_skills]
        }
        pars_vacancies.append(vac_data)
        for skill in key_skills:
            if skill['name'].upper() in set_skills:
                set_skills[skill['name'].upper()] += 1
            else:
                set_skills[skill['name'].upper()] = 1
    params['page'] += 1

filtered_skills = {skill: count for skill, count in set_skills.items() if count > 1}

table = []
for vacancy in pars_vacancies:
    row = [vacancy['url'], vacancy['name'], vacancy['area']]
    for skill in filtered_skills:
        row.append(1 if skill in vacancy['skills'] else 0)
    table.append(row)
    
headers = ['URL', 'Name', 'Area'] + list(filtered_skills.keys())

with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    writer.writerows(table)

print('Данные записаны в файл')
