import streamlit as st
from bs4 import BeautifulSoup
import requests
import random
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def return_random_quote(url):
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
    quote_elements = soup.select('div[class="quote mediumText"]')
    
    quotes = []
    for quote_element in quote_elements:
        try:
            quote_text = quote_element.decode_contents().split('<br')[0].strip()
            quotes.append(quote_text)
        except Exception as e:
            continue
    
    if quotes:
        random_quote = random.choice(quotes)
        return random_quote
    else:
        return "No quotes found."

def append_to_database(selected_value, current_time):
    conn = sqlite3.connect('searchesDB.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS searches (
                      search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      keyword TEXT,
                      timestamp TEXT)''')
    cursor.execute("INSERT INTO searches (keyword, timestamp) VALUES (?, ?)", (selected_value, current_time))
    conn.commit()
    conn.close()

# Streamlit app
st.set_page_config(layout="wide")
st.header('Daily Quotes By beridzeg45 😉')
st.text('')

input_value = st.text_input('Enter a keyword to search for quotes (E.g. Friedrich Nietzsche, life, fight club, etc.):')

if st.button('Show Quote') and input_value:
    input_value_as_list = '+'.join([i.strip() for i in input_value.split(' ')])
    url = f'https://www.goodreads.com/quotes/search?commit=Search&page={random.choice(range(1, 2))}&q={input_value_as_list}'

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    append_to_database(input_value, current_time)
    
    random_quote = return_random_quote(url)
    st.markdown(f"<h1 style='font-size:24px;'>{random_quote}</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("# About me:")
intro_text = """
Hi!👋 \n
I'm Giorgi, and this is my another python project. This website recommends quotes based on the keyword.\n
It involves following python libraries in action: requests, bs4, sqlite3.\n
If you're curious about the code and want to explore it, feel free to visit my [Github account!](https://github.com/beridzeg45)\n
"""
st.sidebar.markdown(intro_text)

# Read from database and display statistics
conn = sqlite3.connect('searchesDB.db')
df = pd.read_sql_query("SELECT * FROM searches", conn)
conn.close()

df['timestamp'] = pd.to_datetime(df['timestamp'])
top_10 = df.groupby('keyword')['search_id'].count().sort_values(ascending=False).reset_index().rename(columns={'keyword': 'Keyword', 'search_id': 'Search Count'}).head(5)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.subheader('5 Most Frequently Searched Keywords')
st.sidebar.dataframe(top_10, use_container_width=True)

fig, ax = plt.subplots(figsize=(5, 4))
fig_data = df.groupby(df['timestamp'].dt.to_period('D'))['search_id'].count()
fig_data.plot.line(marker='o', xlabel='Date', ylabel='Search Count', title='Number Of Searches By Date', ax=ax)
ax.set_xlabel(None)
st.sidebar.pyplot(fig)

# Database download button
with open("searchesDB.db", "rb") as file:
    st.sidebar.download_button(
        label="Download Database",
        data=file,
        file_name="searchesDB.db",
        mime="application/octet-stream"
    )
