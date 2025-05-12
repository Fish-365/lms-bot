from openai import OpenAI
import autopep8
import json


with open(r'api_key.json', 'r') as f:
  key = json.load(f)['key']


def extract_last_code_block(gpt_response: str) -> str:
    """Извлекает содержимое последнего блока кода, заключенного в тройные апострофы (```),
    из строки ответа GPT.

    Args:
        gpt_response: Строка, содержащая ответ от GPT.

    Returns:
        Содержимое последнего блока кода без окружающих апострофов и строки
        с указанием языка (если она есть).
        Возвращает пустую строку, если блоки кода не найдены или формат некорректен.
    """
    end_delimiter = '```'
    start_delimiter = '```'

    last_end_index = gpt_response.rfind(end_delimiter)

    if last_end_index == -1:
        return ""

    last_start_index = gpt_response.rfind(start_delimiter, 0, last_end_index)

    if last_start_index == -1:
        return ""

    raw_block_content = gpt_response[last_start_index + len(start_delimiter):last_end_index]

    first_newline_in_block = raw_block_content.find('\n')

    if first_newline_in_block != -1:
        code_content = raw_block_content[first_newline_in_block + 1:]

    else:
        code_content = raw_block_content

    return code_content.strip()

class Ai_tools():
  """Инструменты AI для генерации кода."""

  def __init__(self):
    """Инициализирует инструменты AI, загружает ключ API"""
    with open(r'api_key.json', 'r') as f:
      self.key = json.load(f)['key']

  def create_prompt(self, lesson_title, title, description, mode='unfinished', course_code=None, console_log=None, comments=None):
    """Создает промпт для генерации кода.

    Args:
        lesson_title: Название модуля.
        title: Название урока.
        description: Описание задания.
        mode: Режим работы ('unfinished' или 'rework').
        course_code: Код пользователя (для режима 'rework').
        console_log: Лог консоли (для режима 'rework').
        comments: Комментарии системы (для режима 'rework').
    """
    if mode == 'unfinished':
      self.prompt = f'Ты — профессиональный агент по написанию кода на языке Python на платформе yandex lms.\
          Пиши код, не комментируя его (если не попросят в задании), также не используй библиотеки,\
          без которых можно обойтись стандартными методами или которые не упоминаются в задании или\
          названии модуля. Если просят реализовать классы/функции, но не описывают их, значит,\
          наполнять их не нужно и они служат для проверки архитектуры. Старайся писать код универсальным,\
          так как он проходит несколько проверок (больше, чем указано в задании).\
          Не используй сложные конструкции, такие как: if name == "__main__" (если не просят) и не пиши сложный код.\
          Точно следуй заданию, не придумывая нового. Пиши код, соблюдая стандарты pep8.\
          В ответе я хочу видеть только код в оформлении marcdown ```Python code``` и ничего больше.\n\
          Твоё задание:\n\
          название урока:\n\
          {title}\n\
          название модуля:\n\
          {lesson_title}\n\
          Само задание:\n\
          {description}'
    
    elif mode == 'rework':
      self.prompt = f'Ты — профессиональный агент по написанию и доработке кода на языке Python на платформе yandex lms.\
          Исправь код, написанный пользователем, сохраняя его стиль. При написании нового кода не комментируй его\
          (если не попросят в задании или если пользователь не делал этого), также не используй библиотеки,\
          без которых можно обойтись стандартными методами или которые не упоминаются в задании или названии модуля.\
          Если просят реализовать классы/функции, но не описывают их, значит, наполнять их не нужно и они служат для\
          проверки архитектуры. Старайся писать код универсальным, так как он проходит несколько проверок (больше, чем указано в задании).\
          Не используй сложные конструкции, такие как: if name == "__main__" (если не просят) и не пиши сложный код. Точно следуй заданию,\
          не придумывая нового. Пиши код, соблюдая стандарты pep8. В ответе я хочу видеть только код в оформлении marcdown ```Python code``` и ничего больше.\n\
          Твоё задание:\n\
          Исправь код пользователя:\n\
          {course_code}\n\
          Консоль лог:\n\
          {console_log}\n\
          Комментарий от системы:\n\
          {comments}\n\n\
          Данный код был написан под следующее задание:\n\
          Название урока:\n\
          {title}\n\
          Название блока:\n\
          {lesson_title}\n\
          Само задание:\n\
          {description}'

  def gen_code(self):
    """Генерирует код на основе промпта.

    Returns:
        Сгенерированный код или None, если произошла ошибка.
    """

    client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=self.key,
    )

    completion = client.chat.completions.create(
      extra_headers={
        "HTTP-Referer": "openrouter.ai", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "openrouter.ai", # Optional. Site title for rankings on openrouter.ai.
      },
      model="deepseek/deepseek-prover-v2",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": self.prompt
            }
          ]
        }
      ]
    )

    if not completion.choices is None:
      code = extract_last_code_block(completion.choices[0].message.content)
      print(f'not format code:\n {code}')
      fixed_code = autopep8.fix_code(code, options={'aggressive': 2})
      print(f'format code:\n {fixed_code}')
      return fixed_code
    
    else:
      return None

