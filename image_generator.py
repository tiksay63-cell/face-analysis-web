import os
import requests

HF_TOKEN = "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"

API_URL = "https://api-inference.huggingface.co/models/sczhou/CodeFormer"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def generate_improved_photo(image_path):
    with open(image_path, "rb") as f:
        data = f.read()

    response = requests.post(
        API_URL,
        headers=headers,
        data=data,
        timeout=90
    )

    if response.status_code != 200:
        if response.status_code == 503:
            raise RuntimeError("Модель сейчас загружается. Подожди 20–30 секунд и попробуй ещё раз.")
        raise RuntimeError(f"Ошибка Hugging Face {response.status_code}: {response.text}")

    output_path = "data/improved_photo.png"
    os.makedirs("data", exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path
