import os
import glob
import shutil
import logging

from typing import List, Dict

from app.utils.file_utils.path import ensure_directory_exists

logger = logging.getLogger(__name__)

def ensure_empty_directory(directory: str) -> None:

    if os.path.exists(directory):

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                logger.warning(f"Error removing {item_path}: {e}")
    else:

        os.makedirs(directory, exist_ok=True)

def calculate_directory_size(directory: str) -> int:

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def count_files(directory: str, pattern: str = "*") -> int:

    return len(glob.glob(os.path.join(directory, pattern)))

def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:

    if recursive:
        return glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    else:
        return glob.glob(os.path.join(directory, pattern))

def get_directory_stats(directory: str) -> Dict[str, any]:

    if not os.path.exists(directory):
        return {
            "exists": False,
            "size": 0,
            "file_count": 0
        }

    size = calculate_directory_size(directory)
    file_count = 0

    for dirpath, dirnames, filenames in os.walk(directory):
        file_count += len(filenames)

    return {
        "exists": True,
        "size": size,
        "file_count": file_count,
        "size_human": format_file_size(size)
    }

def move_file(source: str, destination: str, overwrite: bool = False) -> bool:

    if not os.path.exists(source):
        return False

    dest_dir = os.path.dirname(destination)
    ensure_directory_exists(dest_dir)

    if os.path.exists(destination) and not overwrite:
        return False

    try:
        shutil.move(source, destination)
        return True
    except Exception as e:
        logger.warning(f"Error moving {source} to {destination}: {e}")
        return False

def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:

    if not os.path.exists(source):
        return False

    dest_dir = os.path.dirname(destination)
    ensure_directory_exists(dest_dir)

    if os.path.exists(destination) and not overwrite:
        return False

    try:
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.warning(f"Error copying {source} to {destination}: {e}")
        return False

def delete_file(filepath: str) -> bool:

    if not os.path.exists(filepath):
        return False

    try:
        os.remove(filepath)
        return True
    except Exception as e:
        logger.warning(f"Error deleting {filepath}: {e}")
        return False

def delete_directory(directory: str) -> bool:

    if not os.path.exists(directory):
        return False

    try:
        shutil.rmtree(directory)
        return True
    except Exception as e:
        logger.warning(f"Error deleting directory {directory}: {e}")
        return False

def format_file_size(size_bytes: int) -> str:

    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"