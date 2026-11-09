import re
import requests

class Country:
    def __init__(self, data):
        try:
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
            flags = data.get("flags", {})
            self.flag = flags.get("png", "")
        except Exception as e:
            raise Exception(f"Country parse failed: {e} | data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")

class CountryAPIClient:
    def get_country(self, name):
        if not re.match(r"^[A-Za-z ]+$", name):
            return None, "Invalid country name. Use letters only."
        try:
            url = f"https://restcountries.com/v3.1/name/{name}?fields=name,cca2,capital,population,region,currencies,languages,timezones,area,flags"
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return None, f"Country '{name}' not found. Status: {response.status_code}"
            data = response.json()
            if isinstance(data, dict):
                return None, f"API returned: {data}"
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            else:
                return None, "No data returned from API"
            return Country(data), "Success"
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
