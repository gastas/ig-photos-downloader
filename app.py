import streamlit as st
import requests
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Instagram Scraper", layout="wide")
st.title("📸 Instagram Scraper via Apify")

st.markdown(
    """
    This tool fetches the **latest 5 posts** from Instagram profiles using  
    [Apify Instagram Scraper](https://apify.com/apify/instagram-scraper).  
    ⚠️ You need an **Apify API Token** (get it from your [Apify Console](https://console.apify.com/)).
    """
)

apify_token = st.text_input("🔑 Enter your Apify API Token", type="password")
usernames = st.text_area("👥 Enter Instagram usernames (one per line)", "instagram\nnatgeo")

# temporary storage for selections
if "results" not in st.session_state:
    st.session_state.results = []

if st.button("Fetch posts"):
    if not apify_token or not usernames.strip():
        st.error("❌ You must provide an API Token and at least one username")
    else:
        usernames_list = [u.strip().lstrip("@") for u in usernames.split("\n") if u.strip()]
        st.session_state.results = []  # reset

        for username in usernames_list:
            st.subheader(f"@{username}")

            url = "https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items"
            params = {"token": apify_token}
            payload = {
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsLimit": 5,
            }

            try:
                response = requests.post(url, params=params, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()

                if not data:
                    st.warning("⚠️ No posts found. The account might be private or empty.")
                    continue

                photo_urls = []
                for idx, item in enumerate(data[:5], start=1):
                    if "displayUrl" in item:
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            selected = st.checkbox(
                                f"Select post {idx}",
                                key=f"{username}_{idx}"
                            )
                        with col2:
                            st.image(item["displayUrl"], caption=item.get("text", ""), use_container_width=True)
                            st.markdown(f"[Open in Instagram]({item['url']})")

                        if selected:
                            photo_urls.append(item["displayUrl"])

                # store results for export
                row = {"username": username}
                for i in range(5):
                    row[f"photo_{i+1}"] = photo_urls[i] if i < len(photo_urls) else ""
                st.session_state.results.append(row)

            except Exception as e:
                st.error(f"Error: {e}")

# CSV export
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.success("✅ Your selection is ready! Download below.")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_buffer.getvalue(),
        file_name="instagram_photos.csv",
        mime="text/csv",
    )
    st.dataframe(df)
