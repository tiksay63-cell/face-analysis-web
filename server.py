import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from urllib.parse import parse_qsl

from fastapi import (
    FastAPI,
    File,
    Header,
    HTTPException,
    UploadFile,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    PHOTO_DIR,
)


app = FastAPI(
    title="Face Analysis API"
)


# ============================================================
# ПАПКА ДЛЯ ФОТОГРАФИЙ
# ============================================================

PHOTO_PATH = Path(PHOTO_DIR)

PHOTO_PATH.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ПРОВЕРКА TELEGRAM INIT DATA
# ============================================================

def validate_telegram_init_data(
    init_data: str
):
    if not init_data:
        raise HTTPException(
            status_code=401,
            detail="Telegram initData отсутствует"
        )

    try:
        parsed = dict(
            parse_qsl(
                init_data,
                keep_blank_values=True
            )
        )

        received_hash = parsed.pop(
            "hash",
            None
        )

        if not received_hash:
            raise HTTPException(
                status_code=401,
                detail="Telegram hash отсутствует"
            )

        data_check_string = "\n".join(
            f"{key}={parsed[key]}"
            for key in sorted(parsed.keys())
        )

        secret_key = hmac.new(
            b"WebAppData",
            TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            calculated_hash,
            received_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Неверная Telegram подпись"
            )

        # Проверяем свежесть авторизации
        auth_date = int(
            parsed.get(
                "auth_date",
                "0"
            )
        )

        current_time = int(
            time.time()
        )

        # 24 часа
        if current_time - auth_date > 86400:
            raise HTTPException(
                status_code=401,
                detail="Telegram initData устарел"
            )

        user_data = json.loads(
            parsed.get(
                "user",
                "{}"
            )
        )

        user_id = user_data.get(
            "id"
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Telegram user не найден"
            )

        return user_id

    except HTTPException:
        raise

    except Exception as error:

        print(
            "TELEGRAM VALIDATION ERROR:",
            error
        )

        raise HTTPException(
            status_code=401,
            detail="Не удалось проверить Telegram данные"
        )


# ============================================================
# ПРОВЕРКА СЕРВЕРА
# ============================================================

@app.get("/")
async def root():

    return {
        "status": "ok",
        "service": "Face Analysis API"
    }


# ============================================================
# ЗАГРУЗКА ФОТОГРАФИИ
# ============================================================

@app.post("/api/upload")
async def upload_photo(
    file: UploadFile = File(...),
    x_telegram_init_data: str | None = Header(
        default=None
    )
):

    user_id = validate_telegram_init_data(
        x_telegram_init_data
    )

    # Проверяем тип файла

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Разрешены только JPG, PNG и WEBP"
        )

    # Читаем файл

    contents = await file.read()

    # Ограничиваем размер
    # 10 MB

    if len(contents) > 10 * 1024 * 1024:

        raise HTTPException(
            status_code=400,
            detail="Файл слишком большой. Максимум 10 MB."
        )

    # Имя файла не берём от пользователя

    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }[file.content_type]

    filename = (
        f"{user_id}"
        f"{extension}"
    )

    destination = (
        PHOTO_PATH /
        filename
    )

    with open(
        destination,
        "wb"
    ) as output:

        output.write(
            contents
        )

    return {
        "success": True,
        "user_id": user_id,
        "filename": filename,
        "message": "Фотография успешно загружена"
    }
# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )