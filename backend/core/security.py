import re
from pathlib import Path

MAX_FILENAME_LENGTH = 255
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def sanitize_filename(filename: str) -> str:
    clean_name = Path(filename).name
    clean_name = re.sub(r'[^\w\.-]', '_', clean_name)
    if len(clean_name) > MAX_FILENAME_LENGTH:
        ext = Path(clean_name).suffix
        clean_name = clean_name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    return clean_name

def validate_extension(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS
