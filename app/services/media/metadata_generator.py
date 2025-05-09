import json
import logging
import subprocess

from PIL import Image

from app.models.media import MediaMetadata, ImageMetadata, VideoMetadata, AudioMetadata

logger = logging.getLogger(__name__)

class MediaMetadataGenerator:

    async def create_metadata(self, file_path: str, mime_type: str, file_size: int) -> MediaMetadata:

        category = mime_type.split('/')[0] if '/' in mime_type else ''

        if category == 'image':

            if mime_type == 'image/svg+xml' or file_path.lower().endswith('.svg'):
                return await self._create_svg_metadata(file_path, mime_type, file_size)
            else:
                return await self._create_image_metadata(file_path, mime_type, file_size)
        elif category == 'video':
            return await self._create_video_metadata(file_path, mime_type, file_size)
        elif category == 'audio':
            return await self._create_audio_metadata(file_path, mime_type, file_size)
        else:

            return MediaMetadata(
                file_size=file_size,
                mime_type=mime_type,
                content_type=category
            )

    async def _create_svg_metadata(self, file_path: str, mime_type: str, file_size: int) -> ImageMetadata:

        return ImageMetadata(
            file_size=file_size,
            mime_type=mime_type,
            content_type='image',
            width=0,
            height=0,
            format='SVG',
            mode='Vector'
        )

    async def _create_image_metadata(self, file_path: str, mime_type: str, file_size: int) -> ImageMetadata:

        width, height = 0, 0
        image_format = ''
        mode = ''

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                image_format = img.format
                mode = img.mode
        except Exception as e:
            logger.warning(f"Error creating image metadata: {e}")

        return ImageMetadata(
            file_size=file_size,
            mime_type=mime_type,
            content_type='image',
            width=width,
            height=height,
            format=image_format,
            mode=mode
        )

    async def _create_video_metadata(self, file_path: str, mime_type: str, file_size: int) -> VideoMetadata:

        width, height = 0, 0
        duration = 0.0
        video_format = ''
        codec = ''

        try:

            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)

                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        width = int(stream.get('width', 0))
                        height = int(stream.get('height', 0))
                        codec = stream.get('codec_name', '')

                format_data = data.get('format', {})
                video_format = format_data.get('format_name', '')
                duration = float(format_data.get('duration', 0))

        except Exception as e:
            logger.warning(f"Error creating video metadata: {e}")

        return VideoMetadata(
            file_size=file_size,
            mime_type=mime_type,
            content_type='video',
            width=width,
            height=height,
            duration=duration,
            format=video_format,
            codec=codec
        )

    async def _create_audio_metadata(self, file_path: str, mime_type: str, file_size: int) -> AudioMetadata:

        duration = 0.0
        bitrate = 0
        audio_format = ''
        codec = ''

        try:

            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)

                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        codec = stream.get('codec_name', '')
                        bitrate = int(stream.get('bit_rate', 0))

                format_data = data.get('format', {})
                audio_format = format_data.get('format_name', '')
                duration = float(format_data.get('duration', 0))

                if bitrate == 0 and 'bit_rate' in format_data:
                    bitrate = int(format_data.get('bit_rate', 0))

        except Exception as e:
            logger.warning(f"Error creating audio metadata: {e}")

        return AudioMetadata(
            file_size=file_size,
            mime_type=mime_type,
            content_type='audio',
            duration=duration,
            bitrate=bitrate,
            format=audio_format,
            codec=codec
        )