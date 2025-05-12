from bs4 import BeautifulSoup
import requests
import json

def get_courses(session: requests.Session) -> list:
    """
    Получает список курсов с главной страницы LMS.

    Args:
        session: Сессия requests для выполнения запросов.

    Returns:
        list: Список словарей, каждый из которых содержит информацию о курсе:
              'course_id', 'group_id', 'name_course'.
              Возвращает пустой список в случае ошибки или отсутствия курсов.
    """
    try:
        response = session.get('https://lms.yandex.ru/')
        response.raise_for_status()  # Проверка на HTTP ошибки
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к LMS: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    if not soup.find('a', class_='logo__link logo__link_type_service'):
        print('Ошибка при запросе')
        return None

    else:
        block_with_course = soup.find('ul', class_="courses__list")
        if not block_with_course:
            return []  # Если блок с курсами не найден, возвращаем пустой список
        courses = block_with_course.find_all('li', class_="courses__list-item")

        course_arr = []

        for course in courses:
            link_course = course.find('a', class_='course-card course-card_type_link course-card_enrolled')
            if link_course: # Проверка, что элемент найден перед доступом к 'href'
                link_course = link_course.get('href')
            else:
                continue # Пропускаем курс, если ссылка не найдена

            name_course_element = course.find('div', class_="course-card-header__title")
            if name_course_element: # Проверка, что элемент найден перед доступом к 'title'
                name_course = name_course_element.get('title')
            else:
                name_course = "Название курса не найдено" # Или другое значение по умолчанию

            if link_course:
                info_with_course = link_course.split('/')
                if len(info_with_course) >= 5: # Проверка, что список содержит достаточно элементов
                    course_id = info_with_course[2]
                    group_id = info_with_course[4]

                    course_arr.append({
                        'course_id': course_id,
                        'group_id': group_id,
                        'name_course': name_course
                    })
        return course_arr


def get_lessons(session: requests.Session, course_id: str, group_id: str) -> list:
    """
    Получает список уроков для заданного курса и группы.

    Args:
        session: Сессия requests для выполнения запросов.
        course_id: ID курса.
        group_id: ID группы.

    Returns:
        list: Список словарей, каждый из которых содержит информацию об уроке:
              'lesson_id', 'title', 'num_tasks', 'num_passed'.
              Возвращает пустой список в случае ошибки или отсутствия уроков.
    """
    url = f'https://lms.yandex.ru/api/student/lessons?courseId={course_id}&groupId={group_id}'
    try:
        response = session.get(url)
        response.raise_for_status()
        lessons_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе уроков: {e}")
        return None

    lessons_arr = []
    for lesson in lessons_data:
        if lesson.get('msBeforeDeadline', 0) > 0: # Безопасный доступ к ключу и значение по умолчанию
            lesson_set = {
                'lesson_id': lesson.get('id'),
                'title': lesson.get('title'),
                'num_tasks': lesson.get('numTasks'),
                'num_passed': lesson.get('numPassed')
            }
            lessons_arr.append(lesson_set)

    return lessons_arr


def get_task(session: requests.Session, course_id: str, group_id: str, lesson_id: str) -> list:
    """
    Получает список задач для заданного урока.

    Args:
        session: Сессия requests для выполнения запросов.
        course_id: ID курса.
        group_id: ID группы.
        lesson_id: ID урока.

    Returns:
        list: Список словарей, каждый из которых содержит информацию о задаче:
              'task_id', 'title', 'type_work', 'score_max', 'verdict', 'get_score'.
              Возвращает пустой список в случае ошибки или отсутствия задач.
    """
    url = f'https://lms.yandex.ru/api/student/lessonTasks?courseId={course_id}&groupId={group_id}&lessonId={lesson_id}'
    try:
        response = session.get(url)
        response.raise_for_status()
        tasks_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе задач: {e}")
        return None

    tasks_arr = []
    for type_ in tasks_response:
        for task in type_.get('tasks', []): # Безопасный доступ к ключу и значение по умолчанию
            task_set = {}
            task_set['task_id'] = task.get('id')
            task_set['title'] = task.get('title')
            task_set['type_work'] = task.get('tag', {}).get('type') # Безопасный доступ к вложенным ключам
            task_set['score_max'] = task.get('scoreMax')

            solution = task.get('solution')
            if solution and solution.get('status', {}).get('type') != 'new': # Безопасная проверка вложенных ключей
                task_set['verdict'] = solution['status']['type']
                task_set['get_score'] = solution.get('score', 0) # Значение по умолчанию, если score отсутствует
            else:
                task_set['verdict'] = 'unfinished'
                task_set['get_score'] = 0

            tasks_arr.append(task_set)

    return tasks_arr


def get_description(session: requests.Session, group_id: str, task_id: str) -> dict:
    """
    Получает подробное описание задачи.

    Args:
        session: Сессия requests для выполнения запросов.
        group_id: ID группы.
        task_id: ID задачи.

    Returns:
        dict: Словарь, содержащий описание задачи:
              'solution_id', 'submissions', 'verdict', 'lesson_title', 'title', 'description'.
              Возвращает пустой словарь в случае ошибки или отсутствия описания.
    """
    url = f'https://lms.yandex.ru/api/student/tasks/{task_id}?groupId={group_id}'
    try:
        response = session.get(url)
        response.raise_for_status()
        description_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе описания задачи: {e}")
        return None

    soup = BeautifulSoup(description_response.get('description', ''), 'html.parser') # Безопасный доступ к ключу

    title = description_response.get('title', None)

    text_result = f'{title}\n'

    for class_ in ['time-limit', 'memory-limit', 'input-file', 'output-file']:
        row = soup.find('tr', class_=class_)
        if row: # Проверка, что строка найдена
            title_cell = row.find('td', class_='property-title')
            title_text = title_cell.text.strip() if title_cell else "Не указано" # Безопасный доступ к тексту
            value_cell = row.find_all('td')[1] if len(row.find_all('td')) > 1 else None # Безопасный доступ к ячейке значения
            value_text = value_cell.text.strip() if value_cell else "Не указано" # Безопасный доступ к тексту
            text_result += f'{title_text}: {value_text}\n'

    legend = soup.find('div', class_='legend')
    text_result += f'{legend.text if legend else "Описание отсутствует"}\n' # Безопасный доступ к тексту

    sample_tests = soup.find_all('table', class_='sample-tests')
    for i, sample_test in enumerate(sample_tests):
        pre = sample_test.find_all('pre')
        if len(pre) >= 2: # Проверка, что есть как минимум два <pre> элемента
            text_result += f'ПРИМЕР {i + 1}:\n'
            text_result += f'Ввод:\n{pre[0].text}Вывод:\n{pre[1].text}\n'
    
    note = soup.find('div', class_='notes')

    if not note is None:
        note = note.text
        text_result += f'Примечания:{note}'

    latestSubmission = description_response.get('latestSubmission', None)

    if latestSubmission:
        submissions = latestSubmission.get('id')
        verdict = latestSubmission.get('verdict')
    else:
        submissions = None
        verdict = None


    description_set = {
        'solution_id': description_response.get('solutionId'),
        'submissions': submissions,
        'verdict': verdict,
        'lesson_title': description_response.get('lesson', {}).get('title'),
        'title': title,
        'description': text_result
    }

    return description_set


def get_contest_log(session: requests.Session, submissions: str) -> str or None:
    """
    Получает лог контеста по submission ID.

    Args:
        session: Сессия requests для выполнения запросов.
        submissions: ID submission.

    Returns:
        str or None: Строка с логом контеста в случае ошибки, None если verdict 'ok'.
                     Возвращает None в случае ошибки запроса.
    """
    url = f'https://lms.yandex.ru/api/submissions/{submissions}/contest-logs'
    try:
        response = session.get(url)
        response.raise_for_status()
        log_response = response.json()
    except:
        print(f"Ошибка при запросе лога контеста: {e}")
        return

    verdict = log_response.get('verdict')
    if verdict == 'compilation-error':
        text_result = 'Ошибка компиляции\n'
        text_result += f"Лог компилятора:\n{log_response.get('compileLog', 'Лог компиляции отсутствует')}\n"
        return text_result
    if verdict != 'ok':
        text_result = f"Лог компилятора:\n{log_response.get('compileLog', 'Лог компиляции отсутствует')}\n" # Безопасный доступ к ключу
        text_result += f"Затраченое время: {log_response.get('usedTime', 0)}ms, память: {round(log_response.get('usedMemory', 0) / (10 ** 6), 2)}MB\n\n" # Безопасный доступ к ключу

        test_info = log_response.get('testInfo', {}) # Безопасный доступ к ключу
        input_ = test_info.get('input', '')
        if input_:
            text_result += f'Ввод:\n{input_}\n'

        answer = test_info.get('answer', '')
        if answer:
            text_result += f'Ожидаемый результат:\n{answer}\n'

        output = test_info.get('output', '')
        if output:
            text_result += f'Вывод:\n{output}\n'

        message = test_info.get('message')
        if message:
            text_result += f'Сообщение:\n{message}\n'

        return text_result
    else:
        return None


def get_source_code(session: requests.Session, solution_id: str, course_id: str, group_id: str) -> str or None:
    """
    Получает исходный код решения.

    Args:
        session: Сессия requests для выполнения запросов.
        solution_id: ID решения.
        course_id: ID курса.
        group_id: ID группы.

    Returns:
        str or None: Исходный код решения в виде строки, None в случае ошибки или отсутствия кода.
    """
    url = f'https://lms.yandex.ru/api/student/solutions/{solution_id}?courseId={course_id}&groupId={group_id}'
    try:
        response = session.get(url)
        response.raise_for_status()
        source_code_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе исходного кода: {e}")
        return None

    file_data = source_code_response.get('file', {}) # Безопасный доступ к ключу
    return file_data.get('sourceCode') # Безопасный доступ к ключу


def get_comments(session: requests.Session, solution_id: str, course_id: str, group_id: str) -> list or None:
    """
    Получает комментарии к решению.

    Args:
        session: Сессия requests для выполнения запросов.
        solution_id: ID решения.
        course_id: ID курса.
        group_id: ID группы.

    Returns:
        list or None: Список комментариев в виде строк, None если комментарии отсутствуют или произошла ошибка.
    """
    url = f'https://lms.yandex.ru/api/student/solutions/{solution_id}?courseId={course_id}&groupId={group_id}'
    try:
        response = session.get(url)
        response.raise_for_status()
        comments_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе комментариев: {e}")
        return None

    comments = comments_response.get('comments', []) # Безопасный доступ к ключу

    if not comments:
        return None

    user_username = comments[0]['author']['username'] if comments and comments[0].get('author') else None # Безопасный доступ к вложенным ключам
    black_list_username = [user_username, 'LyceumBot'] if user_username else ['LyceumBot'] # Если username не получен, используем только 'LyceumBot'

    comments_arr = []

    for comment in comments:
        author_username = comment.get('author', {}).get('username') # Безопасный доступ к вложенным ключам
        comment_data = comment.get('data', '') # Безопасный доступ к ключу

        if (author_username not in black_list_username and
            comment_data not in ['accepted', 'rework'] and
            not (comment_data[:-2].isdigit() and comment_data.endswith('.0'))): # Проверка на число с '.0' на конце
            comments_arr.append(comment_data)

    if comments_arr:
        return comments_arr
    else:
        return None
