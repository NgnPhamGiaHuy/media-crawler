import os
import json
import logging
import subprocess

from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

def get_video_info(video_path: str) -> Dict[str, Any]:

    if not os.path.exists(video_path):
        return {}

    try:

        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"ffprobe failed for {video_path}: {result.stderr}")
            return {}

        data = json.loads(result.stdout)

        info = {
            'file_size': os.path.getsize(video_path),
            'file_path': video_path,
            'filename': os.path.basename(video_path)
        }

        format_data = data.get('format', {})
        info.update({
            'format': format_data.get('format_name', ''),
            'duration': float(format_data.get('duration', 0)),
            'bit_rate': int(format_data.get('bit_rate', 0)) if format_data.get('bit_rate') else 0,
        })

        video_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
        if video_stream:
            info.update({
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'codec': video_stream.get('codec_name', ''),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')) if '/' in video_stream.get('r_frame_rate', '0/1') else 0,
                'pix_fmt': video_stream.get('pix_fmt', ''),
                'video_bitrate': int(video_stream.get('bit_rate', 0)) if video_stream.get('bit_rate') else 0,
            })

        audio_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
        if audio_stream:
            info.update({
                'audio_codec': audio_stream.get('codec_name', ''),
                'audio_channels': int(audio_stream.get('channels', 0)),
                'audio_sample_rate': int(audio_stream.get('sample_rate', 0)),
                'audio_bitrate': int(audio_stream.get('bit_rate', 0)) if audio_stream.get('bit_rate') else 0,
            })

        return info

    except Exception as e:
        logger.warning(f"Error getting video info for {video_path}: {e}")
        return {'error': str(e)}

def extract_video_frame(
    video_path: str,
    output_path: str,
    time_offset: float = 1.0,
    size: Optional[Tuple[int, int]] = None
) -> bool:

    if not os.path.exists(video_path):
        return False

    try:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', str(time_offset),
            '-frames:v', '1',
            '-q:v', '2'
        ]

        if size:
            cmd.extend(['-s', f"{size[0]}x{size[1]}"])

        cmd.extend(['-y', output_path])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"ffmpeg failed to extract frame: {result.stderr}")
            return False

        return os.path.exists(output_path)

    except Exception as e:
        logger.warning(f"Error extracting video frame: {e}")
        return False

def create_video_thumbnail(
    video_path: str,
    output_path: str,
    size: Tuple[int, int] = (300, 300)
) -> bool:

    if not os.path.exists(video_path):
        return False

    try:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        video_info = get_video_info(video_path)
        duration = video_info.get('duration', 0)

        time_offset = max(1.0, duration * 0.1)

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', str(time_offset),
            '-frames:v', '1',
            '-vf', f'scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease',
            '-q:v', '2',
            '-y', output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"ffmpeg failed to create thumbnail: {result.stderr}")
            return False

        return os.path.exists(output_path)

    except Exception as e:
        logger.warning(f"Error creating video thumbnail: {e}")
        return False

def get_video_duration(video_path: str) -> float:

    if not os.path.exists(video_path):
        return 0.0

    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return 0.0

        data = json.loads(result.stdout)
        duration = float(data.get('format', {}).get('duration', 0))

        return duration

    except Exception as e:
        logger.warning(f"Error getting video duration for {video_path}: {e}")
        return 0.0