import streamlit as st
import urllib.request
import urllib.parse
import json
import time
import pandas as pd

st.set_page_config(page_title="Lead Finder", layout="wide")

st.title("🗺️ Local Business Lead Finder")
st.markdown("Powered by Google Places API — gets name, phone, website, rating for every business")

# Sidebar for settings
with st.sidebar:
    st.header("🔑 Google API Key")
    api_key = st.text_input("Paste your Google Places API key", type="password")
    st.caption("Stored only in session memory — never saved or sent anywhere except Google's API.")

# Main columns
col1, col2, col3 = st.columns(3)

with col1:
    city = st.text_input("Area (e.g., Koramangala, Bangalore)", value="Koramangala, Bangalore")

with col2:
    category = st.selectbox("Category", options=[
        ("All Shops", "store"),
        ("Restaurants / Cafes", "restaurant"),
        ("Salons / Parlours", "hair_care"),
        ("Pharmacies", "pharmacy"),
        ("Clothing Stores", "clothing_store"),
        ("Electronics", "electronics_store"),
        ("Bakeries", "bakery"),
        ("Gyms / Fitness", "gym"),
    ], format_func=lambda x: x[0])

with col3:
    search_btn = st.button("🔍 Find Leads", use_container_width=True, type="primary")

# Session state
if "all_data" not in st.session_state:
    st.session_state.all_data = []

if "active_filter" not in st.session_state:
    st.session_state.active_filter = "all"

# API functions
def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def geocode(address, key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={key}"
    return fetch_json(url)

def nearbysearch(lat, lng, radius, type_param, key, pagetoken=None):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type={type_param}&key={key}"
    if pagetoken:
        url += f"&pagetoken={pagetoken}"
    return fetch_json(url)

def place_details(place_id, key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,website,formatted_address,rating,url&key={key}"
    return fetch_json(url)

# Search logic
if search_btn:
    if not api_key:
        st.error("❌ Please enter your Google API key")
    elif not city:
        st.error("❌ Please enter an area")
    else:
        st.session_state.all_data = []
        
        with st.spinner("⏳ Step 1/3: Finding location..."):
            geo = geocode(city, api_key)
            if not geo or geo.get("status") != "OK":
                st.error(f"❌ Location not found. Check your area name.")
            else:
                loc = geo["results"][0]["geometry"]["location"]
                
                with st.spinner("⏳ Step 2/3: Searching businesses..."):
                    places = []
                    pagetoken = None
                    page = 0

                    while True:
                        data = nearbysearch(loc["lat"], loc["lng"], 2500, category[1], api_key, pagetoken)
                        if data and data.get("status") == "REQUEST_DENIED":
                            st.error(f"❌ API key rejected: {data.get('error_message', '')}")
                            break
                        if data:
                            places.extend(data.get("results", []))
                            pagetoken = data.get("next_page_token")
                            if not pagetoken:
                                break
                            time.sleep(2)
                        else:
                            break
                        page += 1
                
                if not places:
                    st.error("❌ No businesses found in this area. Try a different locality.")
                else:
                    with st.spinner(f"⏳ Step 3/3: Fetching details for {len(places)} businesses..."):
                        for i, p in enumerate(places):
                            st.write(f"   Fetching {i+1}/{len(places)}...")
                            details = place_details(p.get("place_id"), api_key)
                            d = details.get("result", {}) if details else {}
                            
                            st.session_state.all_data.append({
                                "name": d.get("name") or p.get("name"),
                                "phone": d.get("formatted_phone_number"),
                                "website": d.get("website"),
                                "address": d.get("formatted_address"),
                                "rating": d.get("rating") or p.get("rating"),
                                "mapsUrl": d.get("url") or f"https://www.google.com/maps/place/?q=place_id:{p.get('place_id')}"
                            })

# Display results
if st.session_state.all_data:
    all_data = st.session_state.all_data
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Businesses Found", len(all_data))
    with col2:
        no_website = len([b for b in all_data if not b["website"]])
        st.metric("No Website (Hot Leads)", no_website)
    with col3:
        has_phone = len([b for b in all_data if b["phone"]])
        st.metric("Have Phone", has_phone)
    with col4:
        rated = [b for b in all_data if b["rating"]]
        avg_rating = sum(b["rating"] for b in rated) / len(rated) if rated else 0
        st.metric("Avg Rating", f"{avg_rating:.1f}" if rated else "—")
    
    # Filters
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("All", use_container_width=True, key="filter_all"):
            st.session_state.active_filter = "all"
    with col2:
        if st.button("No Website", use_container_width=True, key="filter_no_web"):
            st.session_state.active_filter = "no-website"
    with col3:
        if st.button("Has Phone", use_container_width=True, key="filter_phone"):
            st.session_state.active_filter = "has-phone"
    with col4:
        if st.button("📞 + No Website", use_container_width=True, key="filter_both"):
            st.session_state.active_filter = "both"
    with col5:
        if st.button("⬇️ Download CSV", use_container_width=True, key="export_csv"):
            rows = [["Name", "Address", "Phone", "Website", "Rating", "Google Maps"]]
            for b in all_data:
                rows.append([
                    b["name"],
                    b["address"] or "",
                    b["phone"] or "",
                    b["website"] or "",
                    b["rating"] or "",
                    b["mapsUrl"] or ""
                ])
            df = pd.DataFrame(rows[1:], columns=rows[0])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="leads.csv",
                mime="text/csv"
            )
    
    # Filter data
    filtered_data = all_data
    if st.session_state.active_filter == "no-website":
        filtered_data = [b for b in all_data if not b["website"]]
    elif st.session_state.active_filter == "has-phone":
        filtered_data = [b for b in all_data if b["phone"]]
    elif st.session_state.active_filter == "both":
        filtered_data = [b for b in all_data if b["phone"] and not b["website"]]
    
    # Display results
    if filtered_data:
        st.write(f"**Showing {len(filtered_data)} businesses**")
        for b in filtered_data:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write("🏪")
                with col2:
                    st.subheader(b["name"], divider=False)
                    if b["address"]:
                        st.caption(f"📍 {b['address']}")
                    
                    cols = st.columns(4, gap="small")
                    if b["website"]:
                        cols[0].button("✅ Has Website", key=f"web_{b['name']}", disabled=True)
                    else:
                        cols[0].button("🔴 No Website", key=f"noweb_{b['name']}", disabled=True)
                    
                    if b["phone"]:
                        cols[1].button(f"📞 {b['phone']}", key=f"phone_{b['name']}", disabled=True)
                    else:
                        cols[1].button("No Phone", key=f"nophone_{b['name']}", disabled=True)
                    
                    if b["rating"]:
                        cols[2].button(f"⭐ {b['rating']}", key=f"rating_{b['name']}", disabled=True)
                    
                    if b["mapsUrl"]:
                        cols[3].link_button("🗺️ Maps", b["mapsUrl"])
    else:
        st.info("No results for this filter")
else:
    st.info("👆 Enter your area, paste your API key, and click Find Leads")
