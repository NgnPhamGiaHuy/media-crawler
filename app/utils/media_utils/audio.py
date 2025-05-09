import os
import json
import logging
import subprocess

from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

def get_audio_info(audio_path: str) -> Dict[str, Any]:

    if not os.path.exists(audio_path):
        return {}

    try:

        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            audio_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"ffprobe failed for {audio_path}: {result.stderr}")
            return {}

        data = json.loads(result.stdout)

        info = {
            'file_size': os.path.getsize(audio_path),
            'file_path': audio_path,
            'filename': os.path.basename(audio_path)
        }

        format_data = data.get('format', {})
        info.update({
            'format': format_data.get('format_name', ''),
            'duration': float(format_data.get('duration', 0)),
            'bit_rate': int(format_data.get('bit_rate', 0)) if format_data.get('bit_rate') else 0,
        })

        audio_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
        if audio_stream:
            info.update({
                'codec': audio_stream.get('codec_name', ''),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'channel_layout': audio_stream.get('channel_layout', ''),
                'bits_per_sample': int(audio_stream.get('bits_per_sample', 0)) if audio_stream.get('bits_per_sample') else None,
            })

        return info

    except Exception as e:
        logger.warning(f"Error getting audio info for {audio_path}: {e}")
        return {'error': str(e)}

def create_audio_waveform_image(
    audio_path: str,
    output_path: str,
    width: int = 800,
    height: int = 200,
    bg_color: str = '0x000000',
    wave_color: str = '0x00FFFF'
) -> bool:

    if not os.path.exists(audio_path):
        return False

    try:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-filter_complex', f"showwavespic=s={width}x{height}:colors={wave_color}",
            '-frames:v', '1',
            '-y', output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"ffmpeg failed to create waveform: {result.stderr}")
            return False

        return os.path.exists(output_path)

    except Exception as e:
        logger.warning(f"Error creating audio waveform: {e}")
        return False

def create_audio_spectrogram(
    audio_path: str,
    output_path: str,
    width: int = 800,
    height: int = 400
) -> bool:

    if not os.path.exists(audio_path):
        return False

    try:

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-filter_complex', f"showspectrumpic=s={width}x{height}",
            '-frames:v', '1',
            '-y', output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"ffmpeg failed to create spectrogram: {result.stderr}")
            return False

        return os.path.exists(output_path)

    except Exception as e:
        logger.warning(f"Error creating audio spectrogram: {e}")
        return False

def create_audio_thumbnail(
    audio_path: str,
    output_path: str,
    size: Tuple[int, int] = (300, 300)
) -> bool:

    return create_audio_waveform_image(
        audio_path,
        output_path,
        width=size[0],
        height=size[1],
        bg_color='0x333333',
        wave_color='0x66CCFF'
    )

def get_audio_duration(audio_path: str) -> float:

    if not os.path.exists(audio_path):
        return 0.0

    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            audio_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return 0.0

        data = json.loads(result.stdout)
        duration = float(data.get('format', {}).get('duration', 0))

        return duration

    except Exception as e:
        logger.warning(f"Error getting audio duration for {audio_path}: {e}")
        return 0.0