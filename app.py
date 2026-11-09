import re
import requests
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"

# --- Fallback data in case any API fails ---
FALLBACK_POP = {
    "NG": 223804632, "GH": 34121985, "US": 340110988, "GB": 67736800,
    "FR": 68172197, "DE": 84355242, "IN": 1450935791, "CN": 1410710000,
    "ZA": 60414778, "KE": 55100586, "EG": 112716598, "CA": 38929902,
}
FALLBACK_TZ = {
    "NG": "UTC+01:00", "GH": "UTC+00:00", "US": "UTC-05:00", "GB": "UTC+00:00",
    "FR": "UTC+01:00", "DE": "UTC+01:00", "IN": "UTC+05:30", "CN": "UTC+08:00",
    "ZA": "UTC+02:00", "KE": "UTC+03:00", "EG": "UTC+02:00", "CA": "UTC-05:00",
}

@st.cache_data
def load_countries():
    r = requests.get(DATA_URL, timeout=20)
    r.raise_for_status()
    return r.json()

def worldbank_pop(code):
    try:
        url = f"https://api.worldbank.org/v2/country/{code}/indicator/SP.POP.TOTL?format=json&per_page=1&date=2022:2024"
        j = requests.get(url, timeout=10).json()
        if len(j) > 1 and j[1] and j[1][0].get("value"):
            return int(j[1][0]["value"])
    except Exception:
        pass
    return 0

def get_country(name):
    if not re.match(r"^[A-Za-z ]+$", name):
        return None, "Invalid country name. Use letters only."
    try:
        all_c = load_countries()
        search = name.strip().lower()
        found = None
        for c in all_c:
            if c.get("name", {}).get("common", "").lower() == search:
                found = c; break
        if not found:
            for c in all_c:
                if search in c.get("name", {}).get("common", "").lower():
                    found = c; break
        if not found:
            return None, f"Country '{name}' not found."
        # Build clean dict
        code = found.get("cca2", "N/A")
        pop = found.get("population", 0) or 0
        if not pop:
            pop = worldbank_pop(code) or FALLBACK_POP.get(code, 0)
        tz = found.get("timezones") or []
        if not tz:
            tz = [FALLBACK_TZ.get(code, "N/A")]
        curr = found.get("currencies", {})
        currency = list(curr.values())[0].get("name", "N/A") if curr else "N/A"
        langs = found.get("languages", {})
        languages = ", ".join(langs.values()) if langs else "N/A"
        cap = found.get("capital", ["N/A"])
        data = {
            "name": found.get("name", {}).get("common", "N/A"),
            "code": code,
            "capital": cap[0] if cap else "N/A",
            "population": pop,
            "region": found.get("region", "N/A"),
            "currency": currency,
            "languages": languages,
            "timezones": tz,
            "area": found.get("area", 0),
            "flag": f"https://flagcdn.com/w320/{code.lower()}.png" if code != "N/A" else "",
        }
        return data, "Success"
    except Exception as e:
        return None, f"Error: {e}"

# --- UI ---
st.title("🌍 Country Explorer")

tab1, tab2 = st.tabs(["Search Country", "Compare Countries"])

with tab1:
    name = st.text_input("Enter country name", placeholder="e.g. Nigeria")
    if st.button("Search"):
        if name:
            country, msg = get_country(name)
            if country:
                if country["flag"]:
                    st.image(country["flag"], width=200)
                st.header(f"{country['name']} ({country['code']})")
                st.write(f"**Capital:** {country['capital']}")
                st.write(f"**Population:** {country['population']:,}")
                st.write(f"**Region:** {country['region']}")
                st.write(f"**Currency:** {country['currency']}")
                st.write(f"**Languages:** {country['languages']}")
                st.write(f"**Timezone:** {country['timezones'][0] if country['timezones'] else 'N/A'}")
                st.write(f"**Area:** {country['area']:,} km²")
                if st.button("⭐ Save to Favourites"):
                    if "favs" not in st.session_state:
                        st.session_state.favs = []
                    if country['name'] not in st.session_state.favs:
                        st.session_state.favs.append(country['name'])
                    st.success(f"Saved {country['name']} to Favourites!")
            else:
                st.error(msg)
        else:
            st.warning("Please enter a country name.")

    if "favs" in st.session_state and st.session_state.favs:
        st.subheader("⭐ Favourites")
        for f in st.session_state.favs:
            st.write(f"- {f}")

with tab2:
    st.subheader("Compare Two Countries")
    c1_name = st.text_input("First country", key="c1")
    c2_name = st.text_input("Second country", key="c2")
    if st.button("Compare"):
        c1, m1 = get_country(c1_name)
        c2, m2 = get_country(c2_name)
        if c1 and c2:
            st.table({
                "Field": ["Capital", "Population", "Region", "Currency", "Area (km2)", "Timezone"],
                c1['name']: [c1['capital'], f"{c1['population']:,}", c1['region'], c1['currency'], f"{c1['area']:,}", c1['timezones'][0]],
                c2['name']: [c2['capital'], f"{c2['population']:,}", c2['region'], c2['currency'], f"{c2['area']:,}", c2['timezones'][0]],
            })
            diff = abs(c1['population'] - c2['population'])
            st.write(f"**Population difference:** {diff:,} people")
            st.write(f"{c1['name']} capital: {c1['capital']} | {c2['name']} capital: {c2['capital']}")
        else:
            st.error(m1 if not c1 else m2)
