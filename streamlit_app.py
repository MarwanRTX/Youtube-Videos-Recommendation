import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/recommend"
df = pd.read_csv("USvideos.csv")
video_titles = df["title"].drop_duplicates().tolist()

st.title("🎬 YouTube Video Recommendation System")
selected_title = st.selectbox("Choose a video:", video_titles)

if st.button("Recommend"):
    response = requests.get(API_URL, params={"title": selected_title})
    if response.status_code == 200:
        try:
            recommendations = response.json()
            st.subheader("Recommended Videos:")

            if isinstance(recommendations, list):
                for rec in recommendations:
                    if isinstance(rec, dict):
                        video_id = rec.get("video_id", "")
                        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                        st.image(thumbnail_url, width=300)
                        st.markdown(f"**{rec.get('title', 'No Title')}**  \nCategory: {rec.get('category_id', 'Unknown')}")
                    else:
                        st.warning(f"Skipping invalid item: {rec}")
            else:
                st.error("Expected a list from API, but got something else.")
        except Exception as e:
            st.error(f"Failed to parse JSON response: {e}")
    else:
        st.error(f"API Error: {response.status_code}")
