import base64
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SHORT_PROMPT = """
Ты — looksmaxxing-аналитик лица.
Анализируй только то, что видно на фото.

Пиши на чистом русском языке.
Технические термины пиши так: Английский термин (русский перевод).

Обязательно поставь:
- PSL оценку от 1.0 до 10.0 + тир (Sub5 / LTN / MTN / HTN / Chadlite / Chad / Gigachad)
- APPIL оценку от 1.0 до 10.0

Будь честным, не завышай оценки.
Не придумывай миллиметры.
Если что-то плохо видно — так и напиши.

Формат ответа:

📋 Краткий анализ

⭐ PSL: X.X / 10
Тир: ...
Почему: ...

⭐ APPIL: X.X / 10
Почему: ...

📐 Трети лица
Верхняя: ...
Средняя: ...
Нижняя: ...

💀 Maxilla / Midface (верхняя челюсть / средняя зона)
...

🗿 Mandible / Jawline (нижняя челюсть)
...

📐 Gonial Angle / Ramus (гониальный угол / ветвь)
...

👤 Chin (подбородок)
...

👁️ Глаза
Hunter Eyes: ...
Canthal Tilt: ...
Eye Set: ...

👃 Нос
...

👄 Губы и Philtrum
...

💇 Волосы и линия роста
...

🧔 Растительность
...

📸 Качество фото
...

🎯 Главные наблюдения
1. ...
2. ...
3. ...
"""

FULL_PROMPT = """
Ты — looksmaxxing-аналитик лица.
Анализируй только то, что видно на фото.

Пиши на чистом русском языке.
Технические термины пиши так: Английский термин (русский перевод).

Обязательно поставь:
- PSL оценку от 1.0 до 10.0 + тир (Sub5 / LTN / MTN / HTN / Chadlite / Chad / Gigachad)
- APPIL оценку от 1.0 до 10.0

Будь честным, не завышай оценки.
Не придумывай миллиметры.
Если что-то плохо видно — так и напиши.

Формат ответа:

📋 Полный анализ

⭐ PSL: X.X / 10
Тир: ...
Разбивка:
• Костная структура: ...
• Гармония: ...
• Диморфизм: ...
• Угловатость: ...
• Глаза: ...
Почему: ...

⭐ APPIL: X.X / 10
Почему: ...

📐 Трети лица
...

💀 Maxilla (верхняя челюсть)
...

📏 Midface (средняя зона)
...

🗿 Mandible / Jawline
...

📐 Gonial Angle / Ramus
...

👤 Chin (подбородок)
...

👁️ Глаза
Hunter Eyes: ...
Canthal Tilt: ...
Eye Set: ...

🧠 Brow Ridge (надбровные дуги)
...

👃 Нос
...

👄 Губы и Philtrum
...

💇 Волосы
...

🧔 Растительность
...

📸 Анализ фото и ракурса
...

✨ Визуальная подача
...

💡 Рекомендации (только soft-maxxing)
• Причёска: ...
• Уход: ...
• Кожа: ...
• Освещение и ракурс: ...

🎯 Главные наблюдения
1. ...
2. ...
3. ...
4. ...
5. ...
"""

def analyze_image(image_path, full=False):
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    prompt = FULL_PROMPT if full else SHORT_PROMPT

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_data}"
                    }
                ]
            }
        ]
    )
    return response.output_text
