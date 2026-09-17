import base64

from openai import OpenAI

from config import OPENAI_API_KEY
from prompts import ANALYSIS_PROMPT


client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_image(image_path, full=False):

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    prompt = ANALYSIS_PROMPT

    if full:
        prompt += """

Это полный расширенный анализ.
Сделай более подробный разбор видимых характеристик фотографии,
чем в обычном анализе. Структурируй ответ по отдельным разделам
и добавь больше конкретных наблюдений по изображению.
"""

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
                        "image_url":
                            f"data:image/jpeg;base64,{encoded_image}"
                    }
                ]
            }
        ]
    )

    return response.output_text
