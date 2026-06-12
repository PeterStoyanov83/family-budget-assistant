"""Base scraper interface for all retail chains."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class ScrapedPrice:
    chain: str
    store_name: str
    product_name: str
    brand: str | None
    category: str | None
    price: float               # EUR
    regular_price: float | None
    unit_type: str | None      # kg, l, piece
    unit_size: float | None
    unit_size_label: str | None
    unit_price: float | None   # EUR per kg/l/piece
    is_member: bool
    is_promo: bool
    promo_valid_until: datetime | None
    image_url: str | None
    scraped_at: datetime = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now(timezone.utc)


class BaseScraper(ABC):
    chain: str
    base_url: str

    def __init__(self):
        self.logger = logging.getLogger(f"scraper.{self.chain}")

    @abstractmethod
    async def scrape(self) -> list[ScrapedPrice]:
        """Scrape all current prices and promotions."""
        ...

    def compute_unit_price(self, price: float, unit_type: str | None,
                           unit_size: float | None) -> float | None:
        """Normalise price to EUR per kg or EUR per litre."""
        if not unit_type or not unit_size or unit_size <= 0:
            return None
        if unit_type in ("kg", "l"):
            return round(price / unit_size, 4)
        if unit_type == "g":
            return round(price / (unit_size / 1000), 4)
        if unit_type == "ml":
            return round(price / (unit_size / 1000), 4)
        return None

    def score_promotion(self, promo_price: float, hist_avg_30d: float | None) -> str:
        """Score a promotion: real | average | fake."""
        if hist_avg_30d is None or hist_avg_30d <= 0:
            return "average"
        real_discount = (hist_avg_30d - promo_price) / hist_avg_30d
        if real_discount > 0.10:
            return "real"
        elif real_discount >= 0:
            return "average"
        return "fake"
