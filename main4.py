import os

import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary(min_salary, max_salary):
    if not(min_salary):
        return max_salary * 0.8
    if not(max_salary):
        return min_salary * 1.2
    return (max_salary + min_salary) / 2


def print_table(title, table_data_stats):
    table_data = [
        (
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        )
    ]
    table_data.extend(table_data_stats)
    table = AsciiTable(table_data)
    table.title = title
    print(table.table)


def hh_salary_statistics(vacancies):
    vacancies_items = vacancies['items']
    page_sum_language_salary = 0
    page_vacancies_processed = 0
    page_language_vacancies = 0
    for vacancy in vacancies_items:
        page_language_vacancies += 1
        salary = vacancy['salary']
        if not(salary) or salary['currency'] != 'RUR':
            continue
        min_salary = salary['from']
        max_salary = salary['to']
        vacancy_salary = predict_rub_salary(min_salary, max_salary)
        page_sum_language_salary += vacancy_salary
        page_vacancies_processed += 1
    return page_language_vacancies,
    page_sum_language_salary,
    page_vacancies_processed


def sj_salary_statistics(vacancies):
    page_sum_language_salary = 0
    page_vacancies_processed = 0
    page_language_vacancies = 0
    for vacancy in vacancies['objects']:
        page_language_vacancies += 1
        min_salary = vacancy['payment_from']
        max_salary = vacancy['payment_to']
        if (min_salary == 0 and max_salary == 0) \
                or (vacancy['currency'] != 'rub'):
                    continue
        vacancy_salary = predict_rub_salary(min_salary, max_salary)
        page_sum_language_salary += vacancy_salary
        page_vacancies_processed += 1
    return page_language_vacancies,
    page_sum_language_salary,
    page_vacancies_processed


def main():
    load_dotenv()
    superjob_api_key = os.environ['SUPERJOB_API_KEY']
    programming_languages = (
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Shell'
    )
    job_sites = {
        'headhunter': {
            'table_name': 'HeadHunter Moscow',
            'api_link': 'https://api.hh.ru/vacancies',
            'params': {
                'area': 1,
                'only_with_salary': True,
                'period': 30,
                'per_page': 100
            },
            'headers': {}
        },
        'superjob': {
            'table_name': 'Superjob Moscow',
            'api_link': 'https://api.superjob.ru/2.0/vacancies/',
            'params': {
                'town': 'Москва',
            },
            'headers':  {
                'X-Api-App-Id': superjob_api_key,
            }
        }
    }
    for job_site in job_sites:
        table_data = []
        table_name = job_sites[job_site]['table_name']
        for language in programming_languages:
            total_pages = 20
            language_stats = []
            api_link = job_sites[job_site]['api_link']
            total_language_vacancies = 0
            vacancies_processed = 0
            sum_language_salary = 0
            for page in range(total_pages):
                if job_site == 'headhunter':
                    job_sites[job_site]['params']['text'] =\
                         f'Программист {language}'
                else:
                    job_sites[job_site]['params']['keyword'] =\
                         f'Программист {language}'
                job_sites[job_site]['params']['page'] = page
                params = job_sites[job_site]['params']
                headers = job_sites[job_site]['headers']
                response = requests.get(
                                    api_link,
                                    params=params,
                                    headers=headers
                                    )
                response.raise_for_status
                vacancies = response.json()
                if job_site == 'headhunter':
                    page_language_vacancies,
                    page_language_salary,
                    page_vacancies_processed = hh_salary_statistics(vacancies)
                else:
                    page_language_vacancies,
                    page_language_salary,
                    page_vacancies_processed = sj_salary_statistics(vacancies)
                total_language_vacancies += page_language_vacancies
                sum_language_salary += page_language_salary
                vacancies_processed += page_vacancies_processed
            average_salary = int(sum_language_salary/vacancies_processed)
            language_stats.extend(
                [
                    language,
                    total_language_vacancies,
                    vacancies_processed,
                    average_salary
                ]
                )
            table_data.append(language_stats)
        print_table(table_name, table_data)


if __name__ == '__main__':
    main()
