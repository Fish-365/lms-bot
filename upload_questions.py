from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# name = 'session'
# chrome_driver_path = r'/home/rus/Documents/project/my_project/lms-bot/chromedriver'  # Замените на фактический путь



class Selen():
    
    def __init__(self, name, chrome_driver_path):
        self.name = name
        self.chrome_driver_path = chrome_driver_path
        
        service = ChromeService(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.get("https://lms.yandex.ru/")

        try:
            with open(f"sessions/{name}.json", "r") as f:
                cookies = json.load(f)

            for cookie in cookies:
                if 'domain' not in cookie:
                    cookie['domain'] = '.yandex.ru'
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Ошибка при добавлении cookie: {cookie} - {e}")
        
        except Exception as e:
            self.driver.quit()
            raise Exception(f"Ошибка инициализации Selen: {e}")
        
        self.driver.get("https://lms.yandex.ru/")  # Обновляем страницу, чтобы cookies вступили в силу
        
        

    # -----------ПЕРЕХОД К УРОКУ И НАЖАТИЕ НА КНОПКУ "ОТКРЫТЬ РЕДАКТОР"-------------------
    def upload(self, lesson_url, code, NS=True):

        driver = self.driver

        try:
            driver.get(lesson_url)

            if NS: # Если решение ещё не отправлено
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div/div[2]/div/section/header/a'))
                )
                # Затем ждем, пока элемент станет кликабельным
                element = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div/div[2]/div/section/header/a'))
                )

                element.click()

        # -----------ВСТАВКА КОДА И ОТПРАВКА РЕШЕНИЯ-------------------

            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'cm-content'))
            )
            # Затем ждем, пока элемент станет кликабельным
            element = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'cm-content'))
            )

            element.click()
            # Вместо send_keys используем JavaScript для установки значения
            driver.execute_script("arguments[0].textContent = arguments[1];", element, code)
            # Может потребоваться дополнительное событие, чтобы редактор "увидел" изменения
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)


            element = WebDriverWait(driver, 600).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div[2]/div[2]/div/section/header/button'))
            )

            element.click()

        # -----------ПОЛУЧЕНИЕ РЕЗУЛЬТАТА-------------------

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div[2]/div[1]/div/section/div[1]/header'))
            )

            time.sleep(3)

            # Затем ждем, пока элемент станет кликабельным
            element = WebDriverWait(driver, 190).until(
                EC.visibility_of_any_elements_located((By.XPATH, '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div[2]/div[1]/div/section/div[1]/header'))
            )

            result = driver.find_element("xpath", '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div[2]/div[1]/div/section/div[1]/header/div[2]/section/div/h4/span[2]').text
            
            title_task = driver.find_element("xpath", '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/header/div/h1').text
            print(title_task)

            while (result == 'Ещё не проверено') and not ('Ручная проверка' in title_task):
                driver.refresh()
                time.sleep(4)

                element = WebDriverWait(driver, 40).until(
                    EC.visibility_of_any_elements_located((By.XPATH, '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div[2]/div[1]/div/section/div[1]/header'))
                )

                result = driver.find_element("xpath", '//*[@id="root"]/div[3]/div[1]/div[2]/div/main/div[2]/div[1]/div/section/div[1]/header/div[2]/section/div/h4/span[2]').text

                


            print(f"Результат: {result}")
            return result
            time.sleep(5)
            
            driver.quit()
        except Exception as e:
            print(f"Произошла ошибка: {e}")
