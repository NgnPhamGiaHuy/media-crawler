import os
import uuid
import string
import hashlib

from typing import Tuple

def sanitize_filename(filename: str) -> str:

    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    sanitized = ''.join(c for c in filename if c in valid_chars)

    sanitized = sanitized.replace(' ', '_')

    if len(sanitized) > 128:
        base, ext = os.path.splitext(sanitized)
        sanitized = f"{base[:120]}{ext}"

    if not sanitized:
        sanitized = str(uuid.uuid4().hex)

    return sanitized

def get_unique_filename(path: str, filename: str) -> str:

    if not os.path.exists(os.path.join(path, filename)):
        return filename

    base, ext = os.path.splitext(filename)
    counter = 1

    while os.path.exists(os.path.join(path, f"{base}_{counter}{ext}")):
        counter += 1

    return f"{base}_{counter}{ext}"

def ensure_directory_exists(directory: str) -> None:

    os.makedirs(directory, exist_ok=True)

def get_filename_from_url(url: str) -> str:

    path = url.split('?')[0].split('/')

    filename = os.path.basename(path)

    if not filename:
        filename = hashlib.md5(url.encode()).hexdigest()

    return sanitize_filename(filename)

def split_filename(filename: str) -> Tuple[str, str]:

    return os.path.splitext(filename)

def generate_unique_path(directory: str, filename: str = None) -> str:

    ensure_directory_exists(directory)

    if not filename:
        filename = f"{uuid.uuid4().hex}"
    else:
        filename = sanitize_filename(filename)

    unique_filename = get_unique_filename(directory, filename)

    return os.path.join(directory, unique_filename)