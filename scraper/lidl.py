"""Lidl Bulgaria scraper — runs every Thursday 06:00."""
import re
from datetime import datetime, timezone

from scraper.base import BaseScraper, ScrapedPrice


class LidlScraper(BaseScraper):
    chain = "lidl"
    base_url = "https://www.lidl.bg"

    # Lidl BG serves promotions at /bg/offers — Playwright needed for JS rendering
    OFFERS_URL = "https://www.lidl.bg/bg/offers"
    CATALOG_URL = "https://www.lidl.bg/bg/shop"

    async def scrape(self) -> list[ScrapedPrice]:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            self.logger.error("playwright not installed")
            return []

        results: list[ScrapedPrice] = []
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (compatible; FamilyBudgetBot/1.0)",
                locale="bg-BG",
            )
            page = await context.new_page()

            try:
                results.extend(await self._scrape_offers(page))
            except Exception as exc:
                self.logger.error("Lidl offers scrape failed: %s", exc)

            await browser.close()

        self.logger.info("Lidl: scraped %d prices", len(results))
        return results

    async def _scrape_offers(self, page) -> list[ScrapedPrice]:
        await page.goto(self.OFFERS_URL, wait_until="networkidle", timeout=30_000)
        await page.wait_for_selector("[data-qa='product-grid-item']", timeout=15_000)

        items = await page.query_selector_all("[data-qa='product-grid-item']")
        results = []
        for item in items:
            try:
                results.append(await self._parse_offer_item(item))
            except Exception as exc:
                self.logger.debug("Failed to parse Lidl item: %s", exc)

        return [r for r in results if r is not None]

    async def _parse_offer_item(self, item) -> ScrapedPrice | None:
        name_el = await item.query_selector("[data-qa='product-title']")
        price_el = await item.query_selector("[data-qa='product-price']")
        if not name_el or not price_el:
            return None

        name = (await name_el.inner_text()).strip()
        price_text = (await price_el.inner_text()).strip()
        price = self._parse_price(price_text)
        if price is None:
            return None

        regular_price = None
        regular_el = await item.query_selector("[data-qa='product-regular-price']")
        if regular_el:
            regular_price = self._parse_price(await regular_el.inner_text())

        unit_type, unit_size, unit_size_label = self._parse_unit(name)
        unit_price = self.compute_unit_price(price, unit_type, unit_size)

        return ScrapedPrice(
            chain=self.chain,
            store_name="Lidl",
            product_name=name,
            brand="Lidl",
            category=self._guess_category(name),
            price=price,
            regular_price=regular_price,
            unit_type=unit_type,
            unit_size=unit_size,
            unit_size_label=unit_size_label,
            unit_price=unit_price,
            is_member=False,
            is_promo=regular_price is not None,
            promo_valid_until=None,
            image_url=None,
        )

    @staticmethod
    def _parse_price(text: str) -> float | None:
        text = text.replace("\xa0", " ").replace(",", ".").strip()
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            return round(float(match.group(1)), 2)
        return None

    @staticmethod
    def _parse_unit(name: str) -> tuple[str | None, float | None, str | None]:
        patterns = [
            (r"(\d+(?:[.,]\d+)?)\s*kg", "kg"),
            (r"(\d+(?:[.,]\d+)?)\s*g\b", "g"),
            (r"(\d+(?:[.,]\d+)?)\s*l\b", "l"),
            (r"(\d+(?:[.,]\d+)?)\s*ml", "ml"),
        ]
        for pattern, unit in patterns:
            m = re.search(pattern, name, re.IGNORECASE)
            if m:
                size = float(m.group(1).replace(",", "."))
                label = f"{m.group(1)}{unit}"
                norm_unit = "kg" if unit in ("kg", "g") else "l"
                norm_size = size if unit in ("kg", "l") else size / 1000
                return norm_unit, norm_size, label
        return None, None, None

    @staticmethod
    def _guess_category(name: str) -> str:
        name_lower = name.lower()
        if any(w in name_lower for w in ["мляко", "кисело", "сирене", "масло"]):
            return "dairy"
        if any(w in name_lower for w in ["пиле", "месо", "свинско", "телешко"]):
            return "meat"
        if any(w in name_lower for w in ["олио", "зехтин"]):
            return "oils"
        if any(w in name_lower for w in ["хляб", "питка"]):
            return "bakery"
        if any(w in name_lower for w in ["препарат", "прах", "омекотител"]):
            return "household"
        return "grocery"
