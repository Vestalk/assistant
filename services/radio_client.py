from dataclasses import dataclass
from typing import Optional

import logging
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)


class RadioBrowserClient:
    BASE_URL = "https://de1.api.radio-browser.info/json"

    def __init__(self, app_name: str = "MyRadioApp/1.0", timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        # Вказівка User-Agent є вимогою Radio Browser API
        self.session.headers.update({"User-Agent": app_name})

    def get_stations_by_country(self, country: str = "ukraine") -> List[RadioStation]:
        """Отримує список радіостанцій за країною."""
        url = f"{self.BASE_URL}/stations/bycountry/{country.lower()}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            raw_stations = response.json()
            return [RadioStation.from_dict(item) for item in raw_stations]

        except requests.RequestException as e:
            logger.error(f"Помилка при запиті до Radio Browser API: {e}")
            return []

    def get_top_stations(self, country: str = "ukraine", limit: int = 20) -> List[RadioStation]:
        """Отримує найпопулярніші станції країни, відсортовані за голосами."""
        stations = self.get_stations_by_country(country)
        # Фільтрація порожніх назв та сортування за кількістю голосів
        valid_stations = [s for s in stations if s.name and s.url_resolved]
        valid_stations.sort(key=lambda s: s.votes, reverse=True)
        return valid_stations[:limit]

@dataclass
class RadioStation:
    station_id: str
    name: str
    url: str
    url_resolved: str
    homepage: str
    favicon: str
    tags: str
    country: str
    country_code: str
    language: str
    codec: str
    bitrate: int
    votes: int

    @classmethod
    def from_dict(cls, data: dict) -> "RadioStation":
        """Фабричний метод для безпечного парсингу словника з API."""
        return cls(
            station_id=data.get("stationuuid", ""),
            name=data.get("name", "").strip(),
            url=data.get("url", ""),
            url_resolved=data.get("url_resolved", "") or data.get("url", ""),
            homepage=data.get("homepage", ""),
            favicon=data.get("favicon", ""),
            tags=data.get("tags", ""),
            country=data.get("country", ""),
            country_code=data.get("countrycode", ""),
            language=data.get("language", ""),
            codec=data.get("codec", ""),
            bitrate=int(data.get("bitrate", 0)),
            votes=int(data.get("votes", 0)),
        )