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
        self.population = data.get("population", 0)
        self.region = data.get("region", "N/A")
        curr = data.get("currencies", {})
        if curr:
            first = list(curr.values())[0]
            self.currency = first.get("name", "N/A")
        else:
            self.currency = "N/A"
        langs = data.get("languages", {})
        self.languages = ", ".join(langs.values()) if langs else "N/A"
        self.timezones = data.get("timezones", ["N/A"])
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

    def get_country(self, name):
        if not re.match(r"^[A-Za-z ]+$", name):
            return None, "Invalid country name. Use letters only."
        try:
            all_countries = self._load()
            search = name.strip().lower()
            for c in all_countries:
                common = c.get("name", {}).get("common", "").lower()
                official = c.get("name", {}).get("official", "").lower()
                if common == search or official == search:
                    return Country(c), "Success"
            # Partial match if exact not found
            for c in all_countries:
                common = c.get("name", {}).get("common", "").lower()
                if search in common:
                    return Country(c), "Success"
            return None, f"Country '{name}' not found."
        except requests.exceptions.RequestException as e:
            return None, f"API failed: {e}"
        except Exception as e:
            return None, f"Error: {type(e).__name__} - {e}"

class CountryComparator:
    def compare(self, a, b):
        comparison = {
            "Field": ["Capital", "Population", "Region", "Currency", "Area (km2)", "Timezone"],
            a.name: [a.capital, f"{a.population:,}", a.region, a.currency, f"{a.area:,}", a.timezones[0] if a.timezones else "N/A"],
            b.name: [b.capital, f"{b.population:,}", b.region, b.currency, f"{b.area:,}", b.timezones[0] if b.timezones else "N/A"],
        }
        pop_diff = abs(a.population - b.population)
        report = f"Comparison: {a.name} vs {b.name}\nPopulation difference: {pop_diff:,} people\n{a.name} capital: {a.capital} | {b.name} capital: {b.capital}\n"
        return comparison, report
