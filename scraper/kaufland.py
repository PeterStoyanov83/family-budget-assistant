"""Kaufland Bulgaria scraper — runs every Wednesday 06:00."""
import re

from scraper.base import BaseScraper, ScrapedPrice
from scraper.lidl import LidlScraper  # reuse _parse_price / _parse_unit / _guess_category


class KauflandScraper(BaseScraper):
    chain = "kaufland"
    base_url = "https://www.kaufland.bg"

    OFFERS_URL = "https://www.kaufland.bg/aktualni-predlozheniya.html"

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
                self.logger.error("Kaufland offers scrape failed: %s", exc)

            await browser.close()

        self.logger.info("Kaufland: scraped %d prices", len(results))
        return results

    async def _scrape_offers(self, page) -> list[ScrapedPrice]:
        await page.goto(self.OFFERS_URL, wait_until="networkidle", timeout=30_000)
        await page.wait_for_selector(".m-product-tile", timeout=15_000)

        items = await page.query_selector_all(".m-product-tile")
        results = []
        for item in items:
            try:
                r = await self._parse_offer_item(item)
                if r:
                    results.append(r)
            except Exception as exc:
                self.logger.debug("Failed to parse Kaufland item: %s", exc)
        return results

    async def _parse_offer_item(self, item) -> ScrapedPrice | None:
        name_el = await item.query_selector(".m-product-tile__title")
        price_el = await item.query_selector(".m-price__price")
        if not name_el or not price_el:
            return None

        name = (await name_el.inner_text()).strip()
        price_text = (await price_el.inner_text()).strip()
        price = LidlScraper._parse_price(price_text)
        if price is None:
            return None

        regular_price = None
        regular_el = await item.query_selector(".m-price__old")
        if regular_el:
            regular_price = LidlScraper._parse_price(await regular_el.inner_text())

        # Kaufland member card pricing
        member_el = await item.query_selector(".m-price__member")
        is_member = member_el is not None
        if is_member and member_el:
            member_price = LidlScraper._parse_price(await member_el.inner_text())
            if member_price:
                regular_price = price
                price = member_price

        unit_type, unit_size, unit_size_label = LidlScraper._parse_unit(name)
        unit_price = self.compute_unit_price(price, unit_type, unit_size)

        return ScrapedPrice(
            chain=self.chain,
            store_name="Kaufland",
            product_name=name,
            brand=None,
            category=LidlScraper._guess_category(name),
            price=price,
            regular_price=regular_price,
            unit_type=unit_type,
            unit_size=unit_size,
            unit_size_label=unit_size_label,
            unit_price=unit_price,
            is_member=is_member,
            is_promo=regular_price is not None,
            promo_valid_until=None,
            image_url=None,
        )
