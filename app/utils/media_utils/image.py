import os
import logging

from typing import Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def get_image_dimensions(image_path: str) -> Tuple[int, int]:

    if not os.path.exists(image_path):
        return (0, 0)

    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        logger.warning(f"Error getting image dimensions for {image_path}: {e}")
        return (0, 0)

def create_thumbnail(
    source_path: str,
    destination_path: str,
    max_size: Tuple[int, int] = (300, 300),
    format: str = 'JPEG',
    quality: int = 85
) -> bool:

    if not os.path.exists(source_path):
        return False

    try:

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        with Image.open(source_path) as img:

            if img.mode != 'RGB' and format == 'JPEG':
                img = img.convert('RGB')

            img.thumbnail(max_size)

            if format == 'JPEG':
                img.save(destination_path, format, quality=quality)
            else:
                img.save(destination_path, format)

        return True

    except Exception as e:
        logger.warning(f"Error creating thumbnail for {source_path}: {e}")
        return False

def create_placeholder_image(
    destination_path: str,
    text: str,
    size: Tuple[int, int] = (300, 300),
    bg_color: Tuple[int, int, int] = (50, 50, 50),
    text_color: Tuple[int, int, int] = (200, 200, 200),
    font_size: int = 20
) -> bool:

    try:

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        img = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("Arial", font_size)
        except IOError:
            font = ImageFont.load_default()

        try:

            text_width = draw.textlength(text, font=font)
            text_height = font_size
        except AttributeError:

            text_width, text_height = draw.textsize(text, font=font)

        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2

        draw.text((text_x, text_y), text, font=font, fill=text_color)

        img.save(destination_path, 'JPEG', quality=85)

        return True

    except Exception as e:
        logger.warning(f"Error creating placeholder image: {e}")
        return False

def get_image_metadata(image_path: str) -> Dict[str, Any]:

    if not os.path.exists(image_path):
        return {}

    try:
        metadata = {
            'file_size': os.path.getsize(image_path),
            'file_path': image_path,
            'filename': os.path.basename(image_path)
        }

        with Image.open(image_path) as img:
            metadata.update({
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'has_alpha': img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
            })

            exif_data = {}
            if hasattr(img, '_getexif') and callable(img._getexif):
                exif = img._getexif()
                if exif:
                    for tag, value in exif.items():
                        tag_name = EXIF_TAGS.get(tag, str(tag))
                        exif_data[tag_name] = str(value)

            if exif_data:
                metadata['exif'] = exif_data

        return metadata

    except Exception as e:
        logger.warning(f"Error getting image metadata for {image_path}: {e}")
        return {'error': str(e)}

EXIF_TAGS = {
    0x010F: 'Make',
    0x0110: 'Model',
    0x0112: 'Orientation',
    0x0132: 'DateTime',
    0x829A: 'ExposureTime',
    0x829D: 'FNumber',
    0x8827: 'ISO',
    0x9003: 'DateTimeOriginal',
    0x9004: 'DateTimeDigitized',
    0x9286: 'UserComment',
    0xA002: 'ExifImageWidth',
    0xA003: 'ExifImageHeight',
}