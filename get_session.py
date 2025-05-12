import requests
import json


def get_sessions(name):
    session = requests.Session()

    try:
        with open(f"sessions/{name}.json", "r") as f:
            cookies = json.load(f)

        # Преобразование cookies из формата Selenium в формат requests
        requests_cookies = {}
        for cookie in cookies:
            requests_cookies[cookie['name']] = cookie['value']

        # Добавление cookies в сессию
        session.cookies.update(requests_cookies)

        response = session.get(
            "https://id.yandex.ru/",
            params={'onlyActiveCourses': True, 'withCoursesSummary': True, 'withExpelled': True},
        )

        return session

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None