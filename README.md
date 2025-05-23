# LMS Bot

Этот проект — бот на Python, работающий с Yandex LMS. Он получает данные об уроках, генерирует код и автоматически отправляет его через эмуляцию браузера. Также предусмотрены дополнительные итерации для исправления ошибок.
## Основные файлы проекта

- **`get_cokie.py`**: файл для получения cookie-файлов, необходимых для работы с Yandex LMS. Этот файл взаимодействует с веб-интерфейсом Yandex LMS для получения cookies.
- **`main.py`**: Главный файл для выполнения основной логики бота.
- **`api_key.json`**: Файл с вашим API-ключом. 
- **`requirements.txt`**: Список всех библиотек и зависимостей, необходимых для работы проекта.

## Установка и настройка

Для запуска проекта выполните следующие шаги:

### 1. Создайте виртуальное окружение

Для изоляции зависимостей создайте виртуальное окружение:

```bash
python -m venv venv
```
На Windows:
```bash
.\venv\Scripts\activate
```
На MacOS/Linux:
```bash
source venv/bin/activate
```
### 2. Установите зависимости
После активации виртуального окружения установите необходимые библиотеки:
```bash
pip install -r requirements.txt
```
### 3. Настройка API ключа
Откройте файл **`api_key.json`** и поменяйте надпись "API key OpenRouter.ai" на свой ключ от OpenRouter.

### 4. получение cokie
запустите файл **`get_cokie.py`** и войдите в Yandex LMS удобным вам способом

