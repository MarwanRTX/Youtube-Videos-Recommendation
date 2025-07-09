from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load data
df = pd.read_csv("USvideos.csv")
df["combined"] = df["title"] + " " + df["category_id"].astype(str) + " " + df["tags"]
df.drop_duplicates(subset="title", inplace=True)
df.reset_index(drop=True, inplace=True)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["combined"])

# Create API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(link):
    if isinstance(link, str):
        if "watch?v=" in link:
            return link.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in link:
            return link.split("youtu.be/")[-1].split("?")[0]
    return ""

@app.get("/recommend")
def recommend(title: str, top_n: int = 5):
    if title not in df["title"].values:
        return []

    i = df[df["title"] == title].index[0]
    if i >= X.shape[0]:
        return []

    cosine_scores = cosine_similarity(X[i], X)
    top_indices = cosine_scores.flatten().argsort()[::-1][1:top_n+1]
    top_df = df.iloc[top_indices][["title", "category_id"]].copy()

    # Extract video_id from video_link (if available)
    if "video_id" in df.columns:
        top_df["video_id"] = df.iloc[top_indices]["video_id"]
    else:
        top_df["video_id"] = ""

    return top_df.to_dict(orient="records")
