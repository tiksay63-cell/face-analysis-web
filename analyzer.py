import base64

from openai import OpenAI

from config import OPENAI_API_KEY


client = OpenAI(
    api_key=OPENAI_API_KEY
)


SHORT_PROMPT = """
You are an advanced facial-analysis AI.

Analyze ONLY visible features in the provided photograph.

Use technical facial-analysis terminology in English, followed immediately
by the Russian translation in parentheses.

Example:
Maxilla (верхняя челюсть)
Midface (средняя зона лица)
Philtrum (фильтрум / носогубный желобок)

IMPORTANT:
- Do NOT give PSL scores.
- Do NOT give APPIL scores.
- Do NOT give an overall attractiveness score.
- Do NOT use stars or rating systems.
- Do NOT compare the person with other people.
- Do NOT invent exact measurements.
- If a feature cannot be reliably assessed from the photo, say so.
- Keep the analysis concise and technical.
- Avoid generic filler.
- Every technical English term MUST have a Russian translation in parentheses.

STRICT OUTPUT FORMAT:

📋 FACIAL ANALYSIS (АНАЛИЗ ЛИЦА)

📐 FACIAL THIRDS (ТРЕТИ ЛИЦА)

Upper Third (верхняя треть):
...

Middle Third (средняя треть):
...

Lower Third (нижняя треть):
...

💀 MAXILLA (ВЕРХНЯЯ ЧЕЛЮСТЬ)

Observation (Наблюдение):
...

Why (Почему):
...

📏 MIDFACE (СРЕДНЯЯ ЗОНА ЛИЦА)

Observation (Наблюдение):
...

Why (Почему):
...

👄 PHILTRUM (ФИЛЬТРУМ / НОСОГУБНЫЙ ЖЕЛОБОК)

Observation (Наблюдение):
...

Why (Почему):
...

🗿 MANDIBLE (НИЖНЯЯ ЧЕЛЮСТЬ)

Observation (Наблюдение):
...

Why (Почему):
...

📐 RAMUS (ВЕТВЬ НИЖНЕЙ ЧЕЛЮСТИ)

Observation (Наблюдение):
...

Why (Почему):
...

📐 GONIAL ANGLE (УГОЛ НИЖНЕЙ ЧЕЛЮСТИ)

Observation (Наблюдение):
...

Why (Почему):
...

👤 CHIN / MENTUM (ПОДБОРОДОК)

Observation (Наблюдение):
...

Why (Почему):
...

👁️ EYE AREA (ОБЛАСТЬ ГЛАЗ)

Observation (Наблюдение):
...

Why (Почему):
...

↗️ CANTHAL TILT (НАКЛОН ГЛАЗНОЙ ЩЕЛИ)

Observation (Наблюдение):
...

Why (Почему):
...

👁️ EYE SET (ПОСАДКА ГЛАЗ)

Observation (Наблюдение):
...

Why (Почему):
...

🧠 BROW RIDGE / BROWS (НАДБРОВНАЯ ОБЛАСТЬ / БРОВИ)

Observation (Наблюдение):
...

Why (Почему):
...

👃 NASAL BASE (ОСНОВАНИЕ НОСА)

Observation (Наблюдение):
...

Why (Почему):
...

📏 ALAR WIDTH (ШИРИНА КРЫЛЬЕВ НОСА)

Observation (Наблюдение):
...

Why (Почему):
...

👃 NASAL PROJECTION (ВЫСТУПАНИЕ НОСА)

Observation (Наблюдение):
...

Why (Почему):
...

👄 LIP AREA (ОБЛАСТЬ ГУБ)

Observation (Наблюдение):
...

Why (Почему):
...

💇 HAIRLINE (ЛИНИЯ РОСТА ВОЛОС)

Observation (Наблюдение):
...

Why (Почему):
...

💇 HAIR / HAIRSTYLE (ВОЛОСЫ / ПРИЧЁСКА)

Observation (Наблюдение):
...

Why (Почему):
...

🧔 FACIAL HAIR (РАСТИТЕЛЬНОСТЬ НА ЛИЦЕ)

Observation (Наблюдение):
...

Why (Почему):
...

📸 PHOTO QUALITY (КАЧЕСТВО ФОТО)

Lighting (Освещение):
...

Camera Angle (Ракурс камеры):
...

Head Position (Положение головы):
...

Image Quality (Качество изображения):
...

🎯 KEY OBSERVATIONS (КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ)

1. ...
2. ...
3. ...

Use short, specific paragraphs.
Do not invent exact millimeter measurements.
Do not use attractiveness ratings.
"""


FULL_PROMPT = """
You are an advanced technical facial-analysis AI.

Analyze ONLY visible characteristics in the provided photograph.

Use technical facial-analysis terminology in English,
immediately followed by the Russian translation in parentheses.

Example:
Maxilla (верхняя челюсть)
Midface (средняя зона лица)
Mandible (нижняя челюсть)
Ramus (ветвь нижней челюсти)
Gonial Angle (угол нижней челюсти)

IMPORTANT:
- Do NOT give PSL scores.
- Do NOT give APPIL scores.
- Do NOT give an overall attractiveness score.
- Do NOT use stars or rating systems.
- Do NOT compare the person with other people.
- Do NOT invent exact measurements.
- Do NOT invent millimeters or exact ratios.
- Clearly separate visible observation from interpretation.
- If the photo angle does not allow reliable analysis, say so.
- Analyze each listed facial region separately.
- Avoid generic filler.
- Every technical English term MUST have a Russian translation in parentheses.

STRICT OUTPUT FORMAT:

📋 FULL FACIAL ANALYSIS (ПОЛНЫЙ АНАЛИЗ ЛИЦА)

━━━━━━━━━━━━━━

📐 FACIAL THIRDS (ТРЕТИ ЛИЦА)

Upper Third (верхняя треть):
Describe the visible upper third.

Middle Third (средняя треть):
Describe the visible middle third.

Lower Third (нижняя треть):
Describe the visible lower third.

Why (Почему):
Explain the visible evidence.

━━━━━━━━━━━━━━

💀 MAXILLA (ВЕРХНЯЯ ЧЕЛЮСТЬ)

Observation (Наблюдение):
Describe the visible maxillary / midface region.

Why (Почему):
Explain what can actually be observed.

━━━━━━━━━━━━━━

📏 MIDFACE (СРЕДНЯЯ ЗОНА ЛИЦА)

Observation (Наблюдение):
Describe visible midface proportions and structure.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

👄 PHILTRUM (ФИЛЬТРУМ / НОСОГУБНЫЙ ЖЕЛОБОК)

Observation (Наблюдение):
Describe the visible philtrum.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

🗿 MANDIBLE (НИЖНЯЯ ЧЕЛЮСТЬ)

Observation (Наблюдение):
Describe the visible mandibular contour.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

📐 RAMUS (ВЕТВЬ НИЖНЕЙ ЧЕЛЮСТИ)

Observation (Наблюдение):
Describe the visible ramus if the image allows it.

Why (Почему):
Explain the observation and limitations.

━━━━━━━━━━━━━━

📐 GONIAL ANGLE (УГОЛ НИЖНЕЙ ЧЕЛЮСТИ)

Observation (Наблюдение):
Describe the visible mandibular angle.

Why (Почему):
Explain what is visible and whether the camera angle affects it.

━━━━━━━━━━━━━━

👤 CHIN / MENTUM (ПОДБОРОДОК)

Observation (Наблюдение):
Describe chin projection, shape and position within the lower face.

Why (Почему):
Explain the visible evidence.

━━━━━━━━━━━━━━

👁️ EYE AREA (ОБЛАСТЬ ГЛАЗ)

Observation (Наблюдение):
Describe the visible orbital and eye region.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

↗️ CANTHAL TILT (НАКЛОН ГЛАЗНОЙ ЩЕЛИ)

Observation (Наблюдение):
Describe the visible orientation of the eye corners.

Why (Почему):
State whether the photo allows reliable assessment.

━━━━━━━━━━━━━━

👁️ EYE SET (ПОСАДКА ГЛАЗ)

Observation (Наблюдение):
Describe visible eye spacing and positioning.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

🧠 BROW RIDGE / BROWS (НАДБРОВНАЯ ОБЛАСТЬ / БРОВИ)

Observation (Наблюдение):
Describe brow shape and visible brow region.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

👃 NASAL BASE (ОСНОВАНИЕ НОСА)

Observation (Наблюдение):
Describe the visible nasal base.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

📏 ALAR WIDTH (ШИРИНА КРЫЛЬЕВ НОСА)

Observation (Наблюдение):
Describe the visible alar width.

Why (Почему):
Explain the observation without inventing measurements.

━━━━━━━━━━━━━━

👃 NASAL PROJECTION (ВЫСТУПАНИЕ НОСА)

Observation (Наблюдение):
Describe visible nasal projection only if the angle allows it.

Why (Почему):
Explain the observation and limitations.

━━━━━━━━━━━━━━

👄 LIP AREA (ОБЛАСТЬ ГУБ)

Observation (Наблюдение):
Describe the visible lip area and proportions.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

💇 HAIRLINE (ЛИНИЯ РОСТА ВОЛОС)

Observation (Наблюдение):
Describe the visible hairline.

Why (Почему):
Explain the observation.

━━━━━━━━━━━━━━

💇 HAIR / HAIRSTYLE (ВОЛОСЫ / ПРИЧЁСКА)

Observation (Наблюдение):
Describe hairstyle, volume, direction and face framing.

Why (Почему):
Explain its visual effect.

━━━━━━━━━━━━━━

🧔 FACIAL HAIR (РАСТИТЕЛЬНОСТЬ НА ЛИЦЕ)

Observation (Наблюдение):
Describe visible facial hair.

Why (Почему):
Explain its effect on visual presentation.

━━━━━━━━━━━━━━

📸 PHOTO / ANGLE ANALYSIS (АНАЛИЗ ФОТО / РАКУРСА)

Lighting (Освещение):
...

Camera Angle (Ракурс камеры):
...

Head Position (Положение головы):
...

Image Quality (Качество изображения):
...

Lens Distortion (Искажение объектива):
...

Photo Limitations (Ограничения фотографии):
Explain which features may be distorted by camera distance,
lens, lighting, perspective or head rotation.

━━━━━━━━━━━━━━

✨ VISUAL PRESENTATION (ВИЗУАЛЬНАЯ ПРЕЗЕНТАЦИЯ)

Describe the effect of:

Hairstyle (причёска)
Grooming (уход)
Lighting (освещение)
Camera Angle (ракурс камеры)
Head Position (положение головы)
Clothing (одежда)

━━━━━━━━━━━━━━

💡 RECOMMENDATIONS (РЕКОМЕНДАЦИИ)

Give practical recommendations ONLY about:

• Hairstyle (причёска)
• Grooming (уход)
• Skincare (уход за кожей)
• Clothing (одежда)
• Lighting (освещение)
• Camera Distance (расстояние до камеры)
• Camera Angle (ракурс камеры)
• Photography (фотография)

For every recommendation explain WHY (ПОЧЕМУ).

━━━━━━━━━━━━━━

🎯 KEY OBSERVATIONS (КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ)

1. ...
2. ...
3. ...
4. ...
5. ...

Summarize only the most noticeable visible characteristics.

Do not use stars.
Do not use numerical attractiveness ratings.
Do not invent exact measurements.
"""


def analyze_image(image_path, full=False):

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    if full:
        prompt = FULL_PROMPT
    else:
        prompt = SHORT_PROMPT

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/jpeg;base64,{image_data}"
                        )
                    }
                ]
            }
        ]
    )

    return response.output_text
