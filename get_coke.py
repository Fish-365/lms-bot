from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import json
import time


name = 'session'  # Имя файла для сохранения cookies
chrome_driver_path = r'/home/rus/Documents/project/my_project/lms-bot/chromedriver'  # Замените на фактический путь


def main():
    # 1. Открытие страницы и получение cookies
    options = Options()
    # options.add_argument("--headless")  # Запуск в фоновом режиме (без GUI)
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get("https://passport.yandex.ru/auth/list?origin=lyceum&retpath=https%3A%2F%2Flms.yandex.ru%2F")
        
        # Дайте странице время загрузиться и, возможно, выполнить какие-то действия вручную (например, войти в аккаунт)
        input("Войдите в аккаунт Yandex и нажмите Enter, чтобы продолжить...")

        cookies = driver.get_cookies()
        print("Cookies сохранены.")

        # Сохраняем cookies в файл (опционально, для отладки)
        with open(f"sessions/{name}.json", "w+") as f:
            json.dump(cookies, f)

    finally:
        driver.quit()
        print("Первый браузер закрыт.")

    # 4. Открытие страницы с использованием сохраненных cookies
    options = Options()
    # options.add_argument("--headless")  # Запуск в фоновом режиме
    service = ChromeService(executable_path=chrome_driver_path)
    driver2 = webdriver.Chrome(service=service)

    try:
        driver2.get("https://lms.yandex.ru/")

        # Загружаем cookies из файла (если вы их сохранили)
        with open(f"sessions/{name}.json", "r") as f:
            cookies = json.load(f)

        for cookie in cookies:
            # У selenium есть проблема с добавлением домена для некоторых cookies
            # Попробуем добавить домен вручную, если он отсутствует
            if 'domain' not in cookie:
                cookie['domain'] = '.yandex.ru'  # Или другой подходящий домен
            try:
                driver2.add_cookie(cookie)
            except Exception as e:
                print(f"Ошибка при добавлении cookie: {cookie} - {e}")

        driver2.get("https://lms.yandex.ru/")  # Обновляем страницу, чтобы cookies вступили в силу
        input('нажмите enter для закрытия браузера')

        # Проверка авторизации (простой пример - проверка наличия элемента, который появляется только после авторизации)
        try:
            # Этот элемент нужно заменить на что-то, что есть только у авторизованного пользователя
            # Например, аватар пользователя, кнопка выхода и т.д.
            user_info_element = driver2.find_element("xpath", """//*[@id="root"]/div[2]/div[1]/header/div[1]/div[2]/nav/div[3]/div/button/div/div""")
            print("Авторизация прошла успешно")
        except:
            print("Авторизация не удалась (элемент не найден).")

    finally:
        driver2.quit()
        print("Второй браузер закрыт.")


if __name__ == "__main__":
    main()