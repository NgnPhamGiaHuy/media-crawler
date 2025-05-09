import os
import logging

from PIL import Image, ImageDraw, ImageFont

from app.config import THUMBNAIL_SIZE

logger = logging.getLogger(__name__)

class ThumbnailGenerator:

    async def generate_thumbnail(self, file_path: str, thumbnail_path: str, media_type: str) -> bool:

        if media_type == 'image':

            if file_path.lower().endswith('.svg'):
                return await self._generate_svg_thumbnail(file_path, thumbnail_path)
            return await self._generate_image_thumbnail(file_path, thumbnail_path)
        elif media_type == 'video':
            return await self._generate_video_thumbnail(file_path, thumbnail_path)
        elif media_type == 'audio':
            return await self._generate_audio_thumbnail(file_path, thumbnail_path)
        else:
            return await self._generate_placeholder_thumbnail(thumbnail_path, f"File: {os.path.basename(file_path)}")

    async def _generate_svg_thumbnail(self, svg_path: str, thumbnail_path: str) -> bool:

        return await self._generate_placeholder_thumbnail(thumbnail_path, "SVG Image", "#4CAF50")

    async def _generate_image_thumbnail(self, image_path: str, thumbnail_path: str) -> bool:

        try:

            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

            with Image.open(image_path) as img:

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img.thumbnail(THUMBNAIL_SIZE)

                img.save(thumbnail_path, 'JPEG', quality=85)

            logger.debug(f"Generated image thumbnail: {thumbnail_path}")
            return True

        except Exception as e:
            logger.warning(f"Error generating image thumbnail: {e}")

            return await self._generate_placeholder_thumbnail(thumbnail_path, "Image Thumbnail Error")

    async def _generate_video_thumbnail(self, video_path: str, thumbnail_path: str) -> bool:

        try:

            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

            import subprocess
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', '00:00:03',
                '-frames:v', '1',
                '-vf', f'scale={THUMBNAIL_SIZE[0]}:{THUMBNAIL_SIZE[1]}:force_original_aspect_ratio=decrease',
                '-y',
                thumbnail_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
                logger.debug(f"Generated video thumbnail: {thumbnail_path}")
                return True

            return await self._generate_placeholder_thumbnail(thumbnail_path, "Video File", "#3F51B5")

        except Exception as e:
            logger.warning(f"Error generating video thumbnail: {e}")
            return await self._generate_placeholder_thumbnail(thumbnail_path, "Video File", "#3F51B5")

    async def _generate_audio_thumbnail(self, audio_path: str, thumbnail_path: str) -> bool:

        return await self._generate_placeholder_thumbnail(thumbnail_path, "Audio File", "#E91E63")

    async def _generate_placeholder_thumbnail(self, thumbnail_path: str, text: str, color: str = "#2196F3"):

        try:

            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

            img = Image.new('RGB', THUMBNAIL_SIZE, color=color)
            draw = ImageDraw.Draw(img)

            try:

                font = ImageFont.truetype("Arial", 14)
            except IOError:

                font = ImageFont.load_default()

            text_width = draw.textlength(text, font=font)
            text_position = ((THUMBNAIL_SIZE[0] - text_width) / 2, THUMBNAIL_SIZE[1] / 2)

            draw.text(text_position, text, fill="white", font=font)

            img.save(thumbnail_path, 'JPEG', quality=85)

            logger.debug(f"Generated placeholder thumbnail: {thumbnail_path}")
            return True

        except Exception as e:
            logger.warning(f"Error generating placeholder thumbnail: {e}")
            return False