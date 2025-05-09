import os
import magic
import mimetypes

from typing import Optional

from app.config import MEDIA_TYPES, MEDIA_EXTENSIONS

mimetypes.init()

def get_mime_type(filepath: str, use_magic: bool = True) -> str:

    if not os.path.exists(filepath):
        return 'application/octet-stream'

    mime_type = None

    if use_magic:
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(filepath)
        except Exception:

            mime_type = None

    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filepath)

    if not mime_type:
        _, ext = os.path.splitext(filepath.lower())

        for media_type, extensions in MEDIA_EXTENSIONS.items():
            if ext in extensions:
                guessed_mime = mimetypes.guess_type(f'file{ext}')[0]
                if guessed_mime:
                    return guessed_mime
        mime_type = 'application/octet-stream'

    return mime_type or 'application/octet-stream'

def get_media_type(mime_type: str) -> Optional[str]:

    if not mime_type:
        return None

    mime_lower = mime_type.lower()

    for media_type, mime_list in MEDIA_TYPES.items():
        if any(mime in mime_lower for mime in mime_list):
            return media_type

    if mime_lower.startswith('image/'):
        return 'image'
    elif mime_lower.startswith('video/'):
        return 'video'
    elif mime_lower.startswith('audio/'):
        return 'audio'

    return None

def get_extension_for_mime(mime_type: str) -> str:

    ext = mimetypes.guess_extension(mime_type)
    if ext:
        return ext

    for media_type, extensions in MEDIA_EXTENSIONS.items():
        for ext in extensions:
            guessed = mimetypes.guess_type(f'file{ext}')[0]
            if guessed == mime_type:
                return ext

    media_type = get_media_type(mime_type)
    if media_type == 'image':
        return '.jpg'
    elif media_type == 'video':
        return '.mp4'
    elif media_type == 'audio':
        return '.mp3'

    return '.bin'

def is_media_file(filepath: str) -> bool:

    mime_type = get_mime_type(filepath)
    return get_media_type(mime_type) is not None