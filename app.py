import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

st.set_page_config(page_title="Gutenberg Top EBooks", layout="wide")

# -------- SCRAPE GUTENBERG --------

url = "https://www.gutenberg.org/browse/scores/top"
base_url = "https://www.gutenberg.org"

@st.cache_data
def fetch_books(url, base_url):
    res = requests.get(url, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    header = soup.find("h2", string="Top 100 EBooks yesterday")
    ol = header.find_next_sibling("ol")

    books = []

    for li in ol.find_all("li"):
        a = li.find("a")

        text = a.text.strip()
        link = base_url + a.get('href')

        parts = text.split(" by ", 1)

        title = parts[0].strip()
        author = parts[1].strip() if len(parts) > 1 else "Unknown"

        books.append({
            "Title": title,
            "Author": author,
            "Link": link
        })

    return pd.DataFrame(books)

df = fetch_books(url, base_url)

# -------- LOAD YOUR EXCEL BOOKS --------

my_books = pd.read_excel("books.xlsx")

df = pd.concat([df, my_books], ignore_index=True)

# -------- APP INTERFACE --------

st.title("📚 City_Prof Educational Foundation Library")

search_option = st.radio(
"Choose how to find books:",
["Search by Title","Search by Author","Browse All Alphabetically"]
)

results = df.copy()

if search_option == "Search by Title":

    title_search = st.text_input("Enter book title")

    if title_search:
        results = df[df["Title"].str.contains(title_search,case=False)]

    else:
        results = pd.DataFrame([])

elif search_option == "Search by Author":

    author_search = st.text_input("Enter author")

    if author_search:
        results = df[df["Author"].str.contains(author_search,case=False)]

    else:
        results = pd.DataFrame([])

else:

    results = df.sort_values(by="Title")

# -------- DISPLAY BOOKS --------

if not results.empty:

    st.write(f"{len(results)} books found")

    for index,row in results.iterrows():

        st.markdown(f"""
        ### {row['Title']}
        Author: {row['Author']}

        [Open Book]({row['Link']})

        ---
        """)

else:

    st.info("No books found")

# -------- DOWNLOAD OPTION --------

@st.cache_data
def convert_df_to_excel(df):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    return output.getvalue()

excel = convert_df_to_excel(results)

st.download_button(
"Download Results",
excel,
"library_books.xlsx"
)