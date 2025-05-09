import logging

from typing import Dict, Any
from datetime import datetime

from app.models.crawler import CrawlStats, CrawlPage

logger = logging.getLogger(__name__)

class StatsManager:

    def __init__(self):
        self.stats = CrawlStats()
        self.reset()

    def reset(self):

        self.stats = CrawlStats()
        self.stats.start_time = datetime.now()

    def update_from_page(self, page: CrawlPage):

        self.stats.total_pages += 1

        if page.is_successful:
            self.stats.successful_pages += 1
        else:
            self.stats.failed_pages += 1

        media_count = len(page.media_urls)
        self.stats.total_media += media_count

        if page.is_successful:
            logger.debug(f"Successfully crawled {page.url} (depth {page.depth}): "
                        f"found {media_count} media URLs")
        else:
            logger.debug(f"Failed to crawl {page.url} (depth {page.depth}): {page.error_message}")

    def finalize(self):

        self.stats.end_time = datetime.now()

    def get_stats(self) -> CrawlStats:

        return self.stats

    def get_formatted_stats(self) -> Dict[str, Any]:

        duration = self.stats.duration

        formatted = {
            "pages": {
                "total": self.stats.total_pages,
                "successful": self.stats.successful_pages,
                "failed": self.stats.failed_pages,
                "success_rate": self._percentage(self.stats.successful_pages, self.stats.total_pages)
            },
            "media": {
                "total": self.stats.total_media,
                "images": self.stats.total_images,
                "videos": self.stats.total_videos,
                "audio": self.stats.total_audio
            },
            "timing": {
                "duration_seconds": duration,
                "duration_formatted": self._format_duration(duration),
                "pages_per_second": round(self.stats.total_pages / duration, 2) if duration > 0 else 0
            }
        }

        return formatted

    def _percentage(self, part: int, total: int) -> float:

        return round(100 * part / total, 1) if total > 0 else 0

    def _format_duration(self, seconds: float) -> str:

        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = seconds % 60
            return f"{minutes} min {int(remaining_seconds)} sec"
        else:
            hours = int(seconds / 3600)
            remaining = seconds % 3600
            minutes = int(remaining / 60)
            return f"{hours} hr {minutes} min"