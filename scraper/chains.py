"""
Scraper configuration for Bulgarian retail chains.

Schedule:
  Lidl        Thursday  06:00  (Playwright)
  Kaufland    Wednesday 06:00  (Playwright)
  Billa       Monday    06:00  (BeautifulSoup)
  Fantastico  Wednesday 06:00  (BeautifulSoup)
  T-Market    Thursday  06:00  (BeautifulSoup)
  DM          Monday    06:00  (BeautifulSoup)
  Metro       Tuesday   06:00  (Playwright)
"""

CHAINS = {
    "lidl": {
        "url": "https://www.lidl.bg",
        "engine": "playwright",
        "promo_day": "thursday",
    },
    "kaufland": {
        "url": "https://www.kaufland.bg",
        "engine": "playwright",
        "promo_day": "wednesday",
    },
    "billa": {
        "url": "https://www.billa.bg",
        "engine": "beautifulsoup",
        "promo_day": "monday",
    },
    "fantastico": {
        "url": "https://www.fantastico.bg",
        "engine": "beautifulsoup",
        "promo_day": "wednesday",
    },
    "tmarket": {
        "url": "https://www.t-market.bg",
        "engine": "beautifulsoup",
        "promo_day": "thursday",
    },
    "dm": {
        "url": "https://www.dm-drogerie.bg",
        "engine": "beautifulsoup",
        "promo_day": "monday",
    },
    "metro": {
        "url": "https://www.metro.bg",
        "engine": "playwright",
        "promo_day": "tuesday",
    },
}
