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

selected_posts = {}  # store user selections
results = []

if st.button("Fetch last 5 posts"):
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
                "resultsLimit": 5,  # always fetch last 5 posts
            }

            try:
                response = requests.post(url, params=params, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()

                if not data:
                    st.warning("⚠️ No posts found. The account might be private or empty.")
                    continue

                selected_posts[username] = []

                for i, item in enumerate(data[:5], start=1):
                    image_url = item.get("displayUrl", "")
                    permalink = item.get("url", "")
                    caption = item.get("text", "")

                    if image_url and "images.apifyusercontent.com" in image_url:
                        st.image(image_url, caption=f"Post {i}: {caption}", use_container_width=True)
                        if st.checkbox(f"Add Post {i} to CSV ({username})", key=f"{username}_{i}"):
                            selected_posts[username].append(image_url)
                            st.markdown(f"[Open in Instagram]({permalink})")

            except Exception as e:
                st.error(f"Error: {e}")

# CSV export
if selected_posts:
    for username, photos in selected_posts.items():
        row = {"username": username}
        for i, url in enumerate(photos, start=1):
            row[f"photo_{i}"] = url
        results.append(row)

if results:
    df = pd.DataFrame(results)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.success("✅ Data ready! Download CSV below.")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_buffer.getvalue(),
        file_name="instagram_photos.csv",
        mime="text/csv",
    )
    st.dataframe(df)
