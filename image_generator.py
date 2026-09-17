import base64
import os
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY
)

EDIT_PROMPT = """
Transform this portrait into a highly attractive, polished, high-end looksmaxxing version of the same person.

Goals:
- Make the person look significantly more attractive, clean, sharp and high-value.
- Improve skin quality: clearer, smoother, healthier, with natural glow (remove acne, redness, uneven tone, dark circles if present).
- Enhance eye area: brighter, clearer eyes, better definition, subtle positive canthal tilt effect through lighting if possible.
- Improve jawline definition and facial angularity through professional lighting and subtle contouring (do not reshape the actual bone structure).
- Make hair look denser, cleaner, better styled and more attractive.
- Optimize lighting: soft but directional, flattering, high-end studio quality.
- Improve color, contrast, sharpness and overall photographic quality.
- Clean / replace background with a premium, minimal, professional one.
- Improve clothing presentation if visible.

Critical rules:
- The result MUST still clearly be the same person.
- Do NOT drastically change facial proportions, nose shape, eye shape, lip shape or overall bone structure.
- Do NOT turn the person into a completely different face.
- Keep the transformation realistic and believable (high-end retouch + flattering photography, not plastic surgery).
- Prefer natural attractiveness over over-processed "AI face".

Style target: premium male/female portrait used in high-end dating profiles, fashion lookbooks or professional headshots after soft-maxxing.
"""

def generate_improved_photo(image_path):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = client.images.edit(
        model="gpt-image-2",
        image=image_bytes,
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
        output_file.write(
            base64.b64decode(image_base64)
        )

    return output_path
