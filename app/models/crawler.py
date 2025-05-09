import uuid

from typing import Dict, Optional, Set, Any
from datetime import datetime
from pydantic import BaseModel, Field

class CrawlSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    pages_crawled: int = 0
    media_found: int = 0
    status: str = "idle"
    error_message: Optional[str] = None
    max_depth: int = 1
    cache_dir: str = ""

    @property
    def duration(self) -> float:

        if not self.end_time:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()

    def model_dump(self) -> Dict[str, Any]:
        result = super().model_dump()
        result["duration"] = self.duration
        if self.start_time:
            result["start_time"] = self.start_time.isoformat()
        if self.end_time:
            result["end_time"] = self.end_time.isoformat()
        return result

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

class CrawlStats(BaseModel):
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_media: int = 0
    total_images: int = 0
    total_videos: int = 0
    total_audio: int = 0
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> float:
        if not self.end_time:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()

    def model_dump(self) -> Dict[str, Any]:
        result = super().model_dump()
        result["duration"] = self.duration
        return result

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

class CrawlPage(BaseModel):
    url: str
    depth: int = 0
    parent_url: Optional[str] = None
    discovered_urls: Set[str] = Field(default_factory=set)
    media_urls: Set[str] = Field(default_factory=set)
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def is_successful(self) -> bool:
        return self.status_code is not None and 200 <= self.status_code < 300

    @property
    def duration(self) -> float:
        if not self.end_time:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()

    def model_dump(self) -> Dict[str, Any]:
        result = super().model_dump()
        result["is_successful"] = self.is_successful
        result["duration"] = self.duration
        result["discovered_urls"] = list(self.discovered_urls)
        result["media_urls"] = list(self.media_urls)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()