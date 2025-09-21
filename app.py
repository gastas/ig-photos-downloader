import streamlit as st
import requests
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Instagram Scraper", layout="wide")
st.title("📸 Instagram Scraper via Apify")

st.markdown(
    """
    This tool fetches the latest photos from Instagram profiles using  
    [Apify Instagram Scraper](https://apify.com/apify/instagram-scraper).  
    ⚠️ You need an **Apify API Token** (get it from your [Apify Console](https://console.apify.com/)).
    """
)

apify_token = st.text_input("🔑 Enter your Apify API Token", type="password")
usernames = st.text_area("👥 Enter Instagram usernames (one per line)", "instagram\nnatgeo")

results = []

if st.button("Fetch photos"):
    if not apify_token or not usernames.strip():
        st.error("❌ You must provide an API Token and at least one username")
    else:
        usernames_list = [u.strip().lstrip("@") for u in usernames.split("\n") if u.strip()]

        for username in usernames_list:
            st.subheader(f"@{username}")

            url = "https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items"
            params = {"token": apify_token}
            payload = {
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsLimit": 4,  # always fetch 4 latest photos
            }

            try:
                response = requests.post(url, params=params, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()

                if not data:
                    st.warning("⚠️ No posts found. The account might be private or empty.")
                    continue

                photo_urls = []
                for item in data[:4]:
                    if "displayUrl" in item:
                        photo_urls.append(item["displayUrl"])
                        st.image(item["displayUrl"], caption=item.get("text", ""), use_container_width=True)
                        st.markdown(f"[Open post in Instagram]({item['url']})")

                # store results in table
                row = {"username": username}
                for i in range(4):
                    row[f"photo_{i+1}"] = photo_urls[i] if i < len(photo_urls) else ""
                results.append(row)

            except Exception as e:
                st.error(f"Error: {e}")

# CSV export
if results:
    df = pd.DataFrame(results)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.success("✅ Data collected! You can download the CSV file below.")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_buffer.getvalue(),
        file_name="instagram_photos.csv",
        mime="text/csv",
    )
    st.dataframe(df)
