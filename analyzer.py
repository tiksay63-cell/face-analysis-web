import base64
import json
import re
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SHORT_PROMPT = """
Ты — жёсткий looksmaxxing-аналитик. Без воды, без сюсюканья.
Говори прямо: что слабо, что тянет вниз.

Анализируй только видимое на фото. Пиши на русском.
Термины: Английский (русский).

Обязательно:
- PSL от 1.0 до 10.0
- Тир: Sub3 / Sub5 / LTN / MTN / HTN / Chadlite / Chad / Gigachad
- APPIL от 1.0 до 10.0

Тиры:
Sub3 = 1.0–3.0
Sub5 = 3.1–4.5
LTN = 4.6–5.5
MTN = 5.6–6.4
HTN = 6.5–7.2
Chadlite = 7.3–7.9
Chad = 8.0–8.9
Gigachad = 9.0–10.0

Не завышай. Не давай советов как исправить — только факты.
Советы только в полном анализе.

Формат:

📋 Краткий разбор

⭐ PSL: X.X / 10
Тир: ...
Почему: 1–2 жёстких предложения.

⭐ APPIL: X.X / 10
Почему: 1 предложение.

💀 Структура
Maxilla / Midface: ...
Mandible / Jawline: ...
Gonial / Chin: ...

👁️ Глаза
Hunter Eyes / Canthal Tilt / Eye Set: ...

👃 Нос: ...
👄 Губы / Philtrum: ...
💇 Волосы: ...
🧔 Растительность: ...

📸 Фото: свет / ракурс / качество.

🎯 Главное
1. ...
2. ...
3. ...

⚠️ Что тянет вниз
• ...
• ...
• ...
"""

FULL_PROMPT = """
Ты — жёсткий looksmaxxing-аналитик. Без воды.
Говори прямо о слабостях. В конце — конкретные soft-maxxing рекомендации.

Только видимое. Русский. Термины: Английский (русский).

Обязательно:
- PSL 1.0–10.0
- Тир: Sub3 / Sub5 / LTN / MTN / HTN / Chadlite / Chad / Gigachad
- APPIL 1.0–10.0

Тиры:
Sub3 1.0–3.0 | Sub5 3.1–4.5 | LTN 4.6–5.5 | MTN 5.6–6.4
HTN 6.5–7.2 | Chadlite 7.3–7.9 | Chad 8.0–8.9 | Gigachad 9.0–10.0

Формат:

📋 Полный разбор

⭐ PSL: X.X / 10
Тир: ...
Разбивка:
• Кость: ...
• Гармония: ...
• Диморфизм: ...
• Угловатость: ...
• Глаза: ...
Почему: жёстко.

⭐ APPIL: X.X / 10
Почему: ...

📐 Трети лица: ...
💀 Maxilla / Midface: ...
🗿 Mandible / Jawline / Gonial / Chin: ...
👁️ Глаза (Hunter Eyes, Canthal Tilt, Eye Set): ...
🧠 Brow Ridge: ...
👃 Нос: ...
👄 Губы / Philtrum: ...
💇 Волосы: ...
🧔 Растительность: ...
📸 Фото / ракурс: ...
✨ Подача: ...

💡 Рекомендации
• Причёска: ...
• Уход / кожа: ...
• Свет и ракурс: ...
• Стиль: ...

🎯 Главное
1. ...
2. ...
3. ...
4. ...
5. ...
"""

STRUCTURED_PROMPT = """
Ты looksmaxxing-аналитик. Ответь ТОЛЬКО валидным JSON. Без markdown, без текста вокруг.

Формат:
{
  "psl": 6.4,
  "appil": 6.2,
  "tier": "MTN",
  "features": [
    {"name": "Глаза", "score": 6.9},
    {"name": "Нос", "score": 6.3},
    {"name": "Губы", "score": 6.4},
    {"name": "Скулы", "score": 6.1},
    {"name": "Челюсть", "score": 5.8},
    {"name": "Кожа", "score": 6.7},
    {"name": "Гармония", "score": 6.3}
  ],
  "summary": "1-2 предложения жёстко: сильные и слабые стороны."
}

Тир только: Sub3, Sub5, LTN, MTN, HTN, Chadlite, Chad, Gigachad
Числа от 1.0 до 10.0. Не завышай.
"""

def analyze_image(image_path, full=False):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    prompt = FULL_PROMPT if full else SHORT_PROMPT

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_data}"}
            ]
        }]
    )
    return response.output_text


def analyze_image_structured(image_path):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": STRUCTURED_PROMPT},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_data}"}
            ]
        }]
    )

    text = response.output_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    data = json.loads(text)
    psl = float(data.get("psl", 5.0))

    if psl <= 3.0:
        data["tier"] = "Sub3"
    elif psl <= 4.5:
        data["tier"] = "Sub5"
    elif psl <= 5.5:
        data["tier"] = "LTN"
    elif psl <= 6.4:
        data["tier"] = "MTN"
    elif psl <= 7.2:
        data["tier"] = "HTN"
    elif psl <= 7.9:
        data["tier"] = "Chadlite"
    elif psl <= 8.9:
        data["tier"] = "Chad"
    else:
        data["tier"] = "Gigachad"

    return data
