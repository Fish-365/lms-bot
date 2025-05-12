from get_session import get_sessions
from upload_questions import Selen
import api_lms
from gen_code import Ai_tools
import time


def main():
    name = 'session'
    chrome_driver_path = r'/home/rus/Documents/project/my_project/lms-bot/chromedriver'
    code = 'print("Hello, World!")'

    # Получаем сессию
    session = get_sessions(name)
    if session is None:
        print("Не удалось получить сессию.")
        return

    # Получаем курсы
    courses = api_lms.get_courses(session=session)

    if courses is None:
        print("Не удалось получить курсы.")
        return
    
    print('Выберете курс:')
    for i, course in enumerate(courses):
        print(f"{i + 1}. {course['name_course']}")
        
    course_index = int(input("Введите номер курса: ")) - 1
    if course_index < 0 or course_index >= len(courses):
        print("Некорректный номер курса.")
        return

    course_id = courses[course_index]['course_id']
    group_id = courses[course_index]['group_id']


    # Получаем уроки
    lesons = api_lms.get_lessons(session=session, course_id=course_id, group_id=group_id)

    if lesons is None:
        print("Не удалось получить уроки.")
        return
    print('Выберете урок:')

    for i, lesson in enumerate(lesons):
        print(f"{i + 1}. {lesson['title']} | {lesson['num_passed']}/{lesson['num_tasks']}")
    lesson_index = int(input("Введите номер урока: ")) - 1

    if lesson_index < 0 or lesson_index >= len(lesons):
        print("Некорректный номер урока.")
        return
    
    lesson_id = lesons[lesson_index]['lesson_id']


    # Получаем задачи
    tasks = api_lms.get_task(session=session, course_id=course_id, group_id=group_id, lesson_id=lesson_id)
    if tasks is None:
        print("Не удалось получить задачи.")
        return
    
    en_ru = {
        "control_work": 'Контрольная работа',
        "individual_work": 'Самостоятельная работа',
        "classwork": 'Классная работа',
        "homework": 'Домашняя работа',
        "additional": 'Дополнительные задачи',
        "other" : 'Прочее'
    }

    verdict_to_smile = {
        "ok": '✅️',
        "accepted": '✅️',
        "unfinished": '☑️',
        "None": '☑️',
        "rework": '❌️',\
        "runtime-error": '❌️',
        "compilation-error": '❌️',
        "wrong-answer": '❌️',
        "review": '📝',
        "auto-review": '📝',
    }
    

    control_work = []
    individual_work = []
    classwork = []
    homework = []
    additional = []
    other = []

    for i in tasks:
        if i['type_work'] == 'control-work':
            control_work.append(i)
        elif i['type_work'] == 'individual-work':
            individual_work.append(i)
        elif i['type_work'] == 'classwork':
            classwork.append(i)
        elif i['type_work'] == 'homework':
            homework.append(i)
        elif i['type_work'] == 'additional':
            additional.append(i)
        else:
            other.append(i)
        works = {
            "control_work": control_work,
            "individual_work": individual_work,
            "classwork": classwork,
            "homework": homework,
            "additional": additional,
            "other": other
        }

    task_id_arr = []    

    for block_name, block_content in works.items():
        if block_content:
            print(en_ru[block_name])
            for i, task in enumerate(block_content):
                print(f"{i + 1}. {verdict_to_smile[task['verdict']]} {task['title']} | {task['get_score']}/{task['score_max']}")
                task_id_arr.append(task['task_id'])


    #  получение описания и solution_id 

    # https://lms.yandex.ru/courses/1177/groups/23553/lessons/6952/tasks/54180/solutions/22358142
    url = 'https://lms.yandex.ru/courses/{}/groups/{}/lessons/{}/tasks/{}/solutions/{}'

    tasks_dict = {}
    
    for i, task in enumerate(task_id_arr):
        data = api_lms.get_description(session=session, group_id=group_id, task_id=task)
        if data is None:
            print("Не удалось получить описание.")
            return

        if data['verdict'] not in ['review', 'accepted', 'ok', 'auto-review']:
            tasks_dict[task] = {
                'course_id': course_id,
                'group_id': group_id,
                'task_id': task,
                'solution_id': data['solution_id'],
                'submissions': data['submissions'],
                'verdict': data['verdict'],
                'lesson_title': data['lesson_title'],
                'title': data['title'],
                'description': data['description'],
                'lesson_url': url.format(course_id, group_id, lesson_id, task, data['solution_id'])
            }

            # if data['verdict'] in ['rework', 'runtime-error']:
            #     console_log = api_lms.get_contest_log(session=session, submissions=data['submissions'])
            #     if console_log is None:
            #         print("Не удалось получить лог.")
            #         return
                
            #     tasks_dict[task]['console_log'] = console_log

# написать функцию для генерации кода, написать условие для NS параметра.
# написать цикл для проверки была ли проверена задача, передать это всё в upload
# запустить этот ёбаный проект в

    lesson_url = 'https://lms.yandex.ru/courses/1177/groups/23553/lessons/6952/tasks/54180/solutions/22358142'

    print(tasks_dict)
    max_attempts = 3  # Максимальное количество попыток для одной задачи
    try:
        selen = Selen(name, chrome_driver_path)
        ai_tools = Ai_tools()


        for id_task in tasks_dict:
            attempt_count = 0 # Счетчик попыток для текущей задачи
            lesson_url = tasks_dict[id_task]['lesson_url']

            lesson_title = tasks_dict[id_task]['lesson_title']
            title = tasks_dict[id_task]['title']
            description = tasks_dict[id_task]['description']
            verdict = tasks_dict[id_task]['verdict']

            # Initialize mode and NS based on verdict
            task_result = None
            mode = 'unfinished'  # default value
            NS = False  # default value

            if verdict in ['rework', 'runtime-error', 'compilation-error', 'wrong-answer']:
                mode = 'rework'
                NS = False

            elif verdict in ['None', 'unfinished', None]:
                mode = 'unfinished'
                if verdict is None:
                    # Если verdict == 'None', то это значит, что задача ещё не проверялась
                    # Поэтому NS = True
                    NS = True
                else:
                    NS = False

                ai_tools.create_prompt(lesson_title=lesson_title, title=title, description=description, mode=mode)
                code = ai_tools.gen_code()

                count = 0
                while code is None and count < 10: 
                    time.sleep(5)
                    code = ai_tools.gen_code()
                    count += 1  # Don't forget to increment count
                
                if count >= 10:
                    print('Ошибка при генерации кода')
                    return 'Error'

                task_result = selen.upload(lesson_url, code, NS=False)
                attempt_count += 1

            # Now task_result is always defined before this check
            if task_result == 'Доработать':
                mode = 'rework'
            
            print(f'Режим: {mode}')
            print(f'verdict: {verdict}')

            while mode == 'rework':
                print(1)
                if attempt_count >= max_attempts:
                    print(f"Превышено максимальное количество попыток ({max_attempts}) для задачи: {title}. Переход к следующей.")
                    break # Выходим из цикла while и переходим к следующей задаче

                submission = tasks_dict[id_task]['submissions']
                solution_id = tasks_dict[id_task]['solution_id']
                course_id = tasks_dict[id_task]['course_id']
                group_id = tasks_dict[id_task]['group_id']


                console_log = api_lms.get_contest_log(session=session, submissions=submission)
                comments = api_lms.get_comments(session=session, solution_id=solution_id, group_id=group_id, course_id=course_id)
                course_code = api_lms.get_source_code(session=session, solution_id=solution_id, course_id=course_id, group_id=group_id)

                ai_tools.create_prompt(lesson_title=lesson_title, title=title, description=description, mode=mode, course_code=course_code, console_log=console_log, comments=comments)
                code = ai_tools.gen_code()

                count = 0
                while code is None and count < 10: 
                    time.sleep(5)
                    print('попытка генерации кода')
                    code = ai_tools.gen_code()

                if count >= 10:
                    print('Ошибка при генерации кода')
                    return 'Error'

                task_result = selen.upload(lesson_url, code, NS=False)
                attempt_count += 1

                if task_result == 'Доработать':
                    mode = 'rework'
                else:
                    mode = 'finish'





    except Exception as e:
        print(f"Ошибка при работе: {e}")
        return

if __name__ == "__main__":
    main()
