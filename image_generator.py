import base64
import os
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

EDIT_PROMPT = """
Transform this portrait into a highly attractive, polished, high-end looksmaxxing version of the same person.

Goals:
- Make the person look significantly more attractive, clean, sharp and high-value.
- Improve skin quality: clearer, smoother, healthier, with natural glow.
- Enhance eye area: brighter and clearer eyes.
- Improve jawline definition through lighting and subtle contouring (do not change bone structure).
- Make hair look denser, cleaner and better styled.
- Use soft, flattering, high-end studio lighting.
- Improve color, contrast and sharpness.
- Clean background or replace with a premium minimal one.

Critical rules:
- The result MUST still clearly be the same person.
- Do NOT drastically change facial proportions, nose, eyes or lips.
- Keep it realistic and natural (high-end retouch, not plastic surgery).
"""

def generate_improved_photo(image_path):
    # Открываем файл правильно, как image/jpeg
    with open(image_path, "rb") as image_file:
        response = client.images.edit(
            model="gpt-image-2",
            image=(image_path, image_file, "image/jpeg"),  # ← вот исправление
            prompt=EDIT_PROMPT,
        )

    if not response.data:
        raise RuntimeError("Image API returned no image.")

    image_base64 = response.data[0].b64_json
    if not image_base64:
        raise RuntimeError("Image API returned empty image data.")

    output_path = "data/improved_photo.png"
    os.makedirs("data", exist_ok=True)

    with open(output_path, "wb") as output_file:
        output_file.write(base64.b64decode(image_base64))

    return output_path
