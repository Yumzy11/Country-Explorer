import requests
import re

class Country:
    def __init__(self, data):
        self.name = data.get("name", {}).get("common", "Unknown")
        self.capital = ", ".join(data.get("capital", ["N/A"]))
        self.population = data.get("population", 0)
        self.region = data.get("region", "N/A")
        self.area = data.get("area", 0)
        currencies = data.get("currencies", {})
        self.currency = ", ".join([v.get("name", k) for k, v in currencies.items()]) or "N/A"
        self.languages = ", ".join(data.get("languages", {}).values()) or "N/A"
        self.flag = data.get("flags", {}).get("png", "")
        self.timezones = data.get("timezones", ["N/A"])
        self.code = data.get("cca2", "N/A")

class CountryAPIClient:
    def get_country(self, name):
        # Regex: validate country name - only letters and spaces
        if not re.match(r"^[A-Za-z ]+$", name):
            return None, "Invalid country name. Use letters only."
        try:
                        url = f"https://restcountries.com/v3.1/name/{name}"
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                return None, f"Country '{name}' not found."
                        data = response.json()
            if isinstance(data, dict):
                return None, f"Country '{name}' not found."
            if isinstance(data, list):
                data = data[0]
            return Country(data), "Success"
        except requests.exceptions.RequestException as e:
            return None, f"API failed: {e}"
        except Exception as e:
            return None, f"Error: {e}"

class CountryComparator:
    def compare(self, a, b):
        comparison = {
            "Capital": [a.capital, b.capital],
            "Population": [a.population, b.population],
            "Region": [a.region, b.region],
            "Area (km²)": [a.area, b.area],
            "Currency": [a.currency, b.currency],
            "Languages": [a.languages, b.languages],
            "Timezone": [", ".join(a.timezones), ", ".join(b.timezones)],
        }
        bigger = a.name if a.population > b.population else b.name
        report = f"{a.name} vs {b.name}\nBigger Population: {bigger}\nCapital: {a.capital} vs {b.capital}"
        return comparison, report
