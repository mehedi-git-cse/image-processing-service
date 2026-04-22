from io import BytesIO

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.utils.response import error


async def validate_uploaded_image(image: UploadFile):
    allowed_exts = {"jpg", "jpeg", "png"}
    allowed_mime_types = {"image/jpeg", "image/png"}
    filename = (image.filename or "").lower()
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    content_type = (getattr(image, "content_type", "") or "").lower()

    if ext not in allowed_exts or content_type not in allowed_mime_types:
        return error(msg="Uploaded file must be a JPG or PNG image", status_code=400)

    try:
        file_bytes = await image.read()
        if not file_bytes:
            return error(msg="Image file is empty", status_code=400)

        jpeg_signature = file_bytes.startswith(b"\xff\xd8\xff")
        png_signature = file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        if not jpeg_signature and not png_signature:
            return error(msg="Invalid image file content", status_code=400)

        with Image.open(BytesIO(file_bytes)) as img:
            img_format = (img.format or "").upper()
            if img_format not in {"JPEG", "PNG"}:
                return error(msg="Uploaded file must be a JPG or PNG image", status_code=400)
            img.verify()

        image.file.seek(0)
        return None
    except (UnidentifiedImageError, OSError, ValueError):
        image.file.seek(0)
        return error(msg="Invalid image file content", status_code=400)