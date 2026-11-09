import streamlit as st
import json
import re
from main import CountryAPIClient, CountryComparator

st.set_page_config(page_title="Country Explorer", page_icon="🌍")
st.title("🌍 Country Explorer - Travel, Study & Relocation")

client = CountryAPIClient()
comparator = CountryComparator()

tab1, tab2, tab3 = st.tabs(["🔍 Search Country", "⚖️ Compare Countries", "✅ Before You Travel"])

# TAB 1 - SEARCH
with tab1:
    name = st.text_input("Enter country name (e.g. Nigeria, Canada):")
    if st.button("Search"):
        # Regex validation
        if not re.match(r"^[A-Za-z ]+$", name.strip()):
            st.error("Invalid name. Use letters only.")
        else:
            country, msg = client.get_country(name.strip())
            if country is None:
                st.error(msg)
            else:
                st.image(country.flag, width=200)
                st.subheader(f"{country.name} ({country.code})")
                st.write(f"**Capital:** {country.capital}")
                st.write(f"**Population:** {country.population:,}")
                st.write(f"**Region:** {country.region}")
                st.write(f"**Currency:** {country.currency}")
                st.write(f"**Languages:** {country.languages}")
                st.write(f"**Timezone:** {', '.join(country.timezones)}")
                st.write(f"**Area:** {country.area:,} km²")
                # Save favourite - File handling
                if st.button("⭐ Save to Favourites"):
                    try:
                        with open("favourites.json", "a", encoding="utf-8") as f:
                            json.dump({"name": country.name, "capital": country.capital}, f)
                            f.write("\n")
                        st.success("Saved to favourites.json")
                    except Exception as e:
                        st.error(f"Save failed: {e}")

# TAB 2 - COMPARE
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        name_a = st.text_input("Country A:", value="Nigeria")
    with col2:
        name_b = st.text_input("Country B:", value="Ghana")
    if st.button("Compare"):
        a, msg_a = client.get_country(name_a.strip())
        b, msg_b = client.get_country(name_b.strip())
        if a is None:
            st.error(f"Country A: {msg_a}")
        elif b is None:
            st.error(f"Country B: {msg_b}")
        else:
            comparison, report = comparator.compare(a, b)
            st.table(comparison)
            st.text(report)
            # Timezone difference - simple version
            st.info(f"Timezone A: {a.timezones[0]} | Timezone B: {b.timezones[0]}")
            if st.button("💾 Save Comparison"):
                try:
                    with open("comparison.txt", "w", encoding="utf-8") as f:
                        f.write(report)
                    st.success("Saved to comparison.txt")
                except Exception as e:
                    st.error(f"Save failed: {e}")

# TAB 3 - CHECKLIST
with tab3:
    st.subheader("Before You Travel Checklist")
    st.checkbox("Valid Passport (6+ months)")
    st.checkbox("Visa / Entry Permit")
    st.checkbox("Flight Ticket Booked")
    st.checkbox("Accommodation Booked")
    st.checkbox("Travel Insurance")
    st.checkbox("Currency Exchanged")
    st.checkbox("Vaccinations / Health Check")
    st.checkbox("Copies of Important Documents")
    if st.button("Save Checklist"):
        st.success("Checklist saved! (Ticked items are your guide)")
