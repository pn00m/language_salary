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


def hh_salary_statistics(programming_languages):
    language_stats = {}
    hh_api_link = 'https://api.hh.ru/vacancies'
    for language in programming_languages:
        sum_language_salary = 0
        vacancies_processed = 0
        total_language_vacancies = 0
        total_pages = 20
        for page in range(total_pages):
            params = {
                'text': f'Программист {language}',
                'area': 1,
                'only_with_salary': True,
                'period': 30,
                'page': page,
                'per_page': 100
            }
            response = requests.get(
                                hh_api_link,
                                params=params
                                )
            vacancies = response.json()
            for vacancy in vacancies['items']:
                total_language_vacancies += 1
                salary = vacancy['salary']
                if not(salary) or salary['currency'] != 'RUR':
                    continue
                min_salary = salary['from']
                max_salary = salary['to']
                vacancy_salary = predict_rub_salary(min_salary, max_salary)
                sum_language_salary += vacancy_salary
                vacancies_processed += 1
        average_salary = int(sum_language_salary/vacancies_processed)
        language_stats[language] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
            }
    print_table('HeadHunter Moscow', language_stats)


def superjob_salary_statistics(programming_languages):
    superjob_api_key = os.environ['SUPERJOB_API_KEY']
    language_stats = {}
    for language in programming_languages:
        sum_language_salary = 0
        vacancies_processed = 0
        total_language_vacancies = 0
        for page in range(10):
            headers_superjob = {
                'X-Api-App-Id': superjob_api_key,
                }
            params_superjob = {
                'keyword': f'Программист {language}',
                'town': 'Москва',
                'page': page
                }
            response = requests.get(
                            'https://api.superjob.ru/2.0/vacancies/',
                            params=params_superjob,
                            headers=headers_superjob
                            )
            vacancies = response.json()
            for vacancy in vacancies['objects']:
                total_language_vacancies += 1
                min_salary = vacancy['payment_from']
                max_salary = vacancy['payment_to']
                if (min_salary == 0 and max_salary == 0) \
                    	or (vacancy['currency'] != 'rub'):
                        	continue
                vacancy_salary =\
                    predict_rub_salary(min_salary, max_salary)
                sum_language_salary += vacancy_salary
                vacancies_processed += 1
        average_salary =\
            int(sum_language_salary/vacancies_processed)
        language_stats[language] = {
            'vacancies_found': total_language_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
            }
    print_table('Superjob Moscow', language_stats)


def print_table(title, language_stats):
    table_data = [
        (
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        )
    ]
    for language in language_stats:
        table_data.append(
            [
                language,
                language_stats[language]['vacancies_found'],
                language_stats[language]['vacancies_processed'],
                language_stats[language]['average_salary']
            ]
        )
    table = AsciiTable(table_data)
    table.title = title
    print(table.table)


def main():
    load_dotenv()
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
    hh_salary_statistics(programming_languages)
    superjob_salary_statistics(programming_languages)


if __name__ == '__main__':
    main()
