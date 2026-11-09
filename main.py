import re
import requests

# Free, no-key source - same data as old REST Countries
DATA_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"

class Country:
    def __init__(self, data):
        self.name = data.get("name", {}).get("common", "N/A")
        self.code = data.get("cca2", "N/A")
        cap = data.get("capital", ["N/A"])
        self.capital = cap[0] if cap else "N/A"

        # --- POPULATION FIX ---
        # Try every possible name for population
        self.population = (
            data.get("population")
            or data.get("pop")
            or data.get("populationCount")
            or data.get("populace")
            or 0
        )
        # If still 0, search inside nested dicts / any key with 'pop'
        if not self.population:
            for k, v in data.items():
                if "pop" in k.lower() and isinstance(v, (int, float)) and v > 0:
                    self.population = v
                    break
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        if "pop" in k2.lower() and isinstance(v2, (int, float)) and v2 > 0:
                            self.population = v2
                            break

        self.region = data.get("region", "N/A")
        curr = data.get("currencies", {})
        if curr:
            first = list(curr.values())[0]
            self.currency = first.get("name", "N/A")
        else:
            self.currency = "N/A"
        langs = data.get("languages", {})
        self.languages = ", ".join(langs.values()) if langs else "N/A"

        # --- TIMEZONE FIX ---
        tz = (
            data.get("timezones")
            or data.get("timeZones")
            or data.get("timezone")
            or data.get("time_zone")
            or data.get("timeZone")
            or None
        )
        if isinstance(tz, str):
            tz = [tz]
        if not tz:
            for k, v in data.items():
                if "time" in k.lower() and isinstance(v, list) and v:
                    tz = v
                    break
                if "time" in k.lower() and isinstance(v, str):
                    tz = [v]
                    break
        self.timezones = tz if tz else ["N/A"]

        self.area = data.get("area", 0)
        # Flag from flagcdn using country code, e.g. ng -> Nigeria flag
        code_lower = self.code.lower() if self.code != "N/A" else "xx"
        self.flag = f"https://flagcdn.com/w320/{code_lower}.png"

class CountryAPIClient:
    def __init__(self):
        self._cache = None

    def _load(self):
        if self._cache is None:
            r = requests.get(DATA_URL, timeout=20)
            r.raise_for_status()
            self._cache = r.json()
        return self._cache

    def _population_from_worldbank(self, code):
        # Last resort: World Bank has real population for every country
        try:
            url = f"https://api.worldbank.org/v2/country/{code}/indicator/SP.POP.TOTL?format=json&per_page=1&date=2022:2024"
            r = requests.get(url, timeout=10)
            j = r.json()
            if len(j) > 1 and j[1] and j[1][0].get("value"):
                return int(j[1][0]["value"])
        except Exception:
            pass
        return 0

    def get_country(self, name):
        if not re.match(r"^[A-Za-z ]+$", name):
            return None, "Invalid country name. Use letters only."
        try:
            all_countries = self._load()
            search = name.strip().lower()
            found = None
            for c in all_countries:
                common = c.get("name", {}).get("common", "").lower()
                official = c.get("name", {}).get("official", "").lower()
                if common == search or official == search:
                    found = c
                    break
            if not found:
                for c in all_countries:
                    common = c.get("name", {}).get("common", "").lower()
                    if search in common:
                        found = c
                        break
            if not found:
                return
