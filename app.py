import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Advanced News Explorer",
    page_icon="📰",
    layout="wide"
)

# ---------------------------
# Constants
# ---------------------------
BASE_URL = "https://newsapi.org/v2"

COUNTRIES = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp",
    "Singapore": "sg"
}

CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology"
]

# ---------------------------
# Load API Key
# ---------------------------
API_KEY = st.secrets["NEWS_API_KEY"]

# ---------------------------
# News Fetch Functions
# ---------------------------
@st.cache_data(ttl=300)
def get_top_headlines(country, category, page_size):
    params = {
        "country": country,
        "category": category,
        "pageSize": page_size,
        "apiKey": API_KEY
    }

    response = requests.get(
        f"{BASE_URL}/top-headlines",
        params=params
    )

    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=300)
def search_news(keyword, page_size, sort_by):
    params = {
        "q": keyword,
        "pageSize": page_size,
        "sortBy": sort_by,
        "language": "en",
        "apiKey": API_KEY
    }

    response = requests.get(
        f"{BASE_URL}/everything",
        params=params
    )

    response.raise_for_status()
    return response.json()

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.title("⚙️ News Filters")

country_name = st.sidebar.selectbox(
    "Select Country",
    list(COUNTRIES.keys())
)

category = st.sidebar.selectbox(
    "Select Category",
    CATEGORIES
)

article_count = st.sidebar.slider(
    "Number of Articles",
    min_value=5,
    max_value=100,
    value=20
)

search_term = st.sidebar.text_input(
    "Keyword Search"
)

sort_by = st.sidebar.selectbox(
    "Sort Results",
    ["publishedAt", "relevancy", "popularity"]
)

fetch_button = st.sidebar.button("Fetch News")

# ---------------------------
# Header
# ---------------------------
st.title("📰 Advanced News Explorer")
st.markdown(
    "Search and explore global news headlines in real-time."
)

# ---------------------------
# Fetch Data
# ---------------------------
if fetch_button:

    try:
        if search_term.strip():

            data = search_news(
                keyword=search_term,
                page_size=article_count,
                sort_by=sort_by
            )

        else:

            data = get_top_headlines(
                country=COUNTRIES[country_name],
                category=category,
                page_size=article_count
            )

        articles = data.get("articles", [])

        if not articles:
            st.warning("No articles found.")
            st.stop()

        st.success(
            f"Found {len(articles)} articles"
        )

        # -----------------------
        # Display Summary Table
        # -----------------------
        df = pd.DataFrame([
            {
                "Title": article["title"],
                "Source": article["source"]["name"],
                "Published": article["publishedAt"]
            }
            for article in articles
        ])

        st.subheader("News Overview")
        st.dataframe(
            df,
            use_container_width=True
        )

        # -----------------------
        # Display Articles
        # -----------------------
        st.subheader("Latest Articles")

        for article in articles:

            with st.container():

                st.markdown(
                    f"### {article.get('title', 'No Title')}"
                )

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(
                        article.get(
                            "description",
                            "No description available."
                        )
                    )

                with col2:
                    st.write(
                        f"*Source:* {article['source']['name']}"
                    )

                    published = article.get(
                        "publishedAt",
                        ""
                    )

                    if published:
                        try:
                            dt = datetime.fromisoformat(
                                published.replace("Z", "+00:00")
                            )
                            st.write(
                                f"*Date:* {dt.strftime('%d %b %Y %H:%M')}"
                            )
                        except:
                            pass

                if article.get("urlToImage"):
                    st.image(
                        article["urlToImage"],
                        use_container_width=True
                    )

                st.markdown(
                    f"[🔗 Read Full Article]({article['url']})"
                )

                st.divider()

    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")

    except Exception as e:
        st.error(f"Unexpected Error: {e}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption(
    "Powered by NewsAPI and Streamlit"
)