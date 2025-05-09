import os
import uuid
import hashlib

from datetime import datetime
from typing import Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator

class MediaMetadata(BaseModel):
    file_size: int
    mime_type: str
    created_at: datetime = Field(default_factory=datetime.now)
    content_type: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaMetadata':
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

class ImageMetadata(MediaMetadata):
    width: int = 0
    height: int = 0
    format: str = ""
    mode: str = ""

class VideoMetadata(MediaMetadata):
    width: int = 0
    height: int = 0
    duration: float = 0.0
    format: str = ""
    codec: str = ""

class AudioMetadata(MediaMetadata):
    duration: float = 0.0
    bitrate: int = 0
    format: str = ""
    codec: str = ""

class Media(BaseModel):
    url: str
    source_url: str
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Optional[Union[MediaMetadata, ImageMetadata, VideoMetadata, AudioMetadata]] = None
    media_type: str = ""
    filename: str = ""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    class Config:
        arbitrary_types_allowed = True

    @validator('filename', pre=True, always=True)
    def set_filename(cls, v, values):
        if not v and 'url' in values and values['url']:
            v = os.path.basename(values['url'].split('?')[0])

        if v and '.' not in v and 'metadata' in values and values['metadata']:
            metadata = values['metadata']
            if hasattr(metadata, 'mime_type'):
                ext_map = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'video/mp4': '.mp4',
                    'audio/mpeg': '.mp3',
                }
                v += ext_map.get(metadata.mime_type, '.bin')
        return v

    @property
    def display_name(self) -> str:
        if len(self.filename) > 25:
            return f"{self.filename[:22]}..."
        return self.filename

    @property
    def file_extension(self) -> str:
        return os.path.splitext(self.filename)[1].lower() if self.filename else ""

    @property
    def cached_filename(self) -> str:
        if self.file_path:
            return os.path.basename(self.file_path)
        return ""

    @property
    def url_hash(self) -> str:
        if self.url:
            return hashlib.md5(self.url.encode()).hexdigest()
        return ""

    def model_dump(self) -> Dict[str, Any]:
        result = super().model_dump(exclude={'metadata'})
        result["cached_filename"] = self.cached_filename

        if self.metadata:
            result["metadata"] = {
                "file_size": self.metadata.file_size,
                "mime_type": self.metadata.mime_type,
                "created_at": self.metadata.created_at.isoformat(),
                "content_type": self.metadata.content_type,
            }

            if isinstance(self.metadata, ImageMetadata):
                result["metadata"].update({
                    "width": self.metadata.width,
                    "height": self.metadata.height,
                    "format": self.metadata.format,
                })
            elif isinstance(self.metadata, VideoMetadata):
                result["metadata"].update({
                    "width": self.metadata.width,
                    "height": self.metadata.height,
                    "duration": self.metadata.duration,
                    "format": self.metadata.format,
                })
            elif isinstance(self.metadata, AudioMetadata):
                result["metadata"].update({
                    "duration": self.metadata.duration,
                    "bitrate": self.metadata.bitrate,
                    "format": self.metadata.format,
                })

        return result

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Media':
        media_data = {k: v for k, v in data.items() if k != 'metadata'}

        media = cls(**media_data)

        if 'metadata' in data:
            metadata = data['metadata']
            media_type = data.get('media_type', '')

            if media_type == 'image':
                media.metadata = ImageMetadata.from_dict(metadata)
            elif media_type == 'video':
                media.metadata = VideoMetadata.from_dict(metadata)
            elif media_type == 'audio':
                media.metadata = AudioMetadata.from_dict(metadata)
            else:
                media.metadata = MediaMetadata.from_dict(metadata)

        return media